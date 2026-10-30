"""Synthetic contracts for expanded local product search."""

import json

import anyio
import httpx

from test_client import Stream, response, row
from test_tools import ProductToolsTestCase
import tools


class ExpandedSearchTests(ProductToolsTestCase):
    async def test_composed_query_retains_all_textual_restrictions(self):
        self.handler = lambda req: response([
            row('1', descricao='Punho LS2 azul'),
            row('2', descricao='Punho LS20 azul'),
            row('3', descricao='Punho azul', mascara='LS2'),
            row('4', descricao='Manopla LS2 vermelho'),
            row('5', descricao='Manopla LS2 azul'),
        ])
        result = await tools.search_products_expanded(
            self.client, 'manopla LS2', required_terms=('azul',),
        )
        self.assertEqual([i['reduced_id'] for i in result['items']], ['5', '1'])
        self.assertEqual(result['required_terms'], ['azul', 'LS2'])
        self.assertEqual([m['match_type'] for m in result['matches']],
                         ['direct', 'reviewed'])
        self.assertEqual(result['unverified_restriction_count'], 3)
        self.assertEqual(self.bodies(), [{'page': 1, 'limit': 50}])

    async def test_ambiguous_phrase_does_not_expand_or_drop_words(self):
        self.handler = lambda req: response([
            row('1', descricao='manopla punho LS2'),
            row('2', descricao='punho LS2'),
            row('3', descricao='manopla LS2'),
        ])
        result = await tools.search_products_expanded(
            self.client, 'manopla punho LS2', suggested_terms=('punho',),
        )
        self.assertEqual([i['reduced_id'] for i in result['items']], ['1'])
        self.assertEqual(result['search_terms'], [
            {'term': 'manopla punho LS2', 'type': 'direct'},
        ])

    async def test_lexical_boundaries_accents_and_literal_punctuation(self):
        cases = (
            ('punho', 'Empunho', False),
            ('punho', 'PUNHO-LS2', True),
            ('cafe', 'Café', True),
            ('[a]*', 'Literal [a]* item', True),
            ('[a]*', 'Literal aaaa item', False),
            ('manopla', 'manoplas', False),
        )
        for query, description, matched in cases:
            with self.subTest(query=query, description=description):
                self.handler = lambda req: response([
                    row('1', descricao=description),
                ])
                result = await tools.search_products_expanded(self.client, query)
                self.assertEqual(result['returned_count'], int(matched))
                self.assertEqual(result['status'],
                                 'found' if matched else 'not_found')
                if matched:
                    self.assertEqual(result['items'][0]['description'],
                                     description)

    async def test_direct_priority_cut_keeps_items_matches_aligned(self):
        self.handler = lambda req: response([
            row('1', descricao='Punho'), row('2', descricao='manopla'),
            row('3', descricao='pegador'),
        ])
        result = await tools.search_products_expanded(
            self.client, 'manopla', suggested_terms=('pegador', 'PUNHO'),
            max_items=1,
        )
        self.assertEqual([i['reduced_id'] for i in result['items']], ['2'])
        self.assertEqual(result['matches'], [
            {'matched_terms': ['manopla'], 'match_type': 'direct'},
        ])
        self.assertEqual(result['matched_count'], 3)
        self.assertTrue(result['output_truncated'])
        self.assertTrue(result['collection_complete'])
        self.assertEqual(result['status'], 'partial')
        self.assertIn('output_limit_reached', result['warnings'])
        self.assertEqual(len(result['search_terms']), 3)

    async def test_expanded_limits_reject_before_send(self):
        for name in ('max_results', 'max_items'):
            for value in (True, 0, 1001, '1', None):
                with self.assertRaises(ValueError):
                    await tools.search_products_expanded(
                        self.client, 'manopla', **{name: value},
                    )
        self.assertEqual(self.requests, [])

    async def test_normalization_empty_terms_are_rejected_before_collection(self):
        self.handler = lambda req: response([
            row('1', descricao='Other product'), row('2', descricao=None),
            row('3', descricao='Manopla'),
        ])
        for mark in ('\u0301', '\u0301 \u0308'):
            for query, kwargs in (
                (mark, {}),
                ('manopla', {'required_terms': (mark,)}),
                ('manopla', {'suggested_terms': (mark,)}),
                ('manopla ' + mark, {}),
                ('ambiguous phrase', {'suggested_terms': (mark,)}),
            ):
                with self.subTest(query=query, kwargs=kwargs):
                    with self.assertRaises(ValueError):
                        await tools.search_products_expanded(
                            self.client, query, **kwargs,
                        )
        self.assertEqual(self.requests, [])

    async def test_one_traversal_cost_matches_literal_for_same_universe(self):
        def pages(req):
            page = json.loads(req.content)['page']
            rows = ([row(str(i), descricao='Other') for i in range(50)]
                    if page == 1 else [row('target', descricao='Punho LS2')])
            return response(rows, page, 2, totalElements=51)

        self.handler = pages
        literal = await tools.search_products(self.client, 'punho')
        bodies = self.bodies()
        self.requests.clear()
        expanded = await tools.search_products_expanded(
            self.client, 'manopla LS2', suggested_terms=('pegador', 'PUNHO'),
        )
        self.assertEqual(self.bodies(), bodies)
        self.assertEqual(len(bodies), 2)
        for result in (literal, expanded):
            self.assertEqual(result['pages_fetched'], 2)
            self.assertEqual(result['rows_received'], 51)
            self.assertEqual(result['matched_count'], 1)
            self.assertEqual(result['returned_count'], 1)
            self.assertGreater(len(json.dumps(result).encode()), 0)

    async def test_errors_after_rows_survive_expanded_filter_and_cut(self):
        for description in ('Other', 'Punho LS2'):
            for status, error in ((401, 'authentication_error'),
                                  (429, 'rate_limited'),
                                  (500, 'upstream_error')):
                self.requests.clear()

                def pages(req):
                    if json.loads(req.content)['page'] == 1:
                        return response([
                            row(str(i), descricao=description) for i in range(50)
                        ], 1, 2)
                    return httpx.Response(status, stream=Stream(b'PRIVATE'))

                self.handler = pages
                result = await tools.search_products_expanded(
                    self.client, 'manopla LS2', max_items=1,
                )
                self.assertEqual(result['status'], 'partial')
                self.assertEqual(result['error'], error)
                self.assertFalse(result['collection_complete'])
                self.assertEqual(result['returned_count'],
                                 int(description == 'Punho LS2'))
                self.assertEqual(len(self.requests), 2)
                self.assertEqual(len(result['matches']), result['returned_count'])
                self.assertNotIn('PRIVATE', json.dumps(result))

    async def test_composed_and_literal_concurrent_budgets_stay_local(self):
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
            size = json.loads(req.content)['limit']
            return httpx.Response(200, stream=Overlap(json.dumps({
                'result': [row(str(i), descricao='Manopla LS2')
                           for i in range(size)],
                'page': 1, 'totalPages': 2,
            }).encode()))

        async def literal():
            results['literal'] = await tools.search_products(
                self.client, 'manopla', 1, max_items=1,
            )

        async def expanded():
            results['expanded'] = await tools.search_products_expanded(
                self.client, 'manopla LS2', max_results=2, max_items=1,
            )

        self.handler = pages
        with anyio.fail_after(2):
            async with anyio.create_task_group() as group:
                group.start_soon(literal)
                group.start_soon(expanded)
        self.assertEqual(sorted(self.bodies(), key=lambda b: b['limit']), [
            {'page': 1, 'limit': 1}, {'page': 1, 'limit': 2},
        ])
        self.assertEqual(results['literal']['inspection_limit'], 1)
        self.assertEqual(results['expanded']['inspection_limit'], 2)
        self.assertEqual(results['literal']['matched_count'], 1)
        self.assertEqual(results['expanded']['matched_count'], 2)
        self.assertTrue(results['expanded']['output_truncated'])
        self.assertEqual(self.client._max_results, 100)

    async def test_expanded_initial_error_and_conflicting_rows(self):
        self.handler = lambda req: httpx.Response(403, stream=Stream(b'PRIVATE'))
        failed = await tools.search_products_expanded(self.client, 'manopla')
        self.assertEqual(failed['status'], 'error')
        self.assertEqual(failed['error'], 'authorization_error')
        self.assertEqual(failed['matches'], [])
        self.handler = lambda req: response([
            row('1', descricao='manopla'), row('1', descricao='punho'),
        ], totalElements=2)
        result = await tools.search_products_expanded(self.client, 'manopla')
        self.assertEqual(result['returned_count'], 2)
        self.assertEqual(result['status'], 'partial')
        self.assertFalse(result['collection_complete'])
        self.assertIn('conflicting_rows_preserved', result['warnings'])

    async def test_collection_anomalies_remain_inconclusive_in_both_searches(self):
        for expanded in (False, True):
            for anomaly in ('missing', 'contradictory', 'empty', 'repeated'):
                self.requests.clear()

                def pages(req):
                    page = json.loads(req.content)['page']
                    if anomaly == 'missing':
                        return httpx.Response(200, stream=Stream(b'{"result":[]}'))
                    if anomaly == 'contradictory':
                        return response([row(descricao='Other')], 1, 1,
                                        totalElements=0)
                    if page == 1 or anomaly == 'repeated':
                        return response([row(descricao='Other')], page, 2)
                    return response([], page, 2)

                self.handler = pages
                function = (tools.search_products_expanded if expanded
                            else tools.search_products)
                result = await function(self.client, 'manopla')
                self.assertEqual(result['returned_count'], 0)
                self.assertFalse(result['collection_complete'])
                self.assertEqual(result['status'],
                                 'error' if anomaly == 'contradictory'
                                 else 'partial')
                self.assertEqual(len(self.requests),
                                 1 if anomaly in ('missing', 'contradictory')
                                 else 2)

    async def test_search_deadline_and_cancellation_finish_stream_cleanup(self):
        for expanded in (False, True):
            for cancel in (False, True):
                started = anyio.Event()

                class WaitingStream(Stream):
                    async def __aiter__(self):
                        started.set()
                        await anyio.sleep_forever()
                        yield b''

                stream = WaitingStream(close_delay=0.01)
                self.handler = lambda req: httpx.Response(200, stream=stream)
                instance = self.make_client()
                function = (tools.search_products_expanded if expanded
                            else tools.search_products)
                if cancel:
                    async def cancel_when_started(scope):
                        await started.wait()
                        scope.cancel()

                    with anyio.fail_after(2):
                        async with anyio.create_task_group() as group:
                            group.start_soon(cancel_when_started,
                                             group.cancel_scope)
                            await function(instance, 'manopla')
                            self.fail('Cancellation must propagate')
                else:
                    instance._deadline = 0.02
                    result = await function(instance, 'manopla')
                    self.assertEqual(result['status'], 'error')
                    self.assertEqual(result['error'], 'timeout')
                self.assertTrue(stream.closed)
                self.assertEqual(stream.close_count, 1)

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
