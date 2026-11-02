"""Explicit bounded search options, including the generic MCP boundary."""

import json
import unittest

from test_client import response, row
from test_tools import ProductToolsTestCase
import test_mcp_tools
import tools


class SearchOptionsTests(ProductToolsTestCase):
    async def test_explicit_pages_and_related_terms_use_one_pass(self):
        def pages(req):
            page = json.loads(req.content)['page']
            return response([row(str(page), descricao=(
                'Other' if page == 1 else 'Punho LS2'))], page, 2,
                totalElements=2)
        self.handler = pages
        result = await tools.search_products(
            self.client, 'manopla LS2', max_results=2, page_size=1,
            max_pages=2, mode='related', suggested_terms=['guidão'],
        )
        self.assertEqual(result['items'][0]['reduced_id'], '2')
        self.assertEqual(result['matches'][0]['match_type'], 'reviewed')
        self.assertTrue(result['collection_complete'])
        self.assertEqual(self.bodies(), [
            {'page': 1, 'limit': 1}, {'page': 2, 'limit': 1},
        ])

    async def test_suffix_and_page_cut_are_explicitly_partial(self):
        self.handler = lambda req: response([row('2', descricao='Match')],
                                            2, 3, totalElements=3)
        result = await tools.search_products(
            self.client, 'match', max_results=5, page_size=1,
            start_page=2, max_pages=1,
        )
        self.assertTrue(result['partial'])
        self.assertFalse(result['collection_complete'])
        self.assertEqual(result['next_page'], 3)
        self.assertEqual(len(self.requests), 1)

    async def test_search_options_validate_before_collection(self):
        for options in (
            {'max_pages': True}, {'page_size': 101}, {'start_page': 0},
            {'mode': 'semantic'}, {'suggested_terms': ['x']},
            {'mode': 'related', 'required_terms': ['\nPRIVATE']},
        ):
            with self.subTest(options=options):
                with self.assertRaises(tools.ToolInputError):
                    await tools.search_products(self.client, 'match', **options)
        self.assertEqual(self.requests, [])


class SearchOptionsMCPTests(unittest.IsolatedAsyncioTestCase):
    session = test_mcp_tools.MCPToolsTests.session

    async def test_related_mode_discovered_and_callable_with_strict_options(self):
        async with self.session(lambda req: response([
            row('1', descricao='Punho LS2')], totalElements=1)) as (
                session, requests, _):
            listed = await session.list_tools()
            schema = next(t.inputSchema for t in listed.tools
                          if t.name == 'search_products')
            self.assertIn('mode', schema['properties'])
            reply = await session.call_tool('search_products', {
                'query': 'manopla LS2', 'mode': 'related', 'max_pages': 2,
                'page_size': 1, 'max_results': 2,
            })
            self.assertFalse(reply.isError)
            self.assertEqual(reply.structuredContent['returned_count'], 1)
            self.assertEqual(json.loads(reply.content[0].text),
                             reply.structuredContent)
            self.assertEqual(len(requests), 1)
            for options in ({'max_pages': '2'}, {'start_page': True},
                            {'mode': 'related', 'suggested_terms': [2]}):
                bad = await session.call_tool('search_products',
                                              {'query': 'x', **options})
                self.assertTrue(bad.isError)
            self.assertEqual(len(requests), 1)
