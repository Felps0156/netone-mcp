"""Sprint 8 contracts through real consumers and synthetic HTTP streams."""

import json
from decimal import Decimal
from typing import Any, cast
import unittest

import anyio
import httpx

from client import BlockedOperationError
from test_client import Stream, response, row
from test_tools import ProductToolsTestCase
import tools


class CommercialToolsCase(ProductToolsTestCase):
    def function(self, name):
        value = getattr(tools, name, None)
        self.assertTrue(callable(value), f'{name} is missing')
        return cast(Any, value)

    async def invalid_inputs(self, function):
        class IntegerSubclass(int):
            pass

        for code in ('', ' ', 'x' * 257, 'SECRET\n', 'SECRET\u200b',
                     'SECRET\ud800', 'SECRET\ue000', 'SECRET\u0378',
                     None, 1, True, b'X', []):
            with self.assertRaises(ValueError) as caught:
                await function(self.client, code)
            self.assertNotIn('SECRET', str(caught.exception))
        for cap in (True, 0, -1, 1001, 'SECRET', 1.0, Decimal(1),
                    None, IntegerSubclass(1)):
            with self.assertRaises(ValueError) as caught:
                await function(self.client, '0001', cap)
            self.assertNotIn('SECRET', str(caught.exception))
        self.assertEqual(self.requests, [])

    async def error_cases(self, function, field):
        for code, error in ((401, 'authentication_error'),
                            (403, 'authorization_error'), (404, 'not_found'),
                            (429, 'rate_limited'), (500, 'upstream_error'),
                            (None, 'timeout')):
            for prior in (None, False, True):
                self.requests.clear()

                def pages(req):
                    page = json.loads(req.content)['page']
                    if page == 1 and prior is not None:
                        return response([
                            row(**{field: '0001' if prior else 'other'}),
                        ], 1, 2)
                    if code is None:
                        raise httpx.ReadTimeout('SECRET')
                    return httpx.Response(code, stream=Stream(b'SECRET'))

                self.handler = pages
                result = await function(self.client, '0001', 100)
                self.assertEqual(result['error'], error)
                self.assertEqual(result['status'],
                                 'error' if prior is None else 'partial')
                self.assertEqual(result['returned_count'], int(prior is True))
                self.assertEqual(len(self.requests),
                                 1 if prior is None else 2)
                self.assertFalse(result['complete_dataset'])
                self.assertNotIn('SECRET', json.dumps(result))
        self.requests.clear()
        self.handler = lambda req: response([], totalElements=0)
        result = await function(self.client, '0001')
        self.assertEqual(result['status'], 'not_found')
        self.assertTrue(result['complete_dataset'])
        self.handler = lambda req: response([
            row(**{field: 'other'}),
        ], 1, 2)
        result = await function(self.client, '0001', 1)
        self.assertEqual(result['status'], 'partial')
        self.assertEqual(result['returned_count'], 0)


