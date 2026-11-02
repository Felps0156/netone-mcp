"""Deterministic analyses using explicitly synthetic commercial records."""

from decimal import Decimal
import importlib
import importlib.util
import json
from typing import Any, cast
import unittest
from unittest.mock import patch

import anyio
import httpx

from catalog import normalize_record
from test_client import Stream, response, row, settings
from test_tools import ProductToolsTestCase
import tools


class AnalysisMetricsTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(importlib.util.find_spec('analysis'),
                             'analysis module is missing')
        self.analysis = importlib.import_module('analysis')

    def universe(self, rows, operation='stock'):
        return self.analysis.prepare_universe(tuple(
            normalize_record(operation, row) for row in rows
        ))

    def test_identity_conflicts_exclude_whole_group_without_losing_zeros(self):
        universe = self.universe([
            {'idReduzido': '01', 'quantidade': 1},
            {'idReduzido': '01', 'quantidade': 1},
            {'idReduzido': '1', 'quantidade': 2},
            {'idProduto': 'A', 'idReduzido': 'bad', 'quantidade': 3},
            {'idProduto': 'B', 'idReduzido': 'bad', 'quantidade': 3},
        ])
        self.assertEqual([r.reduced_id for r in universe.records], ['01', '1'])
        self.assertEqual(universe.distinct_reduced_ids, 3)
        self.assertEqual(universe.conflicting_identity_count, 1)
        self.assertEqual(universe.duplicate_records_excluded, 1)
        with self.assertRaises(AttributeError):
            universe.records = ()

    def test_presence_conflicts_do_not_collapse_distinct_variants(self):
        universe = self.universe([
            {'idProduto': 'P', 'idReduzido': 'a', 'quantidade': None},
            {'idProduto': 'P', 'idReduzido': 'a'},
            {'idProduto': 'P', 'idReduzido': 'b', 'quantidade': 1},
            {'idProduto': 'P', 'idReduzido': 'c', 'quantidade': 1},
        ])
        self.assertEqual(len(universe.records), 2)
        self.assertEqual(universe.conflicting_identity_count, 1)

    def test_repeated_nonfirst_conflict_is_still_a_duplicate(self):
        universe = self.universe([
            {'idReduzido': 'a', 'quantidade': 1},
            {'idReduzido': 'a', 'quantidade': 2},
            {'idReduzido': 'a', 'quantidade': 2},
        ])
        self.assertEqual(universe.records, ())
        self.assertEqual(universe.conflicting_identity_count, 1)
        self.assertEqual(universe.duplicate_records_excluded, 1)

    def test_threshold_rejects_coercion_and_unbounded_representation(self):
        class IntegerSubclass(int):
            pass

        for value in (True, False, 'SECRET', 1.0, None, -1,
                      IntegerSubclass(1), Decimal('NaN'), Decimal('sNaN'),
                      Decimal('Infinity'), Decimal('-0.01'),
                      Decimal('1e101'), Decimal('0e-101'),
                      Decimal('9' * 101), 10 ** 100, 10 ** 5000):
            with self.subTest(kind=type(value).__name__):
                with self.assertRaises(ValueError) as caught:
                    self.analysis.validate_threshold(value)
                self.assertNotIn('SECRET', str(caught.exception))
        for value in (0, 3, Decimal('3.00'), Decimal('1e100'),
                      Decimal('1e-100'), Decimal('9' * 100)):
            self.assertEqual(self.analysis.validate_threshold(value), value)

    def test_inventory_counts_known_quantities_without_summing_units(self):
        universe = self.universe([
            {'idReduzido': 'a', 'quantidade': Decimal('3')},
            {'idReduzido': 'b',
             'quantidade': Decimal('3.000000000000000000001')},
            {'idReduzido': 'c', 'quantidade': 0},
            {'idReduzido': 'd', 'quantidade': -2},
            {'idReduzido': 'e', 'quantidade': None},
            {'idReduzido': 'f'},
        ])
        self.assertEqual(self.analysis.inventory_metrics(universe, Decimal(3)),
                         {
            'known_quantity_count': 4, 'unknown_quantity_count': 2,
            'null_quantity_count': 1, 'absent_quantity_count': 1,
            'low_stock_count': 3, 'zero_quantity_count': 1,
            'negative_quantity_count': 1, 'above_threshold_count': 1,
        })
        zero = self.analysis.inventory_metrics(universe, Decimal(0))
        self.assertEqual(zero['low_stock_count'], 2)
        self.assertEqual(zero['above_threshold_count'], 2)

    def test_catalog_presence_classification_has_no_sentinel_collision(self):
        universe = self.universe([
            {'idProduto': '01', 'idReduzido': 'a', 'mascara': '001',
             'descricao': 'A', 'codigoSku': '000', 'ean': '0001',
             'grupoDescricao': 'null', 'linhaDescricao': 'L',
             'subgrupoDescricao': 'S', 'bloqueado': False, 'quantidade': 99},
            {'idProduto': '01', 'idReduzido': 'b', 'mascara': None,
             'descricao': None, 'codigoSku': None, 'ean': None,
             'grupoDescricao': None, 'bloqueado': None},
            {'idProduto': '1', 'idReduzido': 'c', 'mascara': ' ',
             'descricao': '\t', 'codigoSku': '', 'ean': ' ',
             'grupoDescricao': ' ', 'bloqueado': True},
            {'idProduto': 'other', 'idReduzido': 'd'},
        ], 'products')
        metrics = self.analysis.catalog_metrics(universe)
        self.assertEqual(metrics['distinct_product_count'], 3)
        for field in ('product_mask', 'description', 'sku', 'ean'):
            self.assertEqual(metrics['field_presence'][field], {
                'populated': 1, 'null': 1, 'blank': 1, 'absent': 1,
            })
        self.assertEqual(metrics['blocked_counts'], {
            'true': 1, 'false': 1, 'unknown': 2, 'null': 1, 'absent': 1,
        })
        self.assertEqual(metrics['classifications']['group'], {
            'values': [{'value': 'null', 'count': 1}],
            'absent': 1, 'null': 1, 'blank': 1,
        })
        self.assertEqual(metrics['classifications']['subgroup']['values'],
                         [{'value': 'S', 'count': 1}])
        self.assertEqual(metrics['classifications']['line']['absent'], 3)
        self.assertNotIn('low_stock_count', metrics)

    def test_empty_metrics_use_zero_counts_not_invented_records(self):
        universe = self.universe([])
        self.assertEqual(self.analysis.inventory_metrics(
            universe, Decimal(3))['unknown_quantity_count'], 0)
        self.assertEqual(self.analysis.catalog_metrics(
            universe)['distinct_product_count'], 0)


