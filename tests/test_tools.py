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


class SearchProductsTests(unittest.IsolatedAsyncioTestCase):
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
        self.assertEqual(self.bodies(), [{'page': 1, 'limit': 20}])
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
        self.assertEqual(self.bodies()[-1], {'page': 1, 'limit': 20})

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
        result = await self.search(instance, 'Match', 125)
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


if __name__ == '__main__':
    unittest.main()