class PriceTests(CommercialToolsCase):
    async def test_price_exact_id_and_closed_body(self):
        function = self.function('get_product_price')
        self.handler = lambda req: response([
            row('001', idProduto='0001'), row('002', idProduto='0001'),
            row('003', idProduto='1', mascara='0001', codigoSku='0001'),
            row('004', idProduto=' 0001 '),
        ])
        result = await function(self.client, '0001')
        self.assertEqual(result['returned_count'], 2)
        self.assertEqual([item['reduced_id'] for item in result['items']],
                         ['001', '002'])
        self.assertEqual(self.bodies(), [{'page': 1, 'limit': 20}])
        self.assertEqual(self.requests[0].url.path,
                         '/app-web/api/v2/produto/precos')
        self.assertEqual(result['status'], 'found')
        self.assertIn('price_missing', result['warnings'])
        for identity in ('x', 'x' * 256, ' 0001 ', '\u00a00001\u00a0'):
            self.handler = lambda req: response([row(idProduto=identity)])
            result = await function(self.client, identity)
            self.assertEqual(result['items'][0]['product_id'], identity)

    async def test_price_precision_and_presence(self):
        function = self.function('get_product_price')
        self.handler = lambda req: httpx.Response(200, stream=Stream(
            b'{"result":[{"idProduto":"0001","idReduzido":"001",'
            b'"valor":0.123456789012345678901,"tabelaPreco":"Retail",'
            b'"valorAtacado":0,"tabelaPrecoAtacado":"Wholesale"},'
            b'{"idProduto":"0001","idReduzido":"002","valor":null},'
            b'{"idProduto":"0001","idReduzido":"003"}],'
            b'"page":1,"totalPages":1,"totalElements":3}'
        ))
        result = await function(self.client, '0001')
        first, second, third = result['items']
        self.assertEqual(first['price'], '0.123456789012345678901')
        self.assertEqual(first['wholesale_price'], '0')
        self.assertEqual(first['price_table'], 'Retail')
        self.assertEqual(first['wholesale_price_table'], 'Wholesale')
        self.assertIsNone(second['price'])
        self.assertNotIn('valor', second['missing_fields'])
        self.assertIn('valor', third['missing_fields'])
        self.assertIn('nominal_prices_not_final_quote', result['warnings'])
        self.assertEqual(result['price_kind'], 'source_retail_and_wholesale')
        json.dumps(result, allow_nan=False)

    async def test_price_currency_provenance(self):
        function = self.function('get_product_price')
        for currency in ('USD', '', 'brl', 1, True, [], {}):
            with self.assertRaises(ValueError):
                await function(self.client, '0001', currency=currency)
        self.assertEqual(self.requests, [])
        result = await function(self.client, '0001')
        self.assertIsNone(result['currency'])
        self.assertIsNone(result['currency_source'])
        self.assertIn('currency_unknown', result['warnings'])
        result = await function(self.client, '0001', currency='BRL')
        self.assertEqual(result['currency'], 'BRL')
        self.assertEqual(result['currency_source'], 'operator_confirmation')
        self.assertNotIn('currency_unknown', result['warnings'])
        self.assertEqual(self.bodies(), [{'page': 1, 'limit': 20}] * 2)

    async def test_price_inputs_never_send(self):
        await self.invalid_inputs(self.function('get_product_price'))

    async def test_price_error_precedence(self):
        await self.error_cases(self.function('get_product_price'), 'idProduto')


class InventoryTests(CommercialToolsCase):
    async def test_inventory_exact_reduced_id_and_closed_body(self):
        function = self.function('check_inventory')
        await self.invalid_inputs(function)
        self.handler = lambda req: response([
            {'idReduzido': '0001', 'quantidade': 0},
            row('1', idProduto='0001', mascara='0001', codigoSku='0001'),
            row(' 0001 '),
        ])
        result = await function(self.client, '0001')
        self.assertEqual(result['returned_count'], 1)
        self.assertEqual(result['items'][0]['reduced_id'], '0001')
        self.assertIsNone(result['items'][0]['product_id'])
        self.assertEqual(self.bodies(), [{'page': 1, 'limit': 20}])
        self.assertEqual(self.requests[0].url.path,
                         '/app-web/api/v2/produto/estoque')

    async def test_inventory_presence_scope_and_time(self):
        function = self.function('check_inventory')
        for extra, expected, missing in (
            ({'quantidade': 0}, '0', False),
            ({'quantidade': -2}, '-2', False),
            ({'quantidade': None}, None, False), ({}, None, True),
        ):
            self.handler = lambda req: response([
                row('0001', ultimaAlteracaoTimestamp='raw-time', **extra),
            ])
            result = await function(self.client, '0001')
            item = result['items'][0]
            self.assertEqual(item['quantity'], expected)
            self.assertEqual('quantidade' in item['missing_fields'], missing)
            self.assertEqual('quantity_missing' in result['warnings'],
                             expected is None)
            self.assertEqual(item['last_changed_raw'], 'raw-time')
            self.assertNotEqual(result['retrieved_at'], 'raw-time')
            self.assertEqual(result['inventory_scope'], {
                'selection': 'configured_user_deposit', 'deposit_id': None,
                'branch_id': None,
                'quantity_basis': 'physical_minus_reservations',
            })
            self.assertIn('inventory_scope_unverified', result['warnings'])
            self.assertIn('inventory_freshness_unverified', result['warnings'])
            self.assertNotIn('available', item)
            self.assertEqual(result['status'], 'found')
            json.dumps(result, allow_nan=False)
        self.handler = lambda req: response([row('0001')])
        result = await function(self.client, '0001')
        self.assertIsNone(result['items'][0]['last_changed_raw'])

    async def test_inventory_error_precedence(self):
        await self.error_cases(self.function('check_inventory'), 'idReduzido')

    async def test_inventory_conflicts_duplicates_and_unknown_metadata(self):
        function = self.function('check_inventory')
        self.handler = lambda req: response([
            row('0001', quantidade=1), row('0001', quantidade=1),
            row('0001', quantidade=2),
        ])
        result = await function(self.client, '0001')
        self.assertEqual(result['status'], 'partial')
        self.assertEqual(result['returned_count'], 2)
        self.assertIn('duplicate_rows_removed', result['warnings'])
        self.assertIn('conflicting_rows_preserved', result['warnings'])
        self.assertEqual(result['rows_received'], 3)
        self.handler = lambda req: httpx.Response(
            200, stream=Stream(b'{"result":[]}'),
        )
        result = await function(self.client, '0001')
        self.assertEqual(result['status'], 'partial')
        self.assertFalse(result['complete_dataset'])