class AnalysisApplicationTests(ProductToolsTestCase):
    def function(self, name):
        function = getattr(tools, name, None)
        self.assertTrue(callable(function), f'{name} is missing')
        return cast(Any, function)

    async def test_inventory_default_threshold_three_and_source_fidelity(self):
        function = self.function('analyze_inventory')
        self.handler = lambda req: httpx.Response(200, stream=Stream(
            b'{"result":[{"idReduzido":"01","quantidade":3.0000},'
            b'{"idReduzido":"1","quantidade":3.000000000000000000001},'
            b'{"idReduzido":"zero","quantidade":0,"bloqueado":false},'
            b'{"idReduzido":"null","quantidade":null},'
            b'{"idReduzido":"absent"}],'
            b'"page":1,"totalPages":1,"totalElements":5}'
        ))
        result = await function(self.client)
        self.assertEqual(result['threshold'], '3')
        self.assertEqual(result['metrics']['low_stock_count'], 2)
        self.assertEqual(result['metrics']['unknown_quantity_count'], 2)
        self.assertEqual(result['records_analyzed'], 5)
        self.assertEqual(result['source_record_count'], 5)
        self.assertEqual(result['returned_count'], 5)
        self.assertEqual(result['items'][0]['quantity'], '3.0000')
        self.assertEqual(result['items'][1]['reduced_id'], '1')
        self.assertIs(result['items'][2]['blocked'], False)
        self.assertNotIn('quantidade', result['items'][3]['missing_fields'])
        self.assertIn('quantidade', result['items'][4]['missing_fields'])
        self.assertTrue(result['complete_dataset'])
        self.assertTrue(result['collection_complete'])
        self.assertFalse(result['metrics_complete'])
        self.assertEqual(result['analysis_scope'], 'visible_endpoint')
        self.assertEqual(result['source'], 'netone_api')
        self.assertEqual(result['status'], 'found')
        self.assertEqual(result['inventory_scope']['deposit_id'], None)
        self.assertIn('inventory_freshness_unverified', result['warnings'])
        self.assertEqual(self.bodies(), [{'page': 1, 'limit': 50}])
        self.assertEqual(self.requests[0].url.path,
                         '/app-web/api/v2/produto/estoque')
        self.assertEqual(result['page_limit'], 1)
        self.assertEqual(result['criteria']['low_stock'],
                         'known quantity <= threshold')
        json.dumps(result, allow_nan=False)

    async def test_catalog_does_not_treat_product_quantity_as_stock(self):
        function = self.function('analyze_product_catalog')
        self.handler = lambda req: response([
            row('a', descricao='Synthetic', quantidade=0, bloqueado=False),
            row('b', descricao=None),
        ], totalElements=2)
        result = await function(self.client)
        self.assertEqual(result['records_analyzed'], 2)
        self.assertEqual(result['metrics']['distinct_product_count'], 1)
        self.assertEqual(result['metrics']['field_presence']['description'],
                         {'populated': 1, 'null': 1, 'absent': 0, 'blank': 0})
        self.assertEqual(result['analysis_type'], 'product_catalog')
        self.assertIsNone(result['threshold'])
        self.assertNotIn('low_stock_count', result['metrics'])
        self.assertTrue(result['metrics_complete'])
        self.assertEqual(self.requests[0].url.path,
                         '/app-web/api/v2/produto/reduzidos')

    async def test_analysis_inputs_rejected_before_send(self):
        inventory = self.function('analyze_inventory')
        catalog = self.function('analyze_product_catalog')
        for function in (inventory, catalog):
            for name, values in (
                ('max_results', (True, 0, 1001, None, '1', 1.0)),
                ('max_pages', (True, 0, 101, None, '1', 1.0)),
            ):
                for value in values:
                    with self.assertRaises(ValueError):
                        await function(self.client, **{name: value})
        for value in (True, 'SECRET', 1.0, None, -1, Decimal('sNaN'),
                      Decimal('Infinity'), Decimal('1e101'), 10 ** 5000):
            with self.assertRaises(ValueError):
                await inventory(self.client, threshold=value)
        self.assertEqual(self.requests, [])

    async def test_budgets_pages_and_threshold_are_per_call(self):
        function = self.function('analyze_inventory')

        def pages(req):
            page = json.loads(req.content)['page']
            return response([row(str(page), quantidade=3)], page, 2)

        self.handler = pages
        result = await function(self.client)
        self.assertEqual(len(self.requests), 1)
        self.assertEqual(result['analysis_scope'], 'sample')
        self.assertFalse(result['complete_dataset'])
        self.assertIn('page_limit_reached', result['warnings'])
        self.requests.clear()
        result = await function(self.client, max_results=100,
                                max_pages=2, threshold=Decimal('2.00'))
        self.assertEqual(self.bodies(), [
            {'page': 1, 'limit': 50}, {'page': 2, 'limit': 50},
        ])
        self.assertEqual(result['metrics']['low_stock_count'], 0)
        self.assertEqual(result['threshold'], '2.00')
        self.assertTrue(result['complete_dataset'])
        self.requests.clear()
        restrictive = self.make_client(max_results=1, max_pages=1)
        result = await function(restrictive, max_results=1000, max_pages=100)
        self.assertEqual(self.bodies(), [{'page': 1, 'limit': 1}])
        self.assertEqual(result['inspection_limit'], 1)
        self.assertEqual(result['page_limit'], 1)
        self.assertEqual(self.client._max_results, 100)

    async def test_conflicts_and_duplicates_never_inflate_metrics(self):
        function = self.function('analyze_inventory')
        self.handler = lambda req: response([
            row('a', quantidade=1), row('a', quantidade=1),
            row('b', quantidade=2), row('b', quantidade=3),
            row('c', idProduto='P'), row('c', idProduto='Q'),
        ])
        result = await function(self.client)
        self.assertEqual(result['rows_received'], 6)
        self.assertEqual(result['source_record_count'], 5)
        self.assertEqual(result['records_analyzed'], 1)
        self.assertEqual(result['distinct_reduced_ids'], 3)
        self.assertEqual(result['conflicting_identity_count'], 2)
        self.assertEqual(result['metrics']['low_stock_count'], 1)
        self.assertFalse(result['complete_dataset'])
        self.assertFalse(result['metrics_complete'])
        self.assertEqual(result['status'], 'partial')
        self.assertEqual(result['analysis_scope'], 'sample')
        self.assertEqual(result['returned_count'], 5)

    async def test_valid_empty_remains_not_found(self):
        for name in ('analyze_inventory', 'analyze_product_catalog'):
            function = self.function(name)
            self.handler = lambda req: response([], totalElements=0)
            result = await function(self.client)
            self.assertEqual(result['status'], 'not_found')
            self.assertEqual(result['records_analyzed'], 0)
            self.assertTrue(result['complete_dataset'])
            self.assertTrue(result['metrics_complete'])

    async def test_collector_removed_duplicates_prevent_global_analysis(self):
        function = self.function('analyze_inventory')
        self.handler = lambda req: response([
            row(quantidade=2), row(quantidade=2),
        ])
        result = await function(self.client)
        self.assertFalse(result['collection_complete'])
        self.assertFalse(result['complete_dataset'])
        self.assertEqual(result['records_analyzed'], 1)
        self.assertEqual(result['duplicate_records_excluded'], 0)
        self.assertEqual(result['status'], 'partial')
        self.assertIn('analysis_universe_incomplete', result['warnings'])

    async def test_errors_preserve_prior_metrics_and_safe_error_codes(self):
        for name in ('analyze_inventory', 'analyze_product_catalog'):
            function = self.function(name)
            for code, expected in (
                (401, 'authentication_error'), (403, 'authorization_error'),
                (404, 'not_found'), (429, 'rate_limited'),
                (500, 'upstream_error'), (None, 'timeout'),
            ):
                for prior in (False, True):
                    self.requests.clear()

                    def pages(req):
                        page = json.loads(req.content)['page']
                        if prior and page == 1:
                            return response([row(quantidade=0)], 1, 2)
                        if code is None:
                            raise httpx.ReadTimeout('SECRET')
                        return httpx.Response(code, stream=Stream(b'SECRET'))

                    self.handler = pages
                    result = await function(self.client, max_pages=2)
                    self.assertEqual(result['error'], expected)
                    self.assertEqual(result['status'],
                                     'partial' if prior else 'error')
                    self.assertEqual(result['records_analyzed'], int(prior))
                    self.assertEqual(len(self.requests), 2 if prior else 1)
                    self.assertFalse(result['complete_dataset'])
                    self.assertEqual(result['analysis_scope'], 'sample')
                    self.assertNotIn('SECRET', json.dumps(result))

    async def test_metadata_and_repeated_pages_remain_samples(self):
        for name in ('analyze_inventory', 'analyze_product_catalog'):
            function = self.function(name)
            for payload, error, analyzed in (
                (b'{"result":[]}', None, 0),
                (b'{"result":[],"page":1,"totalPages":1,'
                 b'"totalElements":1}', 'invalid_response', 0),
                (b'{"result":[{"idProduto":"1","idReduzido":"a"}]}',
                 None, 1),
            ):
                self.handler = lambda req: httpx.Response(
                    200, stream=Stream(payload))
                result = await function(self.client)
                self.assertFalse(result['complete_dataset'])
                self.assertEqual(result['error'], error)
                self.assertEqual(result['records_analyzed'], analyzed)
                self.assertEqual(result['analysis_scope'], 'sample')
            self.handler = lambda req: response(
                [row()], json.loads(req.content)['page'], 2)
            result = await function(self.client, max_pages=2)
            self.assertEqual(result['records_analyzed'], 1)
            self.assertIn('pagination_no_progress', result['warnings'])
            self.assertFalse(result['complete_dataset'])

    async def test_all_conflicting_identities_are_not_not_found(self):
        for name in ('analyze_inventory', 'analyze_product_catalog'):
            function = self.function(name)
            self.handler = lambda req: response([
                row(quantidade=1), row(quantidade=2),
            ])
            result = await function(self.client)
            self.assertEqual(result['status'], 'partial')
            self.assertEqual(result['records_analyzed'], 0)
            self.assertEqual(result['returned_count'], 2)
            self.assertEqual(result['conflicting_identity_count'], 1)
            self.assertFalse(result['metrics_complete'])

    async def test_concurrent_thresholds_and_budgets_do_not_share_state(self):
        function = self.function('analyze_inventory')
        ready = anyio.Event()
        started = 0
        outputs = {}

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
                'result': [row(str(page), quantidade=3)],
                'page': page, 'totalPages': 2,
            }).encode()))

        async def analyze(key, threshold, cap, page_cap):
            outputs[key] = await function(
                self.client, threshold=threshold,
                max_results=cap, max_pages=page_cap,
            )

        self.handler = pages
        with anyio.fail_after(2):
            async with anyio.create_task_group() as group:
                group.start_soon(analyze, 'short', 2, 1, 1)
                group.start_soon(analyze, 'long', 3, 100, 2)
        self.assertEqual(outputs['short']['metrics']['low_stock_count'], 0)
        self.assertEqual(outputs['long']['metrics']['low_stock_count'], 2)
        self.assertEqual(outputs['short']['rows_received'], 1)
        self.assertEqual(outputs['long']['rows_received'], 2)
        self.assertFalse(outputs['short']['complete_dataset'])
        self.assertTrue(outputs['long']['complete_dataset'])
        self.assertEqual(self.client._max_results, 100)
        self.assertEqual(self.client._max_pages, 5)

    async def test_cancel_propagates_after_completed_response_close(self):
        for name in ('analyze_inventory', 'analyze_product_catalog'):
            function = self.function(name)
            started = anyio.Event()
            finished = anyio.Event()

            class Blocking(Stream):
                async def __aiter__(self):
                    started.set()
                    await anyio.sleep_forever()
                    yield b''

                async def aclose(self):
                    await anyio.sleep(0)
                    await super().aclose()
                    finished.set()

            self.handler = lambda req: httpx.Response(200, stream=Blocking())
            returned = []

            async def analyze():
                returned.append(await function(self.client))

            with anyio.fail_after(2):
                async with anyio.create_task_group() as group:
                    group.start_soon(analyze)
                    await started.wait()
                    group.cancel_scope.cancel()
            self.assertTrue(finished.is_set())
            self.assertEqual(returned, [])

    async def test_analyses_need_no_configuration_read_or_llm_key(self):
        with patch.dict('os.environ', {}, clear=True), patch(
            'config._read_environment',
            side_effect=AssertionError('No config'),
        ), patch('httpx.AsyncHTTPTransport.handle_async_request',
                 side_effect=AssertionError('No real HTTP')):
            importlib.reload(importlib.import_module('analysis'))
            importlib.reload(tools)
            for name in ('analyze_inventory', 'analyze_product_catalog'):
                result = await self.function(name)(self.client)
                self.assertEqual(result['status'], 'found')
        from server import create_server
        listed = await create_server(settings()).list_tools()
        self.assertEqual({tool.name for tool in listed}, {
            'search_products', 'search_product_by_code', 'get_product_details',
            'search_product_by_ean', 'get_product_price', 'check_inventory',
            'list_products', 'list_inventory',
        })
