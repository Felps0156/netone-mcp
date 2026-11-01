"""Continuation contracts through synthetic guarded HTTP, never real config."""

import asyncio
import inspect
import json
import unittest

import httpx

from client import BlockedOperationError
from test_client import response, row, Stream
from test_tools import ProductToolsTestCase
import tools


class ContinuationTests(ProductToolsTestCase):
    async def collect(self, **kwargs):
        self.assertIn('start_page', inspect.signature(
            self.client._collect).parameters)
        return await self.client._collect('products', **kwargs)

    async def test_terminal_suffix_is_not_a_complete_dataset(self):
        self.handler = lambda req: response([row('last')], 2, 2,
                                             totalElements=3)
        result = await self.collect(start_page=2, max_results=2, page_size=2)
        self.assertIsNone(result.error)
        self.assertFalse(result.complete_dataset)
        self.assertTrue(result.partial)
        self.assertTrue(result.block_complete)
        self.assertTrue(result.endpoint_exhausted)
        self.assertEqual((result.first_page, result.last_page), (2, 2))
        self.assertIsNone(result.next_page)
        self.assertEqual(result.rows_received, 1)
        self.assertEqual(self.bodies(), [{'page': 2, 'limit': 2}])

    async def test_block_budget_provides_safe_next_page(self):
        def pages(req):
            page = json.loads(req.content)['page']
            return response([row(f'{page}a'), row(f'{page}b')], page, 4,
                            totalElements=8)
        self.handler = pages
        result = await self.collect(start_page=2, max_results=5,
                                    page_size=2, max_pages=3)
        self.assertEqual(self.bodies(), [
            {'page': 2, 'limit': 2}, {'page': 3, 'limit': 2},
        ])
        self.assertEqual(result.next_page, 4)
        self.assertEqual((result.first_page, result.last_page), (2, 3))
        self.assertTrue(result.block_complete)
        self.assertFalse(result.endpoint_exhausted)
        self.assertFalse(result.complete_dataset)

    async def test_invalid_start_and_overflow_do_not_send(self):
        for value in (0, -1, 1000001, True, '2', 2.0, None):
            with self.subTest(value=value):
                self.assertIn('start_page', inspect.signature(
                    self.client._collect).parameters)
                with self.assertRaises(BlockedOperationError):
                    await self.collect(start_page=value)
        with self.assertRaises(BlockedOperationError):
            await self.collect(start_page=1000000, max_pages=2)
        self.assertEqual(self.requests, [])

    async def test_later_error_preserves_only_accepted_progress(self):
        def pages(req):
            page = json.loads(req.content)['page']
            if page == 2:
                return response([row('accepted')], 2, 4, totalElements=4)
            return httpx.Response(500, stream=Stream(b'PRIVATE'))
        self.handler = pages
        result = await self.collect(start_page=2, max_results=3,
                                    page_size=1, max_pages=3)
        self.assertEqual(result.error, 'upstream_error')
        self.assertEqual(result.last_page, 2)
        self.assertEqual(result.first_page, 2)
        self.assertIsNone(result.next_page)
        self.assertFalse(result.block_complete)
        self.assertFalse(result.endpoint_exhausted)
        self.assertEqual(len(result.items), 1)
        self.assertNotIn('PRIVATE', json.dumps(result.as_json()))

    async def test_invalid_suffix_metadata_never_advances(self):
        for page, pages, elements in ((1, 2, 3), (2, 1, 3), (2, 2, 0)):
            self.handler = lambda req: response([row('bad')], page, pages,
                                                 totalElements=elements)
            result = await self.collect(start_page=2, max_results=1)
            self.assertEqual(result.error, 'invalid_response')
            self.assertIsNone(result.last_page)
            self.assertIsNone(result.next_page)
            self.assertFalse(result.block_complete)
            self.assertFalse(result.endpoint_exhausted)

    async def test_invalid_normalization_does_not_advance(self):
        self.handler = lambda req: response([{'idReduzido': None}], 2, 2)
        result = await self.collect(start_page=2, max_results=1)
        self.assertEqual(result.error, 'invalid_response')
        self.assertIsNone(result.first_page)
        self.assertIsNone(result.last_page)
        self.assertFalse(result.block_complete)

    async def test_impossible_page_totals_reject_suffix_before_progress(self):
        self.handler = lambda req: response([row('a')], 2, 2,
                                             totalElements=1000)
        result = await self.collect(start_page=2, max_results=50,
                                    page_size=50, max_pages=1)
        self.assertEqual(result.error, 'invalid_response')
        self.assertEqual(result.items, ())
        self.assertIsNone(result.first_page)
        self.assertIsNone(result.last_page)
        self.assertIsNone(result.next_page)
        self.assertFalse(result.block_complete)
        self.assertFalse(result.endpoint_exhausted)

    async def test_changed_totals_retain_previous_progress(self):
        def pages(req):
            page = json.loads(req.content)['page']
            return response([row(str(page))], page, 4,
                            totalElements=4 if page == 2 else 5)
        self.handler = pages
        result = await self.collect(start_page=2, max_results=3,
                                    page_size=1, max_pages=3)
        self.assertEqual(result.error, 'invalid_response')
        self.assertEqual(result.last_page, 2)
        self.assertIsNone(result.next_page)
        self.assertFalse(result.block_complete)

    async def test_missing_repeated_and_conflicting_pages_are_not_safe_blocks(self):
        handlers = [
            lambda req: httpx.Response(200, stream=Stream(
                b'{"result":[{"idProduto":1,"idReduzido":"a"}]}')),
            lambda req: response([], 2, 3, totalElements=3),
            lambda req: response([row('a'), row('a')], 2, 3),
            lambda req: response([row('a', quantidade=1),
                                  row('a', quantidade=2)], 2, 3),
        ]
        for handler in handlers:
            self.handler = handler
            result = await self.collect(start_page=2, max_results=2,
                                        max_pages=1)
            self.assertFalse(result.block_complete)
            self.assertIsNone(result.next_page)
            self.assertFalse(result.complete_dataset)

    async def test_default_full_traversal_retains_completeness(self):
        self.handler = lambda req: response([row('a')], totalElements=1)
        result = await self.collect()
        self.assertEqual(result.start_page, 1)
        self.assertEqual(result.first_page, 1)
        self.assertEqual(result.last_page, 1)
        self.assertTrue(result.complete_dataset)
        self.assertTrue(result.endpoint_exhausted)
        self.assertTrue(result.block_complete)
        self.assertIsNone(result.next_page)

    async def test_empty_first_terminal_is_valid_but_empty_suffix_is_not(self):
        for start in (1, 2):
            self.handler = lambda req: response([], start, start,
                                                 totalElements=0)
            result = await self.collect(start_page=start, max_results=1)
            self.assertEqual(result.block_complete, start == 1)
            self.assertEqual(result.endpoint_exhausted, start == 1)
            self.assertEqual(result.complete_dataset, start == 1)

    async def test_concurrent_starts_keep_filters_and_progress_local(self):
        def pages(req):
            page = json.loads(req.content)['page']
            return response([row(str(page))], page, 5, totalElements=5)
        self.handler = pages
        results = await asyncio.gather(*(
            self.collect(start_page=page, max_results=1, max_pages=1)
            for page in (2, 4)
        ))
        self.assertEqual([r.next_page for r in results], [3, 5])
        self.assertEqual([r.last_page for r in results], [2, 4])
        self.assertTrue(all(r.block_complete for r in results))

    async def test_repeated_later_page_does_not_advance_safe_progress(self):
        def pages(req):
            page = json.loads(req.content)['page']
            return response([row('same')], page, 4, totalElements=4)
        self.handler = pages
        result = await self.collect(start_page=2, max_results=2,
                                    page_size=1, max_pages=2)
        self.assertEqual(result.last_page, 2)
        self.assertFalse(result.block_complete)
        self.assertIsNone(result.next_page)

    async def test_upper_page_limit_without_terminal_metadata_is_not_safe(self):
        self.handler = lambda req: response([row('a')], 1000000, 1000001)
        result = await self.collect(start_page=1000000, max_results=1,
                                    max_pages=1)
        self.assertFalse(result.block_complete)
        self.assertFalse(result.endpoint_exhausted)
        self.assertIsNone(result.next_page)


