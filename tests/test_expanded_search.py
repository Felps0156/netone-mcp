"""Synthetic contracts for expanded local product search."""

import json

import httpx

from test_client import Stream, response, row
from test_tools import ProductToolsTestCase
import tools


class ExpandedSearchTests(ProductToolsTestCase):
    async def test_related_terms_search_one_traversal_beyond_twenty_rows(self):
        def pages(request):
            page = json.loads(request.content)['page']
            if page == 1:
                return response([row(str(i), descricao='Other') for i in range(50)], 1, 2, totalElements=51)
            return response([row('50', descricao='Punho LS2')], 2, 2, totalElements=51)

        self.handler = pages
        result = await tools.search_products_expanded(
            self.client, 'manopla', required_terms=('LS2',),
            suggested_terms=('punho',),
        )
        self.assertEqual(result['returned_count'], 1)
        self.assertEqual(result['items'][0]['description'], 'Punho LS2')
        self.assertEqual(result['matches'][0]['matched_terms'], ['punho'])
        self.assertEqual(result['matches'][0]['match_type'], 'reviewed')
        self.assertTrue(result['complete_dataset'])
        self.assertEqual(self.bodies(), [{'page': 1, 'limit': 50}, {'page': 2, 'limit': 50}])

    async def test_restriction_is_required_in_description(self):
        self.handler = lambda request: response([
            row('1', descricao='Manopla LS2'),
            row('2', descricao='Manopla other'),
            row('3', descricao='Manopla', mascara='LS2'),
        ])
        result = await tools.search_products_expanded(self.client, 'manopla', required_terms=('LS2',))
        self.assertEqual([item['reduced_id'] for item in result['items']], ['1'])

    async def test_invalid_suggestions_fail_before_request(self):
        for terms in (('bad\n',), ('',), ('x',) * 21, 'punho'):
            with self.subTest(terms=terms):
                with self.assertRaises(ValueError):
                    await tools.search_products_expanded(self.client, 'manopla', suggested_terms=terms)
        self.assertEqual(self.requests, [])

    async def test_limited_and_missing_metadata_remain_partial(self):
        self.handler = lambda request: httpx.Response(200, stream=Stream(b'{"result": []}'))
        result = await tools.search_products_expanded(self.client, 'manopla')
        self.assertEqual(result['status'], 'partial')
        self.assertFalse(result['complete_dataset'])
        self.assertIn('pagination_metadata_missing', result['warnings'])

    async def test_reviewed_and_suggested_matches_are_distinct(self):
        self.handler = lambda request: response([
            row('1', descricao='manopla'), row('2', descricao='punho'),
            row('3', descricao='pegador'),
        ])
        result = await tools.search_products_expanded(self.client, 'manopla', suggested_terms=('pegador',))
        self.assertEqual([match['match_type'] for match in result['matches']], ['direct', 'reviewed', 'suggested'])

    async def test_restrictions_do_not_match_longer_model_codes(self):
        self.handler = lambda request: response([
            row('1', descricao='manopla LS20'),
            row('2', descricao='manopla (LS2)'),
            row('3', descricao='manopla desconhecida'),
        ])
        result = await tools.search_products_expanded(
            self.client, 'manopla', required_terms=('LS2',),
        )
        self.assertEqual([item['reduced_id'] for item in result['items']], ['2'])
        self.assertEqual(result['unverified_restriction_count'], 2)

    async def test_duplicate_terminal_page_does_not_claim_complete(self):
        self.handler = lambda request: response([
            row('1', descricao='manopla'), row('1', descricao='manopla'),
        ], totalElements=2)
        result = await tools.search_products_expanded(self.client, 'manopla')
        self.assertEqual(result['status'], 'partial')
        self.assertFalse(result['complete_dataset'])
        self.assertIn('duplicate_rows_removed', result['warnings'])
