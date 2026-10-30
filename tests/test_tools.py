"""Offline product search contracts through the guarded HTTP client."""

import json
from decimal import Decimal
from typing import Any, cast
import unittest
from unittest.mock import patch

import httpx

from client import NetOneClient
from test_client import Stream, response, row, settings
import tools


class ProductToolsTestCase(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        search = getattr(tools, 'search_products', None)
        if not callable(search):
            self.fail('search_products is missing')
        self.search = cast(Any, search)
        self.requests = []
        self.streams = []
        self.handler = lambda request: response([row(descricao='Match')])

        async def handle(request):
            self.requests.append(request)
            result = self.handler(request)
            self.streams.append(result.stream)
            return result

        transport_patch = patch(
            'client.httpx.AsyncHTTPTransport',
            return_value=httpx.MockTransport(handle),
        )
        transport_patch.start()
        self.addCleanup(transport_patch.stop)
        self.client = self.make_client()

    def make_client(self, **changes):
        instance = NetOneClient(settings(**changes))
        self.addAsyncCleanup(instance.aclose)
        return instance

    async def asyncTearDown(self):
        self.assertTrue(all(stream.closed for stream in self.streams))

    def bodies(self):
        return [json.loads(request.content) for request in self.requests]


class SearchProductsTests(ProductToolsTestCase):
    async def test_default_search_reaches_second_page_beyond_twenty(self):
        def pages(request):
            page = json.loads(request.content)['page']
            rows = ([row(str(i), descricao='Other') for i in range(50)]
                    if page == 1 else [row('target', descricao='Match')])
            return response(rows, page, 2, totalElements=51)

        self.handler = pages
        result = await self.search(self.client, 'Match')
        self.assertEqual([item['reduced_id'] for item in result['items']],
                         ['target'])
        self.assertEqual(self.bodies(), [
            {'page': 1, 'limit': 50}, {'page': 2, 'limit': 50},
        ])
        self.assertEqual(result['rows_received'], 51)
        self.assertEqual(result['inspection_limit'], 100)
        self.assertEqual(result['page_limit'], 5)
        self.assertEqual(result['page_size'], 50)
        self.assertEqual(result['deadline_seconds'], 60)
        self.assertEqual(result['requested_max_results'], 100)
        self.assertEqual(result['requested_max_items'], 20)
        self.assertEqual(result['matched_count'], 1)
        self.assertTrue(result['collection_complete'])
        self.assertFalse(result['output_truncated'])

    async def test_output_cut_keeps_collection_completeness_and_counts(self):
        self.handler = lambda req: response([
            row('1', descricao='Match', bloqueado=False, valor=0),
            row('2', descricao='Match'),
        ], totalElements=2)
        result = await self.search(self.client, 'Match', max_items=1)
        self.assertEqual(result['returned_count'], 1)
        self.assertEqual(result['matched_count'], 2)
        self.assertEqual(result['status'], 'partial')
        self.assertTrue(result['collection_complete'])
        self.assertTrue(result['output_truncated'])
        self.assertFalse(result['complete_dataset'])
        self.assertIn('output_limit_reached', result['warnings'])
        self.assertIs(result['items'][0]['blocked'], False)
        self.assertEqual(result['items'][0]['price'], '0')

    async def test_output_limits_validate_before_send(self):
        for value in (True, 0, 1001, None, '1', 1.0):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    await self.search(self.client, 'Match', max_items=value)
        self.assertEqual(self.requests, [])

    async def test_old_explicit_budget_and_restrictive_config_stay_bounded(self):
        self.handler = lambda req: response([
            row(str(i), descricao='Other')
            for i in range(json.loads(req.content)['limit'])
        ], 1, 2)
        for instance, kwargs, expected in (
            (self.client, {'max_results': 20}, 20),
            (self.make_client(max_results=10), {}, 10),
        ):
            result = await self.search(instance, 'Match', **kwargs)
            self.assertEqual(self.bodies()[-1], {'page': 1, 'limit': expected})
            self.assertEqual(result['inspection_limit'], expected)
            self.assertEqual(result['rows_received'], expected)
            self.assertEqual(result['returned_count'], 0)
            self.assertEqual(result['status'], 'partial')
            self.assertFalse(result['collection_complete'])

    async def test_invalid_queries_never_send_or_echo_input(self):
        invalid = (
            '', '   ', 'X' * 201, 'SECRET\n', '\tSECRET',
            'SECRET\u200b', 'SECRET\ud800', 'SECRET\ue000',
            'SECRET\u0378', None, 1, True, b'SECRET', [],
        )
        for query in invalid:
            with self.subTest(query=repr(query)):
                with self.assertRaises(ValueError) as caught:
                    await self.search(self.client, query)
                self.assertNotIn('SECRET', str(caught.exception))
                self.assertNotIn('X' * 201, str(caught.exception))
        self.assertEqual(self.requests, [])

    async def test_invalid_budgets_never_send_or_echo_input(self):
        class IntegerSubclass(int):
            pass

        for budget in (
            True, False, 0, -1, 1001, 1.0, Decimal('1'),
            'SECRET', None, IntegerSubclass(1),
        ):
            with self.subTest(budget=budget):
                with self.assertRaises(ValueError) as caught:
                    await self.search(self.client, 'Match', budget)
                self.assertNotIn('SECRET', str(caught.exception))
        self.assertEqual(self.requests, [])

    async def test_defaults_use_literal_product_route_and_closed_body(self):
        result = await self.search(self.client, '  mAtCh  ')
        self.assertEqual(result['status'], 'found')
        self.assertEqual(result['returned_count'], 1)
        self.assertEqual(self.bodies(), [{'page': 1, 'limit': 50}])
        request = self.requests[0]
        self.assertEqual(request.method, 'POST')
        self.assertEqual(request.url.host, 'example.invalid')
        self.assertEqual(
            request.url.path, '/app-web/api/v2/produto/reduzidos',
        )
        self.assertEqual(request.url.query, b'')
        self.assertNotIn('query', result)
        self.assertEqual(result['items'][0]['description'], 'Match')
        self.assertEqual(result['warnings'], ['local_text_search'])

    async def test_literal_casefold_substrings_match_each_text_field(self):
        for field in ('descricao', 'mascara', 'codigoSku'):
            with self.subTest(field=field):
                self.handler = lambda request: response([
                    row('001', **{field: '  Straße.[A]* Café  '}),
                    row('002', ean='STRASSE', grupoDescricao='STRASSE'),
                    row('003'),
                ])
                for query, count in (
                    ('STRASSE', 1), ('.[a]*', 1), ('CAFÉ', 1),
                    ('cafe', 0), ('.*', 0),
                ):
                    with self.subTest(query=query):
                        result = await self.search(self.client, query)
                        self.assertEqual(result['returned_count'], count)
                        self.assertEqual(
                            result['status'],
                            'found' if count else 'not_found',
                        )
                        if count:
                            key = {
                                'descricao': 'description',
                                'mascara': 'product_mask', 'codigoSku': 'sku',
                            }[field]
                            self.assertEqual(
                                result['items'][0][key],
                                '  Straße.[A]* Café  ',
                            )

    async def test_query_length_boundaries_and_unicode_space(self):
        for query in ('x', 'x' * 200, '\u00a0Match\u00a0'):
            with self.subTest(length=len(query)):
                result = await self.search(self.client, query)
                self.assertIn(result['status'], ('found', 'not_found'))
                if query == '\u00a0Match\u00a0':
                    self.assertEqual(result['status'], 'found')
                    self.assertEqual(result['returned_count'], 1)
                    self.assertEqual(
                        result['items'][0]['description'], 'Match',
                    )
        self.assertEqual(len(self.requests), 3)

    async def test_budgets_are_capped_by_config_without_mutation(self):
        for budget, configured, expected in (
            (1, 100, 1), (1000, 100, 50), (1000, 2, 2),
        ):
            instance = self.make_client(max_results=configured, max_pages=1)
            self.handler = lambda request: response([
                row(str(index)) for index in range(expected)
            ], 1, 2)
            result = await self.search(instance, 'Match', budget)
            self.assertEqual(self.bodies()[-1], {'page': 1, 'limit': expected})
            self.assertTrue(result['partial'])
            self.assertEqual(instance._max_results, configured)
        self.handler = lambda request: response([row(descricao='Match')])
        await self.search(self.client, 'Match')
        self.assertEqual(self.bodies()[-1], {'page': 1, 'limit': 50})

    async def test_budget_counts_nonmatches_and_stops_first_page(self):
        self.handler = lambda request: response([
            row('001', descricao='Other'), row('002', descricao='Match'),
        ], 1, 2, totalElements=4)
        result = await self.search(self.client, 'Match', 2)
        self.assertEqual(self.bodies(), [{'page': 1, 'limit': 2}])
        self.assertEqual(result['rows_received'], 2)
        self.assertEqual(result['returned_count'], 1)
        self.assertEqual(result['status'], 'partial')
        self.assertIn('result_limit_reached', result['warnings'])
        self.assertFalse(result['complete_dataset'])

    async def test_fixed_pages_do_not_spend_leftover_budget(self):
        def pages(request):
            page = json.loads(request.content)['page']
            return response([
                row(f'{page}-{index}', descricao='Match' if index else 'Other')
                for index in range(50)
            ], page, 3, totalElements=150)

        self.handler = pages
        instance = self.make_client(max_results=200)
        result = await self.search(instance, 'Match', 125, max_items=1000)
        self.assertEqual(self.bodies(), [
            {'page': 1, 'limit': 50}, {'page': 2, 'limit': 50},
        ])
        self.assertEqual(result['returned_count'], 98)
        self.assertEqual(result['rows_received'], 100)
        self.assertFalse(result['complete_dataset'])
        self.assertIn('result_limit_reached', result['warnings'])

    async def test_page_limit_preserves_partial_without_matches(self):
        instance = self.make_client(max_pages=1)
        self.handler = lambda request: response([row(descricao='Other')], 1, 2)
        result = await self.search(instance, 'Match')
        self.assertEqual(result['status'], 'partial')
        self.assertEqual(result['returned_count'], 0)
        self.assertFalse(result['complete_dataset'])
        self.assertIn('page_limit_reached', result['warnings'])

    async def test_missing_metadata_remains_partial_without_matches(self):
        self.handler = lambda request: httpx.Response(
            200, stream=Stream(b'{"result": []}'),
        )
        result = await self.search(self.client, 'Match')
        self.assertEqual(result['status'], 'partial')
        self.assertEqual(result['warnings'], [
            'pagination_metadata_missing', 'local_text_search',
        ])

    async def test_complete_found_and_not_found_preserve_metadata(self):
        self.handler = lambda request: response([
            row(descricao='Match', ultimaAlteracaoTimestamp='raw-time'),
        ], totalElements=1)
        for query, status, count in (
            ('Match', 'found', 1), ('absent', 'not_found', 0),
        ):
            with self.subTest(query=query):
                result = await self.search(self.client, query)
                self.assertEqual(result['status'], status)
                self.assertEqual(result['returned_count'], count)
                self.assertFalse(result['partial'])
                self.assertTrue(result['complete_dataset'])
                self.assertIsNone(result['error'])
                self.assertEqual(result['source'], 'netone_api')
                self.assertEqual(result['operation'], 'products')
                self.assertIsInstance(result['retrieved_at'], str)
                self.assertEqual(result['pages_fetched'], 1)
                self.assertEqual(result['rows_received'], 1)
                self.assertEqual(result['total_pages'], 1)
                self.assertEqual(result['total_elements'], 1)
                self.assertEqual(result['warnings'], [
                    'timestamp_semantics_unverified', 'local_text_search',
                ])
                json.dumps(result, allow_nan=False)

    async def test_empty_complete_dataset_is_not_found(self):
        self.handler = lambda request: response([], totalElements=0)
        result = await self.search(self.client, 'Match')
        self.assertEqual(result['status'], 'not_found')
        self.assertEqual(result['returned_count'], 0)
        self.assertTrue(result['complete_dataset'])

    async def test_errors_before_and_after_rows_keep_error_and_status(self):
        cases = (
            (401, 'authentication_error'), (403, 'authorization_error'),
            (404, 'not_found'), (500, 'upstream_error'), (None, 'timeout'),
        )
        for code, error in cases:
            for preceding in (None, 'Other', 'Match'):
                with self.subTest(code=code, preceding=preceding):
                    self.requests.clear()

                    def pages(request):
                        page = json.loads(request.content)['page']
                        if preceding is not None and page == 1:
                            return response([row(descricao=preceding)], 1, 2)
                        if code is None:
                            raise httpx.ReadTimeout('SECRET')
                        return httpx.Response(code, stream=Stream(b'SECRET'))

                    self.handler = pages
                    result = await self.search(self.client, 'Match', 100)
                    self.assertEqual(result['error'], error)
                    self.assertEqual(
                        result['status'],
                        'error' if preceding is None else 'partial',
                    )
                    self.assertEqual(
                        result['returned_count'], int(preceding == 'Match'),
                    )
                    self.assertTrue(result['partial'])
                    self.assertFalse(result['complete_dataset'])
                    self.assertIn('collection_interrupted', result['warnings'])
                    self.assertIn('local_text_search', result['warnings'])
                    self.assertEqual(
                        len(self.requests), 1 if preceding is None else 2,
                    )
                    self.assertEqual(
                        result['rows_received'],
                        0 if preceding is None else 1,
                    )
                    self.assertNotIn('SECRET', json.dumps(result))

    async def test_decimal_null_zero_and_identifiers_stay_exact(self):
        self.handler = lambda request: httpx.Response(200, stream=Stream(
            b'{"result":[{"idProduto":"0001","idReduzido":"0002",'
            b'"descricao":" Match ","mascara":null,"codigoSku":"0003",'
            b'"valor":0.123456789012345678901,"quantidade":0}],'
            b'"page":1,"totalPages":1,"totalElements":1}'
        ))
        result = await self.search(self.client, 'match')
        item = result['items'][0]
        self.assertEqual(item['product_id'], '0001')
        self.assertEqual(item['reduced_id'], '0002')
        self.assertEqual(item['sku'], '0003')
        self.assertEqual(item['description'], ' Match ')
        self.assertEqual(item['price'], '0.123456789012345678901')
        self.assertEqual(item['quantity'], '0')
        self.assertIsNone(item['product_mask'])
        self.assertNotIn('mascara', item['missing_fields'])
        self.assertIn('ean', item['missing_fields'])
        json.dumps(result, allow_nan=False)

    async def test_duplicates_count_budget_and_conflicts_stay_partial(self):
        self.handler = lambda request: response([
            row(descricao='Match'), row(descricao='Match'),
            row(descricao='Match changed'), row('002', descricao='Other'),
        ], totalElements=4)
        result = await self.search(self.client, 'Match', 4)
        self.assertEqual(result['rows_received'], 4)
        self.assertEqual(result['returned_count'], 2)
        self.assertEqual(result['status'], 'partial')
        self.assertFalse(result['complete_dataset'])
        self.assertEqual(result['warnings'], [
            'duplicate_rows_removed', 'conflicting_rows_preserved',
            'local_text_search',
        ])
        self.assertEqual(
            [item['description'] for item in result['items']],
            ['Match', 'Match changed'],
        )
        result = await self.search(self.client, 'absent', 4)
        self.assertEqual(result['status'], 'partial')
        self.assertEqual(result['returned_count'], 0)


class ExactProductToolsTests(ProductToolsTestCase):
    def lookup(self, name):
        function = getattr(tools, name, None)
        self.assertTrue(callable(function), f'{name} is missing')
        return cast(Any, function)

    def cases(self):
        return (
            ('get_product_details', 7, None, None),
            ('search_product_by_sku', '00-Ab', 'codigoSku',
             'local_exact_sku_search'),
            ('search_product_by_ean', '000123', 'ean',
             'local_exact_ean_search'),
        )

    def matching_row(self, field, value, reduced='001', **extra):
        code = {field: value} if field else {}
        return row(reduced, idProduto=7, **code, **extra)

    async def test_details_filters_id_and_preserves_all_reduced_rows(self):
        self.handler = lambda request: response([
            row('0002', idProduto=7), row('0003', idProduto=7),
        ], totalElements=2)
        result = await self.lookup('get_product_details')(self.client, 7)
        self.assertEqual(self.bodies(), [
            {'page': 1, 'limit': 20, 'idsProdutos': [7]},
        ])
        self.assertEqual(result['status'], 'found')
        self.assertEqual(result['returned_count'], 2)
        self.assertEqual(
            [item['reduced_id'] for item in result['items']],
            ['0002', '0003'],
        )
        self.assertEqual(result['warnings'], [])
        self.assertNotIn('product_id', result)

    async def test_codes_match_only_exact_designated_field(self):
        for name, value, field, warning in self.cases()[1:]:
            with self.subTest(name=name):
                self.requests.clear()
                alternatives = (
                    ('00-ab', 'Ab', '00-Ab-extra') if field == 'codigoSku'
                    else ('123', 'x000123', '0001234')
                )
                self.handler = lambda request: response([
                    self.matching_row(field, value),
                    *[self.matching_row(field, code, str(index))
                      for index, code in enumerate(alternatives, 2)],
                    row('005', descricao=value, mascara=value,
                        **({'ean': value} if field == 'codigoSku'
                           else {'codigoSku': value})),
                    row('006', **{field: None}), row('007'),
                ], totalElements=7)
                result = await self.lookup(name)(self.client, value)
                self.assertEqual(result['status'], 'found')
                self.assertEqual(result['returned_count'], 1)
                self.assertEqual(result['items'][0]['reduced_id'], '001')
                self.assertEqual(result['rows_received'], 7)
                self.assertEqual(result['warnings'], [warning])
                self.assertEqual(self.bodies(), [{'page': 1, 'limit': 20}])
                self.assertNotIn('query', result)
                self.assertNotIn(field, result)

    async def test_code_boundaries_and_significant_spaces_are_exact(self):
        for name, _, field, _ in self.cases()[1:]:
            for value in ('x', 'x' * 256, ' 00-Ab ', '\u00a0000123\u00a0'):
                with self.subTest(name=name, length=len(value)):
                    self.handler = lambda request: response([
                        self.matching_row(field, value),
                        self.matching_row(field, value.strip(), '002'),
                    ])
                    result = await self.lookup(name)(self.client, value)
                    expected = 2 if value == value.strip() else 1
                    self.assertEqual(result['returned_count'], expected)
                    key = 'sku' if field == 'codigoSku' else 'ean'
                    self.assertEqual(result['items'][0][key], value)

    async def test_all_invalid_inputs_and_budgets_never_send_or_echo(self):
        class IntegerSubclass(int):
            pass

        invalid_codes = (
            '', ' ', '\u00a0', 'x' * 257, 'SECRET' * 43, 'SECRET\n',
            '\tSECRET', 'SECRET\u200b', 'SECRET\ud800',
            'SECRET\ue000', 'SECRET\u0378', None, True, False,
            7, 1.0, Decimal('1'), b'SECRET', [], {},
        )
        invalid_ids = (
            -1, 9223372036854775808, True, False, 7.0, Decimal('7'),
            '007', 'SECRET', None, IntegerSubclass(7),
        )
        invalid_budgets = (
            True, False, 0, -1, 1001, 1.0, Decimal('1'),
            'SECRET', None, IntegerSubclass(1),
        )
        for name, valid, field, _ in self.cases():
            function = self.lookup(name)
            for value in invalid_codes if field else invalid_ids:
                for budget in (20, 'SECRET'):
                    with self.subTest(name=name, value=repr(value)):
                        with self.assertRaises(ValueError) as caught:
                            await function(self.client, value, budget)
                        self.assertNotIn('SECRET', str(caught.exception))
                        self.assertNotIn('007', str(caught.exception))
            for budget in invalid_budgets:
                with self.subTest(name=name, budget=repr(budget)):
                    with self.assertRaises(ValueError) as caught:
                        await function(self.client, valid, budget)
                    self.assertNotIn('SECRET', str(caught.exception))
        self.assertEqual(self.requests, [])

    async def test_details_accepts_integer_endpoints_without_coercion(self):
        for value in (0, 9223372036854775807):
            self.handler = lambda request: response([
                row(idProduto=value),
            ])
            result = await self.lookup('get_product_details')(
                self.client, value,
            )
            self.assertEqual(result['status'], 'found')
            self.assertEqual(result['items'][0]['product_id'], str(value))
            self.assertEqual(self.bodies()[-1]['idsProdutos'], [value])

    async def test_details_rejects_mixed_identity_page_atomically(self):
        self.handler = lambda request: response([
            row('001', idProduto=7), row('002', idProduto=8),
        ])
        result = await self.lookup('get_product_details')(self.client, 7)
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['error'], 'invalid_response')
        self.assertEqual(result['items'], [])

    async def test_complete_metadata_and_empty_terminal_are_preserved(self):
        for name, value, field, warning in self.cases():
            for matched in (False, True):
                with self.subTest(name=name, matched=matched):
                    rows = [self.matching_row(field, value)] if matched else []
                    self.handler = lambda request: response(
                        rows, totalElements=len(rows),
                    )
                    result = await self.lookup(name)(self.client, value)
                    self.assertEqual(
                        result['status'], 'found' if matched else 'not_found',
                    )
                    self.assertEqual(result['returned_count'], int(matched))
                    self.assertEqual(result['rows_received'], int(matched))
                    self.assertEqual(result['pages_fetched'], 1)
                    self.assertEqual(result['total_pages'], 1)
                    self.assertEqual(result['total_elements'], int(matched))
                    self.assertEqual(result['operation'], 'products')
                    self.assertEqual(result['source'], 'netone_api')
                    self.assertIsInstance(result['retrieved_at'], str)
                    self.assertTrue(result['complete_dataset'])
                    self.assertFalse(result['partial'])
                    self.assertIsNone(result['error'])
                    self.assertEqual(
                        result['warnings'], [warning] if warning else [],
                    )
                    json.dumps(result, allow_nan=False)

    async def test_cap_duplicate_and_nonmatch_rows_consume_budget(self):
        for name, value, field, warning in self.cases():
            self.requests.clear()
            instance = self.make_client(max_results=3)
            matched = self.matching_row(field, value)
            other = self.matching_row(field, 'other', '002')
            self.handler = lambda request: response(
                [matched, matched, other], 1, 2, totalElements=6,
            )
            result = await self.lookup(name)(instance, value, 1000)
            body: dict[str, object] = {'page': 1, 'limit': 3}
            if not field:
                body['idsProdutos'] = [7]
            self.assertEqual(self.bodies(), [body])
            self.assertEqual(result['rows_received'], 3)
            self.assertEqual(result['returned_count'], 1 if field else 2)
            self.assertEqual(result['status'], 'partial')
            self.assertFalse(result['complete_dataset'])
            self.assertIn('duplicate_rows_removed', result['warnings'])
            self.assertIn('result_limit_reached', result['warnings'])
            self.assertEqual(instance._max_results, 3)

    async def test_fixed_pages_keep_filter_and_budget_per_call(self):
        for name, value, field, _ in self.cases():
            self.requests.clear()

            def pages(request):
                page = json.loads(request.content)['page']
                return response([
                    self.matching_row(field, value, f'{page}-{index}')
                    for index in range(50)
                ], page, 3, totalElements=150)

            self.handler = pages
            instance = self.make_client(max_results=200)
            result = await self.lookup(name)(instance, value, 125)
            bodies: list[dict[str, object]] = [
                {'page': 1, 'limit': 50}, {'page': 2, 'limit': 50},
            ]
            if not field:
                for body in bodies:
                    body['idsProdutos'] = [7]
            self.assertEqual(self.bodies(), bodies)
            self.assertEqual(result['rows_received'], 100)
            self.assertEqual(result['returned_count'], 100)
            self.assertEqual(result['status'], 'partial')
            self.assertIn('result_limit_reached', result['warnings'])
            self.handler = lambda request: response([])
            await self.lookup(name)(instance, value)
            self.assertEqual(self.bodies()[-1]['limit'], 20)

    async def test_page_limit_and_missing_metadata_cannot_claim_absence(self):
        for name, value, field, warning in self.cases():
            for metadata in (False, True):
                self.requests.clear()
                instance = self.make_client(max_pages=1)
                self.handler = lambda request: (
                    response([
                        self.matching_row(field, 'other'),
                    ], 1, 2) if metadata else
                    httpx.Response(200, stream=Stream(b'{"result":[]}'))
                )
                result = await self.lookup(name)(instance, value)
                self.assertEqual(result['status'], 'partial')
                self.assertEqual(
                    result['returned_count'], int(metadata and not field),
                )
                self.assertFalse(result['complete_dataset'])
                expected = ('page_limit_reached' if metadata
                            else 'pagination_metadata_missing')
                self.assertIn(expected, result['warnings'])
                if warning:
                    self.assertIn(warning, result['warnings'])

    async def test_initial_and_later_errors_override_found_or_absence(self):
        errors = (
            (401, 'authentication_error'), (403, 'authorization_error'),
            (404, 'not_found'), (429, 'rate_limited'),
            (500, 'upstream_error'), (None, 'timeout'),
        )
        for name, value, field, warning in self.cases():
            for code, error in errors:
                for preceding in (None, False, True):
                    # Details can only retain matching product identities.
                    if not field and preceding is False:
                        continue
                    with self.subTest(name=name, code=code, prior=preceding):
                        self.requests.clear()

                        def pages(request):
                            page = json.loads(request.content)['page']
                            if preceding is not None and page == 1:
                                data = self.matching_row(
                                    field, value if preceding else 'other',
                                )
                                return response([data], 1, 2)
                            if code is None:
                                raise httpx.ReadTimeout('SECRET')
                            return httpx.Response(
                                code, stream=Stream(b'SECRET'),
                            )

                        self.handler = pages
                        result = await self.lookup(name)(
                            self.client, value, 100,
                        )
                        self.assertEqual(result['error'], error)
                        self.assertEqual(
                            result['status'],
                            'error' if preceding is None else 'partial',
                        )
                        self.assertEqual(
                            result['returned_count'], int(preceding is True),
                        )
                        self.assertEqual(
                            result['rows_received'],
                            0 if preceding is None else 1,
                        )
                        self.assertEqual(
                            len(self.requests),
                            1 if preceding is None else 2,
                        )
                        self.assertTrue(result['partial'])
                        self.assertFalse(result['complete_dataset'])
                        self.assertIn(
                            'collection_interrupted', result['warnings'],
                        )
                        if warning:
                            self.assertIn(warning, result['warnings'])
                        self.assertNotIn('SECRET', json.dumps(result))

    async def test_decimal_json_null_absence_and_identifiers_stay_exact(self):
        self.handler = lambda request: httpx.Response(200, stream=Stream(
            b'{"result":[{"idProduto":7,"idReduzido":"0002",'
            b'"codigoSku":"00-Ab","ean":"000123","mascara":null,'
            b'"valor":0.123456789012345678901,"quantidade":0}],'
            b'"page":1,"totalPages":1,"totalElements":1}'
        ))
        for name, value, _, _ in self.cases():
            result = await self.lookup(name)(self.client, value)
            item = result['items'][0]
            self.assertEqual(item['product_id'], '7')
            self.assertEqual(item['reduced_id'], '0002')
            self.assertEqual(item['sku'], '00-Ab')
            self.assertEqual(item['ean'], '000123')
            self.assertEqual(item['price'], '0.123456789012345678901')
            self.assertEqual(item['quantity'], '0')
            self.assertIsNone(item['product_mask'])
            self.assertNotIn('mascara', item['missing_fields'])
            self.assertIsNone(item['description'])
            self.assertIn('descricao', item['missing_fields'])
            json.dumps(result, allow_nan=False)


if __name__ == '__main__':
    unittest.main()