class DirectedCommercialTests(ProductToolsTestCase):
    """User-supplied identities, with entirely synthetic commercial values."""

    def cases(self):
        return (
            (tools.get_product_price, '283688', 'prices',
             'idsProdutos', 'idProduto', 283688),
            (tools.check_inventory, '1697854', 'stock',
             'idsReduzidos', 'idReduzido', 1697854),
        )

    async def test_reported_product_92361_uses_directed_queries(self):
        def send(request):
            body = json.loads(request.content)
            if request.url.path.endswith('/reduzidos'):
                if body.get('mascara') == '92361':
                    return response([row(
                        idReduzido=1697854, idProduto=283688, mascara='92361',
                        descricao='Synthetic regression product',
                    )], totalElements=1)
            elif request.url.path.endswith('/estoque'):
                if body.get('idsReduzidos') == [1697854]:
                    return response([{'idReduzido': 1697854,
                                      'quantidade': 0}], totalElements=1)
            elif body.get('idsProdutos') == [283688]:
                return response([row(
                    idReduzido=1697854, idProduto=283688, valor=12,
                    tabelaPreco='Synthetic retail',
                )], totalElements=1)
            return response([row(idReduzido=1, idProduto=1)], 1, 985)

        self.handler = send
        catalog = cast(Any, await tools.search_product_by_code(
            self.client, '92361',
        ))
        product = catalog['items'][0]
        stock = cast(Any, await tools.check_inventory(
            self.client, product['reduced_id'],
        ))
        price = cast(Any, await tools.get_product_price(
            self.client, product['product_id'],
        ))
        self.assertEqual(stock['status'], 'found')
        self.assertEqual(stock['items'][0]['quantity'], '0')
        self.assertEqual(price['status'], 'found')
        self.assertEqual(price['items'][0]['price'], '12')
        self.assertEqual(self.bodies(), [
            {'page': 1, 'limit': 20, 'mascara': '92361'},
            {'page': 1, 'limit': 20, 'idsReduzidos': [1697854]},
            {'page': 1, 'limit': 20, 'idsProdutos': [283688]},
        ])
        for result in (stock, price):
            self.assertTrue(result['complete_dataset'])
            self.assertFalse(result['partial'])
            self.assertIsNone(result['error'])
            self.assertEqual(result['pages_fetched'], 1)
            self.assertEqual(result['rows_received'], 1)
            self.assertEqual(result['lookup_strategy'], 'remote_id_filter')

    async def test_canonical_boundaries_and_noncanonical_compatibility(self):
        for function, _, _, key, source, _ in self.cases():
            for identity in ('0', '9223372036854775807'):
                with self.subTest(name=function.__name__, identity=identity):
                    self.handler = lambda req: response([
                        row(identity, **{source: identity}),
                    ])
                    result = await function(self.client, identity)
                    self.assertEqual(result['status'], 'found')
                    self.assertEqual(self.bodies()[-1][key], [int(identity)])
            for identity in ('0001', ' 1 ', '+1', '1.0', '\u0661', 'x' * 256):
                self.handler = lambda req: response([
                    row(identity, **{source: identity}),
                ])
                result = cast(Any, await function(self.client, identity))
                self.assertEqual(result['lookup_strategy'],
                                 'bounded_local_exact')
                self.assertIn('numeric_id_filter_unavailable',
                              result['warnings'])
                self.assertEqual(self.bodies()[-1], {'page': 1, 'limit': 20})
                field = 'product_id' if source == 'idProduto' else 'reduced_id'
                self.assertEqual(result['items'][0][field], identity)
            before = len(self.requests)
            for identity in ('9223372036854775808', '9' * 256):
                with self.assertRaises(tools.ToolInputError):
                    await function(self.client, identity)
            self.assertEqual(len(self.requests), before)

    async def test_directed_page_rejects_wrong_identity_atomically(self):
        for function, identity, _, _, source, numeric in self.cases():
            for other in (numeric + 1, '0' + identity, None):
                with self.subTest(function=function.__name__, other=other):
                    self.requests.clear()
                    self.handler = lambda req: response([
                        row('a', **{source: numeric}),
                        row('b', **{source: other}),
                    ])
                    result = await function(self.client, identity)
                    self.assertEqual(result['status'], 'error')
                    self.assertEqual(result['error'], 'invalid_response')
                    self.assertEqual(result['items'], [])
                    self.assertFalse(result['complete_dataset'])
                    self.assertEqual(len(self.requests), 1)

    async def test_directed_later_invalid_page_keeps_previous_data(self):
        for function, identity, _, key, source, numeric in self.cases():
            self.requests.clear()

            def send(request):
                page = json.loads(request.content)['page']
                rows = [row('a', **{source: numeric})]
                if page == 2:
                    rows = [row('b', **{source: numeric}),
                            row('c', **{source: numeric + 1})]
                return response(rows, page, 2)

            self.handler = send
            result = await function(self.client, identity, 100)
            self.assertEqual(result['status'], 'partial')
            self.assertEqual(result['error'], 'invalid_response')
            self.assertEqual(result['returned_count'], 1)
            self.assertEqual(result['last_page'], 1)
            self.assertIsNone(result['next_page'])
            self.assertEqual(self.bodies(), [
                {'page': 1, 'limit': 50, key: [numeric]},
                {'page': 2, 'limit': 50, key: [numeric]},
            ])

    async def test_directed_zero_unknown_absent_and_partial_are_distinct(self):
        for fields, quantity, missing in (
            ({'quantidade': 0}, '0', False),
            ({'quantidade': None}, None, False), ({}, None, True),
        ):
            self.handler = lambda req: response([
                {'idReduzido': 1697854, **fields},
            ], totalElements=1)
            result = cast(Any, await tools.check_inventory(
                self.client, '1697854',
            ))
            self.assertEqual(result['status'], 'found')
            self.assertEqual(result['items'][0]['quantity'], quantity)
            self.assertEqual(
                'quantidade' in result['items'][0]['missing_fields'], missing,
            )
            self.assertEqual('quantity_missing' in result['warnings'],
                             quantity is None)
            self.assertFalse(result['partial'])
            self.assertEqual(self.bodies()[-1]['idsReduzidos'], [1697854])
        for envelope, expected in (
            ({'result': [], 'page': 1, 'totalPages': 1,
              'totalElements': 0}, 'not_found'),
            ({'result': []}, 'partial'),
            ({'result': [{'idReduzido': 1697854, 'quantidade': 0}],
              'page': 1, 'totalPages': 985}, 'partial'),
        ):
            self.handler = lambda req: httpx.Response(
                200, stream=Stream(json.dumps(envelope).encode()),
            )
            result = await tools.check_inventory(self.client, '1697854', 1)
            self.assertEqual(result['status'], expected)
            self.assertEqual(result['complete_dataset'],
                             expected == 'not_found')
            self.assertIsNone(result['error'])

    async def test_directed_price_keeps_variants_tables_and_precision(self):
        def send(request):
            page = json.loads(request.content)['page']
            data = (
                b'{"result":[{"idProduto":283688,"idReduzido":1,'
                b'"valor":0.123456789012345678901,"valorAtacado":0,'
                b'"tabelaPreco":"Retail","tabelaPrecoAtacado":"Wholesale"}],'
                b'"page":1,"totalPages":2,"totalElements":2}'
                if page == 1 else
                b'{"result":[{"idProduto":283688,"idReduzido":2,'
                b'"valor":null,"tabelaPreco":"Other source table"}],'
                b'"page":2,"totalPages":2,"totalElements":2}'
            )
            return httpx.Response(200, stream=Stream(data))

        self.handler = send
        result = cast(Any, await tools.get_product_price(
            self.client, '283688', 100,
        ))
        self.assertEqual(result['returned_count'], 2)
        self.assertEqual(result['items'][0]['price'],
                         '0.123456789012345678901')
        self.assertEqual(result['items'][0]['wholesale_price'], '0')
        self.assertEqual(result['items'][1]['price_table'],
                         'Other source table')
        self.assertIsNone(result['items'][1]['price'])
        self.assertTrue(result['complete_dataset'])
        self.assertEqual(self.bodies(), [
            {'page': 1, 'limit': 50, 'idsProdutos': [283688]},
            {'page': 2, 'limit': 50, 'idsProdutos': [283688]},
        ])

    async def test_directed_failures_never_replay_or_fallback(self):
        for function, identity, _, key, _, numeric in self.cases():
            for status, error in ((401, 'authentication_error'),
                                  (403, 'authorization_error'),
                                  (404, 'not_found'), (429, 'rate_limited'),
                                  (500, 'upstream_error'),
                                  (307, 'upstream_error'), (None, 'timeout')):
                self.requests.clear()

                def send(request):
                    if status is None:
                        raise httpx.ReadTimeout('SECRET')
                    return httpx.Response(status, stream=Stream(b'SECRET'),
                                          headers={'Location': '/elsewhere',
                                                   'Retry-After': '1'})

                self.handler = send
                result = await function(self.client, identity)
                self.assertEqual(result['status'], 'error')
                self.assertEqual(result['error'], error)
                self.assertEqual(result['items'], [])
                self.assertEqual(self.bodies(), [
                    {'page': 1, 'limit': 20, key: [numeric]},
                ])
                self.assertNotIn('SECRET', json.dumps(result))


    async def test_directed_caps_conflicts_and_later_errors_stay_partial(self):
        for function, identity, _, key, source, numeric in self.cases():
            for failure in ('cap', 'conflict', 'http', 'metadata'):
                self.requests.clear()

                def send(request):
                    page = json.loads(request.content)['page']
                    if page == 2:
                        return httpx.Response(403, stream=Stream(b'SECRET'))
                    records = [row('a', **{source: numeric}, quantidade=0)]
                    if failure == 'conflict':
                        records.append(row(
                            'a', **{source: numeric}, quantidade=2,
                        ))
                    if failure == 'metadata':
                        return httpx.Response(200, stream=Stream(json.dumps({
                            'result': records,
                        }).encode()))
                    return response(records, 1,
                                    1 if failure == 'conflict' else 2)

                self.handler = send
                instance = self.make_client(max_results=2, max_pages=1)
                if failure == 'http':
                    instance = self.client
                result = await function(instance, identity, 100)
                self.assertEqual(result['status'], 'partial')
                self.assertFalse(result['complete_dataset'])
                self.assertEqual(result['error'],
                                 'authorization_error' if failure == 'http'
                                 else None)
                self.assertTrue(result['items'])
                self.assertEqual(len(self.requests),
                                 2 if failure == 'http' else 1)
                self.assertTrue(all(body[key] == [numeric]
                                    for body in self.bodies()))

    async def test_stock_conflict_uses_reduced_id_not_optional_product(self):
        for products in ((7, 8), (None, 8), (7, None)):
            records = [
                {'idReduzido': 42, 'quantidade': 0},
                {'idReduzido': 42, 'quantidade': 9},
            ]
            for record, product in zip(records, products):
                if product is not None:
                    record['idProduto'] = product
            self.handler = lambda req: response(records, totalElements=2)
            for name, arguments in (
                ('check_inventory', {'reduced_id': '42'}),
                ('list_inventory', {}), ('analyze_inventory', {}),
            ):
                with self.subTest(name=name, products=products):
                    result = await getattr(tools, name)(
                        self.client, **arguments,
                    )
                    self.assertEqual(result['status'], 'partial')
                    self.assertTrue(result['partial'])
                    self.assertFalse(result['complete_dataset'])
                    self.assertIsNone(result['error'])
                    self.assertIn('conflicting_rows_preserved',
                                  result['warnings'])
                    self.assertEqual(result['returned_count'], 2)
                    self.assertEqual(
                        [item['quantity'] for item in result['items']],
                        ['0', '9'],
                    )
                    self.assertFalse(result['block_complete'])
                    self.assertIsNone(result['next_page'])

    async def test_directed_concurrent_ids_and_budgets_do_not_leak(self):
        ready = anyio.Event()
        started = 0
        results = {}

        class Overlap(Stream):
            async def __aiter__(self):
                nonlocal started
                started += 1
                if started == 3:
                    ready.set()
                await ready.wait()
                async for chunk in super().__aiter__():
                    yield chunk

        def send(request):
            body = json.loads(request.content)
            product = body.get('idsProdutos', [1])[0]
            reduced = body.get('idsReduzidos', [1])[0]
            return httpx.Response(200, stream=Overlap(json.dumps({
                'result': [row(str(reduced), idProduto=product, quantidade=0)],
                'page': 1, 'totalPages': 1, 'totalElements': 1,
            }).encode()))

        async def lookup(name, identity, budget):
            results[(name, identity)] = await getattr(tools, name)(
                self.client, identity, budget,
            )

        self.handler = send
        with anyio.fail_after(2):
            async with anyio.create_task_group() as group:
                group.start_soon(lookup, 'check_inventory', '7', 1)
                group.start_soon(lookup, 'check_inventory', '8', 2)
                group.start_soon(lookup, 'get_product_price', '9', 3)
        bodies = sorted(self.bodies(), key=lambda body: body['limit'])
        self.assertEqual(bodies, [
            {'page': 1, 'limit': 1, 'idsReduzidos': [7]},
            {'page': 1, 'limit': 2, 'idsReduzidos': [8]},
            {'page': 1, 'limit': 3, 'idsProdutos': [9]},
        ])
        self.assertEqual(results[('check_inventory', '7')]['items'][0][
            'reduced_id'], '7')
        self.assertEqual(results[('check_inventory', '8')]['items'][0][
            'reduced_id'], '8')
        self.assertEqual(results[('get_product_price', '9')]['items'][0][
            'product_id'], '9')
        self.assertEqual(self.client._max_results, 100)
        self.assertEqual(self.client._max_pages, 5)

    async def test_directed_cancellation_propagates_after_stream_cleanup(self):
        for function, identity, _, key, _, numeric in self.cases():
            started = anyio.Event()
            returned = []

            class Waiting(Stream):
                async def __aiter__(self):
                    started.set()
                    await anyio.sleep_forever()
                    yield b''

            stream = Waiting(close_delay=0.01)
            self.handler = lambda req: httpx.Response(200, stream=stream)

            async def call():
                returned.append(await function(self.client, identity))

            with anyio.fail_after(2):
                async with anyio.create_task_group() as group:
                    group.start_soon(call)
                    await started.wait()
                    group.cancel_scope.cancel()
            self.assertEqual(returned, [])
            self.assertTrue(stream.closed)
            self.assertEqual(stream.close_count, 1)
            self.assertEqual(self.bodies()[-1][key], [numeric])


