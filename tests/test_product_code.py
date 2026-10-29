"""Commercial-code lookup through the real guarded mock transport."""
import json
from typing import Any, cast

import anyio
import httpx

from client import BlockedOperationError
from test_client import Stream, response, row
from test_tools import ProductToolsTestCase
import tools


class ProductCodeTests(ProductToolsTestCase):
    async def call(self, code: Any = '00-Ab', budget: Any = 20):
        function = getattr(tools, 'search_product_by_code', None)
        self.assertTrue(callable(function), 'search_product_by_code missing')
        return await cast(Any, function)(self.client, code, budget)

    async def test_mask_closed_body_and_literal_route(self):
        code = ' 00-Ab/? '
        await self.client._query('products', 1, 2, product_mask=code)
        request = self.requests[-1]
        self.assertEqual(self.bodies(), [
            {'page': 1, 'limit': 2, 'mascara': code},
        ])
        self.assertEqual(request.method, 'POST')
        self.assertEqual(request.url.query, b'')
        self.assertEqual(request.url.host, 'example.invalid')
        self.assertEqual(request.url.path, '/app-web/api/v2/produto/reduzidos')
        self.assertTrue(self.streams[-1].closed)

    async def test_invalid_masks_combinations_and_operations_never_send(self):
        for value in ('', ' ', 'x' * 257, 'SECRET\n', '\u200b', '\ud800',
                      '\ue000', '\u0378', 7, True, [], {}):
            for collect in (False, True):
                with self.subTest(value=repr(value), collect=collect):
                    with self.assertRaises(BlockedOperationError) as caught:
                        if collect:
                            await self.client._collect(
                                'products', product_mask=cast(Any, value),
                            )
                        else:
                            await self.client._query(
                                'products', 1, 1,
                                product_mask=cast(Any, value),
                            )
                    self.assertNotIn('SECRET', str(caught.exception))
        for operation in ('prices', 'stock'):
            with self.assertRaises(BlockedOperationError):
                await self.client._query(operation, 1, 1, product_mask='00')
            with self.assertRaises(BlockedOperationError):
                await self.client._collect(operation, product_mask='00')
        with self.assertRaises(BlockedOperationError):
            await self.client._query(
                'products', 1, 1, product_id=7, product_mask='00',
            )
        with self.assertRaises(BlockedOperationError):
            await self.client._collect(
                'products', product_id=7, product_mask='00',
            )
        self.assertEqual(self.requests, [])

    async def test_mask_pages_keep_filter_with_provider_partial_match(self):
        def pages(request):
            page = json.loads(request.content)['page']
            return response([
                row(str(page), mascara='00-Ab' if page == 1 else '00-Ab-X'),
            ], page, 2, totalElements=2)

        self.handler = pages
        result = await self.client._collect(
            'products', page_size=1, max_results=2, product_mask='00-Ab',
        )
        self.assertEqual(self.bodies(), [
            {'page': 1, 'limit': 1, 'mascara': '00-Ab'},
            {'page': 2, 'limit': 1, 'mascara': '00-Ab'},
        ])
        self.assertEqual(len(result.items), 2)
        self.assertEqual(result.status, 'found')
        self.assertIsNone(result.error)

    async def test_none_mask_preserves_legacy_bodies(self):
        for operation in ('products', 'prices', 'stock'):
            await self.client._query(operation, 1, 1, product_mask=None)
        self.assertEqual(self.bodies(), [{'page': 1, 'limit': 1}] * 3)

    async def test_concurrent_mask_and_id_filters_stay_local(self):
        ready = anyio.Event()
        started = 0

        class Together(Stream):
            async def __aiter__(self):
                nonlocal started
                started += 1
                if started == 2:
                    ready.set()
                await ready.wait()
                async for chunk in super().__aiter__():
                    yield chunk

        def handle(request):
            body = json.loads(request.content)
            return httpx.Response(200, stream=Together(json.dumps({
                'result': [row(idProduto=7, mascara=body.get('mascara'))],
                'page': 1, 'totalPages': 1,
            }).encode()))

        self.handler = handle

        async def collect_id():
            await self.client._collect('products', product_id=7, max_results=1)

        async def collect_mask():
            await self.client._collect(
                'products', product_mask='00-Ab', max_results=1,
            )

        with anyio.fail_after(2):
            async with anyio.create_task_group() as group:
                group.start_soon(collect_id)
                group.start_soon(collect_mask)
        self.assertCountEqual(self.bodies(), [
            {'page': 1, 'limit': 1, 'idsProdutos': [7]},
            {'page': 1, 'limit': 1, 'mascara': '00-Ab'},
        ])
        self.assertEqual(self.client._max_results, 100)

    async def test_remote_code_matches_only_mask_and_keeps_api_sku(self):
        self.handler = lambda request: response([
            row('01', mascara='00-Ab', codigoSku='API-01'),
            row('02', mascara='00-Ab', codigoSku=None),
            row('03', mascara='00-ab'), row('04', mascara='00-Ab-X'),
            row('05', mascara='other', codigoSku='00-Ab'),
            row('06', mascara=None), row('07', descricao='00-Ab'),
        ], totalElements=7)
        result = await self.call()
        self.assertEqual(self.bodies(), [
            {'page': 1, 'limit': 20, 'mascara': '00-Ab'},
        ])
        self.assertEqual(result['status'], 'found')
        self.assertEqual(result['returned_count'], 2)
        self.assertEqual(result['items'][0]['sku'], 'API-01')
        self.assertIsNone(result['items'][1]['sku'])
        self.assertEqual(result['rows_received'], 7)
        self.assertEqual(result['warnings'], [
            'remote_product_code_exact_match',
        ])
        json.dumps(result, allow_nan=False)

    async def test_code_input_and_budget_invalid_before_send(self):
        for value in ('', ' ', 'x' * 257, 'SECRET\n', '\u200b', '\ud800',
                      '\ue000', '\u0378', None, 7, True, [], {}):
            with self.subTest(value=repr(value)):
                with self.assertRaises(ValueError) as caught:
                    await self.call(value)
                self.assertNotIn('SECRET', str(caught.exception))
        for budget in (True, 0, -1, 1001, '20', 1.0, None):
            with self.assertRaises(ValueError):
                await self.call(budget=budget)
        self.assertEqual(self.requests, [])

    async def test_code_boundary_and_whitespace_preserved(self):
        for code in ('x', 'x' * 256, ' 00-Ab ', '\u00a000-Ab\u00a0'):
            with self.subTest(code=code):
                self.handler = lambda request: response([
                    row('01', mascara=code), row('02', mascara='other'),
                ])
                result = await self.call(code)
                self.assertEqual(result['returned_count'], 1)
                self.assertEqual(result['items'][0]['product_mask'], code)
                self.assertEqual(self.bodies()[-1]['mascara'], code)

    async def test_code_partial_empty_and_errors_are_not_absence(self):
        for code in (401, 403, 404, 429, 500, None):
            for preceding in (False, True):
                with self.subTest(code=code, preceding=preceding):
                    self.requests.clear()

                    def handle(request):
                        page = json.loads(request.content)['page']
                        if preceding and page == 1:
                            return response([row(mascara='other')], 1, 2)
                        if code is None:
                            raise httpx.ReadTimeout('SECRET')
                        return httpx.Response(code, stream=Stream(b'SECRET'))

                    self.handler = handle
                    result = await self.call(budget=100)
                    self.assertEqual(result['returned_count'], 0)
                    self.assertEqual(result['status'],
                                     'partial' if preceding else 'error')
                    self.assertIsNotNone(result['error'])
                    self.assertFalse(result['complete_dataset'])
                    self.assertNotIn('SECRET', json.dumps(result))
        self.handler = lambda request: response([row(mascara='other')], 1, 2)
        result = await self.call(budget=1)
        self.assertEqual(result['status'], 'partial')
        self.assertEqual(result['returned_count'], 0)
        self.handler = lambda request: response([], totalElements=0)
        result = await self.call()
        self.assertEqual(result['status'], 'not_found')
        self.assertTrue(result['complete_dataset'])

    async def test_code_config_cap_and_exact_decimal_projection(self):
        self.client = self.make_client(max_results=1)
        self.handler = lambda request: httpx.Response(200, stream=Stream(
            b'{"result":[{"idProduto":7,"idReduzido":"0001",'
            b'"mascara":"00-Ab","valor":0.1234567890123456789}],'
            b'"page":1,"totalPages":2}'
        ))
        result = await self.call(budget=1000)
        self.assertEqual(self.bodies(), [
            {'page': 1, 'limit': 1, 'mascara': '00-Ab'},
        ])
        self.assertEqual(result['status'], 'partial')
        self.assertEqual(result['items'][0]['price'], '0.1234567890123456789')
        self.assertEqual(result['items'][0]['reduced_id'], '0001')
        self.assertIsNone(result['items'][0]['sku'])
        self.assertIn('codigoSku', result['items'][0]['missing_fields'])