class ListingContinuationTests(ProductToolsTestCase):
    async def test_both_public_listings_continue_on_their_own_route(self):
        for name, route in (('list_products', 'reduzidos'),
                            ('list_inventory', 'estoque')):
            function = getattr(tools, name, None)
            self.assertTrue(callable(function), name + ' must exist')
            self.assertIn('start_page', inspect.signature(function).parameters)
            self.handler = lambda req: response([row('0002', quantidade=0)],
                                                 2, 2, totalElements=2)
            result = await function(self.client, 1, start_page=2,
                                    page_size=1, max_pages=1)
            self.assertEqual(self.requests[-1].url.path,
                             '/app-web/api/v2/produto/' + route)
            self.assertEqual(result['last_page'], 2)
            self.assertTrue(result['endpoint_exhausted'])
            self.assertFalse(result['complete_dataset'])
            self.assertEqual(result['items'][0]['quantity'], '0')
            if name == 'list_inventory':
                self.assertIsNone(result['inventory_scope']['deposit_id'])
                self.assertIn('inventory_freshness_unverified',
                              result['warnings'])

    async def test_listing_invalid_start_is_application_input_error(self):
        for name in ('list_products', 'list_inventory'):
            function = getattr(tools, name, None)
            self.assertTrue(callable(function), name + ' must exist')
            self.assertIn('start_page', inspect.signature(function).parameters)
            for value in (True, '1', 0, 1000001):
                with self.assertRaises(tools.ToolInputError):
                    await function(self.client, start_page=value)
            with self.assertRaises(tools.ToolInputError):
                await function(self.client, start_page=1000000, max_pages=2)
        self.assertEqual(self.requests, [])


if __name__ == '__main__':
    unittest.main()