class ListTests(CommercialToolsCase):
    async def test_list_defaults_to_one_page(self):
        function = self.function('list_products')
        self.handler = lambda req: response([row()], 1, 2)
        result = await function(self.client)
        self.assertEqual(self.bodies(), [{'page': 1, 'limit': 20}])
        self.assertEqual(self.requests[0].url.path,
                         '/app-web/api/v2/produto/reduzidos')
        self.assertTrue(result['partial'])
        self.assertFalse(result['complete_dataset'])
        self.assertIn('page_limit_reached', result['warnings'])
        self.assertIn('provider_visible_catalog_only', result['warnings'])
        for rows, status in (([], 'not_found'), ([row()], 'found')):
            self.handler = lambda req: response(rows, totalElements=len(rows))
            result = await function(self.client)
            self.assertEqual(result['status'], status)
            self.assertTrue(result['complete_dataset'])

    async def test_list_explicit_fixed_pages_and_caps(self):
        function = self.function('list_products')

        def pages(req):
            page = json.loads(req.content)['page']
            return response([row(f'{page}a'), row(f'{page}b')], page, 4)

        self.handler = pages
        result = await function(self.client, 5, page_size=2, max_pages=3)
        self.assertEqual(self.bodies(), [
            {'page': 1, 'limit': 2}, {'page': 2, 'limit': 2},
        ])
        self.assertEqual(result['rows_received'], 4)
        self.assertIn('result_limit_reached', result['warnings'])
        self.assertEqual(result['status'], 'partial')
        self.requests.clear()
        instance = self.make_client(max_results=2, max_pages=1)
        result = await function(instance, 1000, max_pages=100)
        self.assertEqual(self.bodies(), [{'page': 1, 'limit': 2}])
        self.assertFalse(result['complete_dataset'])

    async def test_list_inputs_never_send(self):
        function = self.function('list_products')
        class IntegerSubclass(int):
            pass

        for name, values in (
            ('max_results', (0, 1001, True, '1', 1.0, None,
                             IntegerSubclass(1))),
            ('max_pages', (0, 101, True, '1', 1.0, None,
                           IntegerSubclass(1))),
            ('page_size', (0, 1001, True, '1', 1.0,
                           IntegerSubclass(1))),
        ):
            for value in values:
                with self.assertRaises((ValueError, BlockedOperationError)):
                    await function(self.client, **{name: value})
        instance = self.make_client(max_results=2)
        with self.assertRaises(ValueError):
            await function(instance, 100, page_size=3)
        self.assertEqual(self.requests, [])

    async def test_list_metadata_conflicts_and_errors(self):
        function = self.function('list_products')
        for data, error in (
            (b'{"result":[]}', None),
            (b'{"result":[],"page":1,"totalPages":1,"totalElements":1}',
             'invalid_response'),
        ):
            self.handler = lambda req: httpx.Response(200, stream=Stream(data))
            result = await function(self.client)
            self.assertTrue(result['partial'])
            self.assertEqual(result['error'], error)
        self.handler = lambda req: response([
            row(descricao='A'), row(descricao='A'), row(descricao='B'),
        ])
        result = await function(self.client)
        self.assertEqual(result['returned_count'], 2)
        self.assertEqual(result['status'], 'partial')
        self.assertIn('conflicting_rows_preserved', result['warnings'])
        for failed_page in (1, 2):
            self.requests.clear()

            def pages(req):
                page = json.loads(req.content)['page']
                if page == failed_page:
                    return httpx.Response(401, stream=Stream(b'SECRET'))
                return response([row()], page, 2)

            self.handler = pages
            result = await function(self.client, 2, page_size=1, max_pages=2)
            self.assertEqual(len(self.requests), failed_page)
            self.assertEqual(result['error'], 'authentication_error')
            self.assertEqual(result['status'],
                             'error' if failed_page == 1 else 'partial')
            self.assertNotIn('SECRET', json.dumps(result))

    async def test_list_concurrent_with_existing_search(self):
        function = self.function('list_products')
        ready = anyio.Event()
        started = 0
        results = {}

        class Overlap(Stream):
            async def __aiter__(self):
                nonlocal started
                started += 1
                if started == 2:
                    ready.set()
                await ready.wait()
                async for chunk in super().__aiter__():
                    yield chunk

        def pages(req):
            page = json.loads(req.content)['page']
            return httpx.Response(200, stream=Overlap(json.dumps({
                'result': [row(str(page), descricao='Match')],
                'page': page, 'totalPages': 2,
            }).encode()))

        async def listing():
            results['list'] = await function(self.client, 1)

        async def searching():
            results['search'] = await tools.search_products(
                self.client, 'Match', 2,
            )

        self.handler = pages
        with anyio.fail_after(2):
            async with anyio.create_task_group() as group:
                group.start_soon(listing)
                group.start_soon(searching)
        self.assertEqual(results['list']['pages_fetched'], 1)
        self.assertEqual(results['search']['pages_fetched'], 1)
        self.assertEqual(self.client._max_pages, 5)
        self.assertEqual(self.client._max_results, 100)
        self.handler = lambda req: response(
            [row(str(json.loads(req.content)['page']), descricao='Match')],
            json.loads(req.content)['page'], 2,
        )
        result = await tools.search_products(self.client, 'Match', 100)
        self.assertEqual(result['pages_fetched'], 2)
        self.assertTrue(result['complete_dataset'])


