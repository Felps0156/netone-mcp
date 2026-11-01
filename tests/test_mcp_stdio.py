"""Use the generic SDK client over actual stdio with synthetic ERP data."""

from datetime import timedelta
import json
from pathlib import Path
import sys
import tempfile
import unittest

import anyio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from test_mcp_tools import EXPECTED_TOOLS


class MCPStdioTests(unittest.IsolatedAsyncioTestCase):
    async def test_generic_stdio_directed_price_and_stock(self):
        fixture = Path(__file__).with_name('mcp_stdio_fixture.py').resolve()
        with tempfile.TemporaryFile(mode='w+', encoding='utf-8') as stderr:
            with anyio.fail_after(20):
                async with stdio_client(StdioServerParameters(
                    command=sys.executable,
                    args=['-B', str(fixture), '--directed-queries'],
                ), errlog=stderr) as (reader, writer):
                    async with ClientSession(reader, writer) as session:
                        await session.initialize()
                        for name, arguments in (
                            ('check_inventory', {'reduced_id': '42'}),
                            ('get_product_price', {'product_id': '7'}),
                        ):
                            reply = await session.call_tool(name, arguments)
                            self.assertFalse(reply.isError)
                            data = reply.structuredContent
                            self.assertEqual(data['status'], 'found')
                            self.assertEqual(data['lookup_strategy'],
                                             'remote_id_filter')
                            self.assertEqual(data['pages_fetched'], 1)
                            self.assertEqual(data['items'][0]['reduced_id'],
                                             '42')
                            field = ('quantity' if name == 'check_inventory'
                                     else 'price')
                            self.assertEqual(data['items'][0][field], '0')
                            self.assertEqual(json.loads(reply.content[0].text),
                                             data)
            stderr.seek(0)
            diagnostic = stderr.read()
        summary = next(line.removeprefix('offline_fixture ')
                       for line in diagnostic.splitlines()
                       if line.startswith('offline_fixture '))
        self.assertEqual(json.loads(summary), {
            'requests': 2, 'responses_closed': 2, 'clients_closed': 1,
        })
        self.assertNotIn('Traceback', diagnostic)

    async def test_generic_stdio_continues_catalog_and_inventory(self):
        fixture = Path(__file__).with_name('mcp_stdio_fixture.py').resolve()
        with tempfile.TemporaryFile(mode='w+', encoding='utf-8') as stderr:
            with anyio.fail_after(20):
                async with stdio_client(StdioServerParameters(
                    command=sys.executable,
                    args=['-B', str(fixture), '--continuation'],
                ), errlog=stderr) as (reader, writer):
                    async with ClientSession(reader, writer) as session:
                        await session.initialize()
                        self.assertEqual({t.name for t in (
                            await session.list_tools()).tools}, EXPECTED_TOOLS)
                        for name in ('list_products', 'list_inventory'):
                            reply = await session.call_tool(name, {
                                'start_page': 2, 'max_results': 1,
                                'page_size': 1, 'max_pages': 1,
                            })
                            self.assertFalse(reply.isError)
                            data = reply.structuredContent
                            self.assertEqual(data['items'][0]['reduced_id'],
                                             '001')
                            self.assertEqual(data['last_page'], 2)
                            self.assertTrue(data['endpoint_exhausted'])
                            self.assertFalse(data['complete_dataset'])
                            self.assertEqual(json.loads(reply.content[0].text),
                                             data)
            stderr.seek(0)
            diagnostic = stderr.read()
        summary = next(line.removeprefix('offline_fixture ')
                       for line in diagnostic.splitlines()
                       if line.startswith('offline_fixture '))
        self.assertEqual(json.loads(summary), {
            'requests': 2, 'responses_closed': 2, 'clients_closed': 1,
        })
        self.assertNotIn('Traceback', diagnostic)

    async def test_generic_stdio_client_discovers_executes_and_closes(self):
        await self.exercise()

    async def test_generic_stdio_default_search_reaches_second_page(self):
        await self.exercise(search=True)

    async def exercise(self, search=False):
        fixture = Path(__file__).with_name('mcp_stdio_fixture.py').resolve()
        # The runtime's TMPDIR is managed Hermes scratch, not system temp.
        with tempfile.TemporaryFile(mode='w+', encoding='utf-8') as stderr:
            with anyio.fail_after(20):
                async with stdio_client(StdioServerParameters(
                    command=sys.executable,
                    args=['-B', str(fixture)] + (['--search-pages'] if search else []),
                ), errlog=stderr) as (reader, writer):
                    async with ClientSession(
                        reader, writer,
                        read_timeout_seconds=timedelta(seconds=5),
                    ) as session:
                        await session.initialize()
                        listed = await session.list_tools()
                        self.assertEqual({tool.name for tool in listed.tools},
                                         EXPECTED_TOOLS)
                        for arguments in (
                            {'max_results': True},
                            {'endpoint': 'PRIVATE'}, {'token': 'PRIVATE'},
                        ):
                            rejected = await session.call_tool(
                                'list_products', arguments,
                            )
                            self.assertTrue(rejected.isError)
                            self.assertNotIn('PRIVATE',
                                             rejected.model_dump_json())
                        reply = await session.call_tool(
                            'search_products' if search else 'list_products',
                            {'query': 'Synthetic'} if search else {'max_results': 1},
                        )
                        self.assertFalse(reply.isError)
                        data = reply.structuredContent
                        self.assertEqual(data['status'], 'found')
                        self.assertEqual(data['returned_count'], 1)
                        item = data['items'][0]
                        self.assertEqual(item['product_mask'], '0007')
                        self.assertEqual(item['price'],
                                         '123456789012345678.2300')
                        self.assertEqual(item['quantity'], '0')
                        self.assertIsNone(item['ean'])
                        self.assertEqual(json.loads(reply.content[0].text),
                                         data)
                        if search:
                            self.assertEqual(data['rows_received'], 51)
                            self.assertEqual(data['pages_fetched'], 2)
                            self.assertEqual(data['inspection_limit'], 100)
                            self.assertTrue(data['collection_complete'])
            stderr.seek(0)
            diagnostic = stderr.read()
        summary = next(line.removeprefix('offline_fixture ')
                       for line in diagnostic.splitlines()
                       if line.startswith('offline_fixture '))
        self.assertEqual(json.loads(summary), {
            'requests': 2 if search else 1,
            'responses_closed': 2 if search else 1, 'clients_closed': 1,
        })
        for sentinel in ('PRIVATE', 'example.invalid', 'Traceback'):
            self.assertNotIn(sentinel, diagnostic)


if __name__ == '__main__':
    unittest.main()
