"""Offline external MCP campaign, using real list tools where possible."""

import asyncio
import importlib
import json
from types import SimpleNamespace
import unittest

import test_mcp_tools
from test_client import response, row


def block(page, pages, items, total=None):
    partial = page != 1 or page < pages
    return {
        'status': 'partial' if partial else 'found' if items else 'not_found',
        'partial': partial, 'error': None,
        'complete_dataset': not partial,
        'items': items, 'returned_count': len(items), 'warnings': [],
        'pages_fetched': 1, 'rows_received': len(items), 'page_size': 1,
        'start_page': page, 'first_page': page, 'last_page': page,
        'next_page': page + 1 if page < pages else None,
        'block_complete': True, 'endpoint_exhausted': page >= pages,
        'total_pages': pages, 'total_elements': pages if total is None else total,
    }


class FakeSession:
    def __init__(self, handler):
        self.handler, self.calls = handler, []

    async def call_tool(self, name, arguments):
        self.calls.append((name, arguments))
        return SimpleNamespace(isError=False, structuredContent=self.handler(
            name, arguments['start_page']))


class ConsumerTests(unittest.IsolatedAsyncioTestCase):
    def api(self):
        self.assertIsNotNone(importlib.util.find_spec('mcp_consumer'),
                             'Reusable external MCP consumer is required')
        return importlib.import_module('mcp_consumer')

    async def test_exact_join_zero_unknown_orphans_and_full_coverage(self):
        api = self.api()
        products = [{'reduced_id': v} for v in ('001', '1', '2')]
        stock = [{'reduced_id': '001', 'quantity': '0.00'},
                 {'reduced_id': '1', 'quantity': None},
                 {'reduced_id': 'orphan', 'quantity': '9.20'}]
        session = FakeSession(lambda name, page: block(page, 3,
            [(products if name == 'list_products' else stock)[page - 1]]))
        result = await api.collect_catalog_inventory(session, page_size=1)
        self.assertTrue(result['collection_complete'])
        self.assertEqual(result['calls_made'], 6)
        self.assertEqual(result['rows_received'], 6)
        joined = {v['reduced_id']: v for v in result['items']}
        self.assertEqual(joined['001']['quantity'], '0.00')
        self.assertEqual(joined['001']['stock_status'], 'zero')
        self.assertEqual(joined['1']['stock_status'], 'unknown')
        self.assertEqual(joined['2']['stock_status'], 'not_found')
        self.assertIsNone(joined['2']['quantity'])
        self.assertEqual(result['inventory_only_ids'], ['orphan'])
        self.assertTrue(result['partial'])  # unknown quantity is not complete data
        json.dumps(result, allow_nan=False)

    async def test_inconsistent_completeness_flags_never_upgrade_to_complete(self):
        api = self.api()
        for changes in (
            {'status': 'partial', 'partial': True, 'complete_dataset': False},
            {'status': None}, {'status': 'invalid'}, {'partial': 0},
            {'complete_dataset': 1}, {'partial': True},
            {'complete_dataset': False},
        ):
            with self.subTest(changes=changes):
                def handler(name, page):
                    data = block(1, 1, [{'reduced_id': '1', 'quantity': '2'}])
                    data.update(changes)
                    return data
                session = FakeSession(handler)
                result = await api.collect_catalog_inventory(session, page_size=1)
                self.assertFalse(result['collection_complete'])
                self.assertFalse(result['complete_dataset'])
                self.assertTrue(result['partial'])
                self.assertEqual(result['error'], 'inconsistent_paging_or_records')
                self.assertEqual(len(session.calls), 1)

    async def test_global_budgets_prevent_unnecessary_calls(self):
        api = self.api()
        for options in ({'max_calls': 1}, {'max_pages': 1}, {'max_rows': 1}):
            session = FakeSession(lambda name, page: block(page, 2,
                                      [{'reduced_id': str(page)}]))
            result = await api.collect_catalog_inventory(
                session, page_size=1, **options)
            self.assertEqual(len(session.calls), 1)
            self.assertFalse(result['collection_complete'])
            self.assertTrue(result['partial'])
            self.assertEqual(result['items'][0]['stock_status'], 'unknown')

    async def test_cross_block_duplicates_and_conflicts_stop_without_summing(self):
        api = self.api()
        for conflicting in (False, True):
            def handler(name, page):
                if name == 'list_products':
                    return block(1, 1, [{'reduced_id': '1'}])
                return block(page, 2, [{'reduced_id': '1',
                    'quantity': '2' if page == 1 or not conflicting else '3'}])
            session = FakeSession(handler)
            result = await api.collect_catalog_inventory(session, page_size=1)
            self.assertFalse(result['collection_complete'])
            self.assertTrue(result['partial'])
            self.assertEqual(len(session.calls), 3)
            self.assertIn('conflicting_rows_preserved' if conflicting else
                          'duplicate_rows_removed', result['warnings'])
            item = result['items'][0]
            if conflicting:
                self.assertEqual(item['stock_status'], 'conflict')
                self.assertIsNone(item['quantity'])
                self.assertEqual(len(item['inventory_records']), 2)

    async def test_source_conflict_warning_prevents_single_projected_balance(self):
        api = self.api()
        def handler(name, page):
            data = block(1, 1, [{'reduced_id': '1', 'quantity': '2'}])
            if name == 'list_inventory':
                data.update(block_complete=False, first_page=None, last_page=None,
                            endpoint_exhausted=False,
                            warnings=['conflicting_rows_preserved'])
            return data
        result = await api.collect_catalog_inventory(
            FakeSession(handler), page_size=1)
        self.assertEqual(result['items'][0]['stock_status'], 'conflict')
        self.assertIsNone(result['items'][0]['quantity'])

    async def test_changed_totals_invalid_progress_and_missing_metadata_stop(self):
        api = self.api()
        for mutate in (
            lambda b: b.update(total_pages=3),
            lambda b: b.update(total_elements=3),
            lambda b: b.update(first_page=1),
            lambda b: b.update(next_page=2, endpoint_exhausted=False),
            lambda b: b.update(block_complete=False),
            lambda b: b.update(total_pages=None),
            lambda b: b.update(page_size=2),
            lambda b: b.update(rows_received=0),
        ):
            def handler(name, page):
                b = block(page, 2, [{'reduced_id': str(page)}])
                if page == 2:
                    mutate(b)
                return b
            session = FakeSession(handler)
            result = await api.collect_catalog_inventory(session, page_size=1)
            self.assertFalse(result['collection_complete'])
            self.assertEqual(len(session.calls), 2)
            self.assertEqual(result['catalog']['last_page'], 1)

    async def test_error_after_data_is_sanitized_preserved_and_not_retried(self):
        api = self.api()
        session = FakeSession(lambda name, page: block(page, 3,
                                  [{'reduced_id': str(page)}]))
        original = session.call_tool
        async def call(name, arguments):
            if arguments['start_page'] == 2:
                session.calls.append((name, arguments))
                raise RuntimeError('PRIVATE')
            return await original(name, arguments)
        session.call_tool = call
        result = await api.collect_catalog_inventory(session, page_size=1)
        self.assertEqual(result['error'], 'mcp_call_failed')
        self.assertEqual(result['returned_count'], 1)
        self.assertNotIn('PRIVATE', json.dumps(result))
        self.assertEqual(len(session.calls), 2)

    async def test_invalid_identity_or_quantity_rejects_page_atomically(self):
        api = self.api()
        for invalid in ({'reduced_id': 1}, {'reduced_id': ''},
                        {'reduced_id': '1', 'quantity': 'NaN'},
                        {'reduced_id': '1', 'quantity': 1.5}):
            session = FakeSession(lambda name, page: block(1, 1, [invalid]))
            result = await api.collect_catalog_inventory(session, page_size=1)
            self.assertTrue(result['partial'])
            self.assertEqual(result['returned_count'], 0)
            self.assertEqual(len(session.calls), 1)

    async def test_invalid_options_never_call(self):
        api = self.api()
        for options in ({'page_size': True}, {'max_calls': 0},
                        {'max_rows': '2'}, {'max_pages': 1000001},
                        {'timeout_seconds': 0}):
            session = FakeSession(lambda *_: None)
            with self.assertRaises(ValueError):
                await api.collect_catalog_inventory(session, **options)
            self.assertEqual(session.calls, [])

    async def test_timeout_returns_partial_without_retry(self):
        api = self.api()
        class SlowSession:
            calls = 0
            async def call_tool(self, *_):
                self.calls += 1
                await asyncio.sleep(2)
        session = SlowSession()
        result = await api.collect_catalog_inventory(session, timeout_seconds=1)
        self.assertEqual(result['error'], 'campaign_timeout')
        self.assertTrue(result['partial'])
        self.assertEqual(session.calls, 1)

    async def test_mcp_error_and_missing_structured_content_never_retry(self):
        api = self.api()
        for reply in (SimpleNamespace(isError=True, structuredContent={}),
                      SimpleNamespace(isError=False, structuredContent=None)):
            class Session:
                calls = 0
                async def call_tool(self, *_):
                    self.calls += 1
                    return reply
            session = Session()
            result = await api.collect_catalog_inventory(session)
            self.assertEqual(result['error'], 'mcp_tool_failed')
            self.assertFalse(result['complete_dataset'])
            self.assertEqual(session.calls, 1)

    async def test_cancellation_propagates(self):
        api = self.api()
        class CancelSession:
            async def call_tool(self, *_):
                raise asyncio.CancelledError()
        with self.assertRaises(asyncio.CancelledError):
            await api.collect_catalog_inventory(CancelSession())