class PageCapTests(ProductToolsTestCase):
    async def test_collect_page_cap_validation_and_defaults(self):
        class IntegerSubclass(int):
            pass

        for cap in (True, False, 0, 101, '1', 1.0, IntegerSubclass(1)):
            with self.assertRaises(BlockedOperationError):
                await self.client._collect(
                    'products', max_pages=cast(Any, cap),
                )
        self.assertEqual(self.requests, [])
        self.handler = lambda req: response(
            [row(str(json.loads(req.content)['page']))],
            json.loads(req.content)['page'], 2,
        )
        for kwargs, count in (({}, 2), ({'max_pages': None}, 2),
                              ({'max_pages': 1}, 1)):
            self.requests.clear()
            result = await self.client._collect(
                'products', **cast(Any, kwargs),
            )
            self.assertEqual(len(self.requests), count)
            self.assertEqual(result.partial, count == 1)
            self.assertEqual(result.complete_dataset, count == 2)
            if count == 1:
                self.assertIn('page_limit_reached', result.warnings)
        self.requests.clear()
        instance = self.make_client(max_pages=1)
        result = await instance._collect('products', max_pages=100)
        self.assertEqual(len(self.requests), 1)
        self.assertTrue(result.partial)

    async def test_concurrent_page_caps_are_isolated(self):
        ready = anyio.Event()
        started = 0
        results = {}
        original_http = self.client._http

        class Overlap(Stream):
            async def __aiter__(self):
                nonlocal started
                started += 1
                if started == 2:
                    ready.set()
                await ready.wait()
                async for chunk in super().__aiter__():
                    yield chunk

        def pages(req):
            body = json.loads(req.content)
            page = body['page']
            return httpx.Response(200, stream=Overlap(json.dumps({
                'result': [row(str(page))], 'page': page, 'totalPages': 2,
            }).encode()))

        async def collect(key, cap, budget):
            results[key] = await self.client._collect(
                'products', max_pages=cap, page_size=1, max_results=budget,
            )

        self.handler = pages
        with anyio.fail_after(2):
            async with anyio.create_task_group() as group:
                group.start_soon(collect, 'short', 1, 1)
                group.start_soon(collect, 'long', 2, 2)
        self.assertEqual(results['short'].pages_fetched, 1)
        self.assertEqual(results['long'].pages_fetched, 2)
        self.assertTrue(results['short'].partial)
        self.assertTrue(results['long'].complete_dataset)
        self.assertEqual(self.client._max_pages, 5)
        self.assertEqual(self.client._max_results, 100)
        self.assertIs(self.client._http, original_http)
