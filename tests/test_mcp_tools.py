"""Exercise the public MCP boundary over real application/mock HTTP paths."""

from contextlib import asynccontextmanager
from datetime import timedelta
import io
import json
import logging
from pathlib import Path
import unittest
from unittest.mock import patch

import anyio
import httpx
from mcp import types
from mcp.shared.memory import create_connected_server_and_client_session
from pydantic import SecretStr

from config import Settings
import server
from test_client import Stream, response, row


EXPECTED_TOOLS = {
    'search_products', 'search_product_by_code', 'get_product_details',
    'search_product_by_ean', 'get_product_price', 'check_inventory',
    'list_products',
}


class MCPToolsTests(unittest.IsolatedAsyncioTestCase):
    @asynccontextmanager
    async def session(self, handler=None, max_results=100):
        requests, closed, streams = [], [], []
        captured = io.StringIO()
        root = logging.getLogger()
        saved = root.handlers[:], root.level

        def send(request):
            requests.append(request)
            result = handler(request) if handler else httpx.Response(
                200, stream=Stream(
                    b'{"result":[{"idProduto":7,"idReduzido":"001",'
                    b'"mascara":"0007","ean":"00123","descricao":"item",'
                    b'"valor":1.2300}],"page":1,"totalPages":1,'
                    b'"totalElements":1}'
                ),
            )
            streams.append(result.stream)
            return result

        class Transport(httpx.MockTransport):
            async def aclose(self):
                await anyio.sleep(0)
                await super().aclose()
                closed.append(True)

        original_read = Path.read_text

        def protected_read(path, *args, **kwargs):
            if path.name == '.env':
                raise AssertionError('Real environment access forbidden')
            return original_read(path, *args, **kwargs)

        try:
            with patch('client.httpx.AsyncHTTPTransport',
                       return_value=Transport(send)), patch(
                'sys.stderr', captured,
            ), patch.object(Path, 'read_text', protected_read):
                app = server.create_server(Settings(
                    base_url='https://example.invalid',
                    token=SecretStr('SYNTHETIC_PRIVATE_TOKEN'),
                    max_results=max_results, log_level='DEBUG',
                ))
                with anyio.fail_after(10):
                    async with create_connected_server_and_client_session(
                        app, read_timeout_seconds=timedelta(seconds=5),
                    ) as session:
                        self.assertEqual(requests, [])
                        yield session, requests, captured
            self.assertEqual(closed, [True])
            self.assertTrue(all(stream.closed for stream in streams))
        finally:
            root.handlers, root.level = saved

    async def test_discovery_is_closed_evidenced_read_only_registry(self):
        async with self.session() as (session, requests, _):
            result = await session.list_tools()
            self.assertEqual({tool.name for tool in result.tools},
                             EXPECTED_TOOLS)
            for tool in result.tools:
                schema = tool.inputSchema
                self.assertFalse(schema['additionalProperties'])
                self.assertEqual(schema['properties']['max_results'][
                    'maximum'], 1000)
                self.assertEqual(schema['properties']['max_results'][
                    'minimum'], 1)
                self.assertEqual(schema['properties']['max_results'][
                    'default'], 20)
                self.assertFalse(set(schema['properties']) & {
                    'client', 'ctx', 'settings', 'token', 'endpoint', 'url',
                    'method', 'headers', 'tenant', 'currency',
                })
                self.assertTrue(tool.annotations.readOnlyHint)
                self.assertFalse(tool.annotations.destructiveHint)
                self.assertFalse(tool.annotations.idempotentHint)
                self.assertTrue(tool.annotations.openWorldHint)
                self.assertTrue(tool.description)
            self.assertEqual(requests, [])

    async def test_all_registered_consumers_use_guarded_closed_queries(self):
        cases = (
            ('search_products', {'query': 'item'}, 'reduzidos'),
            ('search_product_by_code', {'code': '0007'}, 'reduzidos'),
            ('get_product_details', {'product_id': 7}, 'reduzidos'),
            ('search_product_by_ean', {'ean': '00123'}, 'reduzidos'),
            ('get_product_price', {'product_id': '7'}, 'precos'),
            ('check_inventory', {'reduced_id': '001'}, 'estoque'),
            ('list_products', {}, 'reduzidos'),
        )
        async with self.session() as (session, requests, _):
            for name, arguments, route in cases:
                with self.subTest(name=name):
                    reply = await session.call_tool(name, arguments)
                    self.assertFalse(reply.isError)
                    data = reply.structuredContent
                    self.assertIsNotNone(data)
                    self.assertEqual(data['returned_count'], 1)
                    self.assertEqual(data['items'][0]['product_mask'], '0007')
                    self.assertEqual(data['items'][0]['price'], '1.2300')
                    self.assertIsNone(data['items'][0]['quantity'])
                    self.assertEqual(json.loads(reply.content[0].text), data)
                    request = requests[-1]
                    self.assertEqual(request.method, 'POST')
                    self.assertEqual(request.url.path,
                                     '/app-web/api/v2/produto/' + route)
                    body = json.loads(request.content)
                    expected: dict[str, object] = {'page': 1, 'limit': 20}
                    if name == 'get_product_details':
                        expected['idsProdutos'] = [7]
                    if name == 'search_product_by_code':
                        expected['mascara'] = '0007'
                    self.assertEqual(body, expected)
                    if name == 'get_product_price':
                        self.assertIsNone(data['currency'])
                        self.assertIn('currency_unknown', data['warnings'])
            self.assertEqual(len(requests), 7)

    async def test_invalid_inputs_are_safe_and_never_send(self):
        cases = [
            ('search_products', {'query': value})
            for value in ('', ' ', 'x' * 201, 'PRIVATE\n',
                          'PRIVATE\u200b', None, 1, True, [])
        ]
        cases += [
            ('get_product_details', {'product_id': value})
            for value in (True, '7', 7.0, -1, 9223372036854775808)
        ]
        cases += [
            ('list_products', {field: value})
            for field, values in (
                ('max_results', (0, 1001, True, '20', 20.0)),
                ('max_pages', (0, 101, True, '1')),
                ('page_size', (0, 1001, True, '1')),
            ) for value in values
        ]
        cases += [
            ('search_product_by_code', {'code': value})
            for value in ('', ' ', 'x' * 257, 'PRIVATE\ue000', 7, True)
        ]
        cases += [
            (name, {**arguments, field: 'PRIVATE'})
            for name, arguments in (
                ('search_products', {'query': 'item'}),
                ('get_product_price', {'product_id': '7'}),
                ('list_products', {}),
            ) for field in ('url', 'endpoint', 'token', 'currency', 'method')
        ]
        cases += [('PRIVATE', {}), ('search_product_by_sku', {'sku': '7'}),
                  ('search_products', {}),
                  ('list_products', {'max_results': 1, 'page_size': 2})]
        async with self.session() as (session, requests, captured):
            for name, arguments in cases:
                with self.subTest(name=name, arguments=arguments):
                    reply = await session.call_tool(name, arguments)
                    self.assertTrue(reply.isError)
                    self.assertNotIn('PRIVATE', reply.model_dump_json())
            self.assertEqual(requests, [])
            self.assertNotIn('PRIVATE', captured.getvalue())
            self.assertNotIn('Traceback', captured.getvalue())

    async def test_literal_codes_are_not_json_parsed_or_trimmed(self):
        for code in ('0007', ' 0007 ', '["literal"]', 'null', 'true'):
            def send(request):
                return response([row(mascara=code)], totalElements=1)

            async with self.session(send) as (session, requests, _):
                reply = await session.call_tool('search_product_by_code',
                                                {'code': code})
                self.assertFalse(reply.isError)
                self.assertEqual(reply.structuredContent['returned_count'], 1)
                self.assertEqual(json.loads(requests[0].content)['mascara'],
                                 code)

    async def test_empty_partial_and_upstream_errors_remain_distinct(self):
        for status, error in ((401, 'authentication_error'),
                              (403, 'authorization_error'),
                              (429, 'rate_limited'), (500, 'upstream_error')):
            async with self.session(lambda req: httpx.Response(
                status, stream=Stream(b'PRIVATE'),
            )) as (session, requests, _):
                reply = await session.call_tool('list_products', {})
                self.assertTrue(reply.isError)
                self.assertEqual(reply.structuredContent['status'], 'error')
                self.assertEqual(reply.structuredContent['error'], error)
                self.assertEqual(len(requests), 1)
                self.assertNotIn('PRIVATE', reply.model_dump_json())
        async with self.session(lambda req: response(
            [], totalElements=0,
        )) as (session, _, _):
            reply = await session.call_tool('list_products', {})
            self.assertFalse(reply.isError)
            self.assertEqual(reply.structuredContent['status'], 'not_found')
        async with self.session(lambda req: response(
            [row()], 1, 2,
        )) as (session, requests, _):
            reply = await session.call_tool('list_products', {})
            self.assertFalse(reply.isError)
            self.assertEqual(reply.structuredContent['status'], 'partial')
            self.assertFalse(reply.structuredContent['complete_dataset'])
            self.assertEqual(len(requests), 1)

    async def test_later_error_keeps_partial_payload_in_protocol(self):
        def send(request):
            if json.loads(request.content)['page'] == 1:
                return response([row()], 1, 2)
            return httpx.Response(403, stream=Stream(b'PRIVATE'))

        async with self.session(send) as (session, requests, _):
            reply = await session.call_tool('list_products', {
                'max_results': 2, 'page_size': 1, 'max_pages': 2,
            })
            self.assertFalse(reply.isError)
            self.assertEqual(reply.structuredContent['status'], 'partial')
            self.assertEqual(reply.structuredContent['returned_count'], 1)
            self.assertEqual(reply.structuredContent['error'],
                             'authorization_error')
            self.assertEqual(len(requests), 2)

    async def test_unexpected_exception_is_safe(self):
        async with self.session() as (session, _, captured):
            with patch('tools.list_products', side_effect=RuntimeError(
                'SYNTHETIC_PRIVATE_TOKEN https://example.invalid PRIVATE',
            )):
                reply = await session.call_tool('list_products', {})
            self.assertTrue(reply.isError)
            combined = reply.model_dump_json() + captured.getvalue()
            for secret in ('PRIVATE', 'example.invalid', 'Traceback'):
                self.assertNotIn(secret, combined)

    async def test_cancelled_query_propagates_and_completes_cleanup(self):
        started, released = anyio.Event(), anyio.Event()

        class WaitingStream(httpx.AsyncByteStream):
            async def __aiter__(self):
                started.set()
                await anyio.sleep_forever()
                yield b''

            async def aclose(self):
                await anyio.sleep(0)
                self.closed = True
                released.set()

        returned = []
        async with self.session(lambda req: httpx.Response(
            200, stream=WaitingStream(),
        )) as (session, requests, _):
            async def call():
                returned.append(await session.call_tool('list_products', {}))

            async with anyio.create_task_group() as group:
                group.start_soon(call)
                await started.wait()
                # SDK task cancellation alone does not send a protocol cancel.
                # initialize is request 0; this first tools/call is request 1.
                await session.send_notification(types.ClientNotification(
                    types.CancelledNotification(
                        params=types.CancelledNotificationParams(requestId=1),
                    ),
                ))
                with anyio.fail_after(3):
                    await released.wait()
                group.cancel_scope.cancel()
            self.assertEqual(returned, [])
            self.assertEqual(len(requests), 1)

    async def test_discovered_schemas_describe_identity_and_page_limits(self):
        async with self.session() as (session, _, _):
            listed = await session.list_tools()
            schemas = {tool.name: tool.inputSchema for tool in listed.tools}
            for name, field, maximum in (
                ('search_products', 'query', 200),
                ('search_product_by_code', 'code', 256),
                ('search_product_by_ean', 'ean', 256),
                ('get_product_price', 'product_id', 256),
                ('check_inventory', 'reduced_id', 256),
            ):
                schema = schemas[name]['properties'][field]
                self.assertEqual(schema['type'], 'string')
                self.assertEqual(schema['minLength'], 1)
                self.assertEqual(schema['maxLength'], maximum)
                self.assertIn(field, schemas[name]['required'])
            product_id = schemas['get_product_details']['properties'][
                'product_id'
            ]
            self.assertEqual(product_id['type'], 'integer')
            self.assertEqual(product_id['minimum'], 0)
            self.assertEqual(product_id['maximum'], 9223372036854775807)
            listing = schemas['list_products']['properties']
            self.assertEqual(listing['max_pages']['default'], 1)
            self.assertEqual(listing['max_pages']['minimum'], 1)
            self.assertEqual(listing['max_pages']['maximum'], 100)
            self.assertEqual(listing['page_size']['anyOf'][0]['minimum'], 1)
            self.assertEqual(listing['page_size']['anyOf'][0]['maximum'], 1000)


if __name__ == '__main__':
    unittest.main()