class ConsumerMCPTests(unittest.IsolatedAsyncioTestCase):
    session = test_mcp_tools.MCPToolsTests.session

    async def test_generic_sdk_preserves_intrablock_conflicts_without_balance(self):
        self.assertIsNotNone(importlib.util.find_spec('mcp_consumer'))
        api = importlib.import_module('mcp_consumer')
        def handler(req):
            if req.url.path.endswith('reduzidos'):
                return response([row('1')], totalElements=1)
            return response([row('1', quantidade=2),
                             row('1', quantidade=3)], totalElements=2)
        async with self.session(handler) as (session, requests, _):
            result = await api.collect_catalog_inventory(session, page_size=2)
            self.assertFalse(result['collection_complete'])
            self.assertEqual(result['items'][0]['stock_status'], 'conflict')
            self.assertIsNone(result['items'][0]['quantity'])
            self.assertEqual(len(result['items'][0]['inventory_records']), 2)
            self.assertEqual(len(requests), 2)

    async def test_generic_sdk_empty_visible_endpoints_are_complete_not_found(self):
        api = importlib.import_module('mcp_consumer')
        async with self.session(lambda req: response([], totalElements=0)) as (
                session, requests, _):
            result = await api.collect_catalog_inventory(session, page_size=1)
            self.assertTrue(result['collection_complete'])
            self.assertFalse(result['partial'])
            self.assertEqual(result['status'], 'not_found')
            self.assertEqual(len(requests), 2)

    async def test_generic_sdk_session_traverses_both_tools(self):
        self.assertIsNotNone(importlib.util.find_spec('mcp_consumer'),
                             'Reusable external MCP consumer is required')
        api = importlib.import_module('mcp_consumer')
        def handler(req):
            page = json.loads(req.content)['page']
            return response([row(str(page), quantidade=0)], page, 2,
                            totalElements=2)
        async with self.session(handler) as (session, requests, _):
            result = await api.collect_catalog_inventory(session, page_size=1)
            self.assertTrue(result['collection_complete'])
            self.assertFalse(result['partial'])
            self.assertEqual(len(requests), 4)
            self.assertEqual([v['stock_status'] for v in result['items']],
                             ['zero', 'zero'])
