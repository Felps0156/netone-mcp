"""Offline contracts for the restricted HTTP and collection paths."""

import ast
from decimal import Decimal
import inspect
import json
from typing import Any, cast
import unittest
from unittest.mock import patch

import anyio
import httpx
from pydantic import SecretStr

from client import BlockedOperationError, NetOneClient, NetOneClientError
from client import ResponseError
import client as client_module
from config import Settings


class Stream(httpx.AsyncByteStream):
    """Supply raw bytes and observe completed cleanup, without sockets."""

    def __init__(self, data=b'', error=None, close_delay: float = 0):
        self.data = data
        self.error = error
        self.close_delay = close_delay
        self.closed = False
        self.close_count = 0

    async def __aiter__(self):
        if self.data:
            yield self.data
        if self.error:
            raise self.error

    async def aclose(self):
        self.close_count += 1
        await anyio.sleep(self.close_delay)
        self.closed = True


def settings(**changes):
    return Settings(
        base_url='https://example.invalid', token=SecretStr('SYNTHETIC_TOKEN'),
        **changes,
    )


def row(reduced='001', **extra):
    return {'idProduto': '0001', 'idReduzido': reduced, **extra}


def response(rows, page=1, pages=1, **extra):
    data = {'result': rows, 'page': page, 'totalPages': pages, **extra}
    return httpx.Response(200, stream=Stream(json.dumps(data).encode()))


class ClientTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Replace the library's transport before constructing the real client.
        self.requests = []
        self.streams = []
        self.handler = lambda request: response([row()])

        async def handle(request):
            self.requests.append(request)
            result = self.handler(request)
            self.streams.append(result.stream)
            return result

        self.transport_patch = patch(
            'client.httpx.AsyncHTTPTransport',
            return_value=httpx.MockTransport(handle),
        )
        self.transport_patch.start()
        self.addCleanup(self.transport_patch.stop)
        self.client = NetOneClient(settings())
        self.addAsyncCleanup(self.client.aclose)

    async def test_allowed_operation_uses_literal_route_and_closed_body(self):
        paths = {
            'products': 'reduzidos', 'prices': 'precos', 'stock': 'estoque',
        }
        for operation, path in paths.items():
            await self.client._query(operation, 1, 10)
            request = self.requests[-1]
            self.assertEqual(request.method, 'POST')
            self.assertEqual(request.url.host, 'example.invalid')
            self.assertEqual(
                request.url.path, f'/app-web/api/v2/produto/{path}',
            )
            self.assertEqual(
                json.loads(request.content), {'page': 1, 'limit': 10},
            )
            self.assertEqual(
                request.headers['netone-auth-token'], 'SYNTHETIC_TOKEN',
            )
        self.assertTrue(all(stream.closed for stream in self.streams))

    async def test_product_filter_uses_closed_body_and_existing_route(self):
        await self.client._query('products', 1, 1, product_id=7)
        request = self.requests[-1]
        self.assertEqual(request.method, 'POST')
        self.assertEqual(request.url.host, 'example.invalid')
        self.assertEqual(
            request.url.path, '/app-web/api/v2/produto/reduzidos',
        )
        self.assertEqual(
            json.loads(request.content),
            {'page': 1, 'limit': 1, 'idsProdutos': [7]},
        )
        self.assertTrue(self.streams[-1].closed)

    async def test_product_filter_accepts_strict_integer_boundaries(self):
        for value in (0, 9223372036854775807):
            with self.subTest(value=value):
                self.handler = lambda request: response([
                    row(idProduto=value),
                ])
                result = await self.client._collect(
                    'products', product_id=value,
                )
                self.assertEqual(result.status, 'found')
                self.assertEqual(result.items[0].product_id, str(value))
                self.assertEqual(
                    json.loads(self.requests[-1].content),
                    {'page': 1, 'limit': 50, 'idsProdutos': [value]},
                )

    async def test_invalid_product_filters_are_blocked_without_send(self):
        class IntegerSubclass(int):
            pass

        for value in (True, False, '007', '7', 7.0, -1,
                      9223372036854775808, IntegerSubclass(7),
                      Decimal('7'), [], {}):
            for collect in (False, True):
                with self.subTest(value=value, collect=collect):
                    with self.assertRaises(BlockedOperationError) as caught:
                        if collect:
                            await self.client._collect(
                                'products', product_id=cast(Any, value),
                            )
                        else:
                            await self.client._query(
                                'products', 1, 1,
                                product_id=cast(Any, value),
                            )
                    self.assertEqual(
                        str(caught.exception),
                        'The NetOne query is not allowed.',
                    )
        self.assertEqual(self.requests, [])

    async def test_identity_filters_are_closed_by_operation(self):
        for operation, filters in (
            ('stock', {'product_id': 7}),
            ('products', {'reduced_id': 7}),
            ('prices', {'reduced_id': 7}),
            ('prices', {'product_id': 7, 'reduced_id': 8}),
            ('stock', {'reduced_id': 7, 'product_mask': 'x'}),
            ('prices', {'product_id': 7, 'product_mask': 'x'}),
        ):
            with self.subTest(operation=operation, filters=filters):
                with self.assertRaises(BlockedOperationError):
                    await cast(Any, self.client)._query(
                        operation, 1, 1, **filters,
                    )
                with self.assertRaises(BlockedOperationError):
                    await cast(Any, self.client)._collect(operation, **filters)
        self.assertEqual(self.requests, [])

    async def test_directed_identity_filters_use_singleton_arrays(self):
        for operation, name, key, source in (
            ('prices', 'product_id', 'idsProdutos', 'idProduto'),
            ('stock', 'reduced_id', 'idsReduzidos', 'idReduzido'),
        ):
            for value in (0, 7, 9223372036854775807):
                self.handler = lambda req: response([
                    row(**cast(Any, {source: value})),
                ])
                await cast(Any, self.client)._query(
                    operation, 1, 1, **{name: value},
                )
                self.assertEqual(json.loads(self.requests[-1].content),
                                 {'page': 1, 'limit': 1, key: [value]})
                result = await cast(Any, self.client)._collect(
                    operation, **{name: value},
                )
                self.assertEqual(result.status, 'found')
                self.assertEqual(json.loads(self.requests[-1].content),
                                 {'page': 1, 'limit': 50, key: [value]})

    async def test_directed_invalid_numeric_filters_never_send(self):
        class IntegerSubclass(int):
            pass

        for operation, name in (('prices', 'product_id'),
                                ('stock', 'reduced_id')):
            for value in (True, False, -1, 9223372036854775808, '007',
                          7.0, Decimal(7), IntegerSubclass(7), [7], {}):
                for collect in (False, True):
                    with self.subTest(operation=operation, collect=collect):
                        with self.assertRaises(BlockedOperationError):
                            if collect:
                                await cast(Any, self.client)._collect(
                                    operation, **{name: value},
                                )
                            else:
                                await cast(Any, self.client)._query(
                                    operation, 1, 1, **{name: value},
                                )
        for collect in (False, True):
            with self.assertRaises(TypeError):
                if collect:
                    await cast(Any, self.client)._collect(
                        'stock', filters={'x': 1},
                    )
                else:
                    await cast(Any, self.client)._query(
                        'stock', 1, 1, idsReduzidos=[7],
                    )
        self.assertEqual(self.requests, [])

    async def test_none_product_filter_preserves_all_legacy_bodies(self):
        for operation in ('products', 'prices', 'stock'):
            await self.client._query(operation, 1, 1, product_id=None)
            await self.client._collect(operation, product_id=None)
        self.assertEqual(
            [json.loads(request.content) for request in self.requests],
            [{'page': 1, 'limit': 1}, {'page': 1, 'limit': 50}] * 3,
        )

    async def test_product_filter_keeps_fixed_pagination_and_budget(self):
        def pages(request):
            page = json.loads(request.content)['page']
            return response([
                row(f'{page}01', idProduto=7),
                row(f'{page}02', idProduto='7'),
            ], page, 3)

        self.handler = pages
        result = await self.client._collect(
            'products', page_size=2, max_results=5, product_id=7,
        )
        self.assertEqual(
            [json.loads(request.content) for request in self.requests],
            [{'page': 1, 'limit': 2, 'idsProdutos': [7]},
             {'page': 2, 'limit': 2, 'idsProdutos': [7]}],
        )
        self.assertEqual(
            [record.reduced_id for record in result.items],
            ['101', '102', '201', '202'],
        )
        self.assertEqual(result.rows_received, 4)
        self.assertEqual(result.status, 'partial')
        self.assertIn('result_limit_reached', result.warnings)

    async def test_mixed_product_page_is_rejected_atomically(self):
        for other in (8, '007', None):
            with self.subTest(other=other):
                self.handler = lambda request: response([
                    row('001', idProduto=7), row('002', idProduto=other),
                ])
                result = await self.client._collect(
                    'products', product_id=7,
                )
                self.assertEqual(result.items, ())
                self.assertEqual(result.status, 'error')
                self.assertEqual(result.error, 'invalid_response')
                self.assertTrue(result.partial)
                self.assertFalse(result.complete_dataset)
                self.assertEqual(result.rows_received, 2)

    async def test_later_mixed_product_page_keeps_only_previous_page(self):
        def pages(request):
            page = json.loads(request.content)['page']
            rows = [row('001', idProduto=7), row('002', idProduto=7)]
            if page == 2:
                rows = [row('003', idProduto=7), row('004', idProduto=8)]
            return response(rows, page, 2, totalElements=4)

        self.handler = pages
        result = await self.client._collect(
            'products', page_size=2, product_id=7,
        )
        self.assertEqual(
            [record.reduced_id for record in result.items], ['001', '002'],
        )
        self.assertEqual(result.status, 'partial')
        self.assertEqual(result.error, 'invalid_response')
        self.assertEqual(result.rows_received, 4)
        self.assertFalse(result.complete_dataset)

    async def test_filtered_http_failure_preserves_error_and_rows(self):
        for failed_page in (1, 2):
            def pages(request):
                page = json.loads(request.content)['page']
                if page == failed_page:
                    return httpx.Response(401, stream=Stream())
                return response([row(idProduto=7)], page, 2)

            with self.subTest(failed_page=failed_page):
                self.handler = pages
                result = await self.client._collect(
                    'products', page_size=1, product_id=7,
                )
                self.assertEqual(result.error, 'authentication_error')
                self.assertEqual(
                    result.status, 'error' if failed_page == 1 else 'partial',
                )
                self.assertEqual(len(result.items), failed_page - 1)
                self.assertTrue(result.partial)
                self.assertFalse(result.complete_dataset)
        self.assertTrue(all(stream.closed for stream in self.streams))

    async def test_filtered_empty_terminal_page_is_not_found(self):
        self.handler = lambda request: response([], totalElements=0)
        result = await self.client._collect('products', product_id=7)
        self.assertEqual(result.status, 'not_found')
        self.assertTrue(result.complete_dataset)
        self.assertFalse(result.partial)

    async def test_concurrent_product_filters_and_budgets_stay_local(self):
        both_started = anyio.Event()
        started = 0
        results = {}
        original_http = self.client._http

        class OverlappingStream(Stream):
            async def __aiter__(self):
                nonlocal started
                started += 1
                if started == 2:
                    both_started.set()
                await both_started.wait()
                async for chunk in super().__aiter__():
                    yield chunk

        def pages(request):
            body = json.loads(request.content)
            product = body['idsProdutos'][0]
            envelope = {
                'result': [row(str(index), idProduto=product)
                           for index in range(body['limit'])],
                'page': 1, 'totalPages': 2,
            }
            return httpx.Response(200, stream=OverlappingStream(
                json.dumps(envelope).encode(),
            ))

        async def collect(product, budget):
            results[product] = await self.client._collect(
                'products', product_id=product, max_results=budget,
            )

        self.handler = pages
        with anyio.fail_after(2):
            async with anyio.create_task_group() as group:
                group.start_soon(collect, 7, 1)
                group.start_soon(collect, 8, 2)
        self.assertEqual(
            sorted((json.loads(request.content) for request in self.requests),
                   key=lambda body: body['limit']),
            [{'page': 1, 'limit': 1, 'idsProdutos': [7]},
             {'page': 1, 'limit': 2, 'idsProdutos': [8]}],
        )
        self.assertEqual([r.product_id for r in results[7].items], ['7'])
        self.assertEqual([r.product_id for r in results[8].items], ['8', '8'])
        self.assertEqual(results[7].rows_received, 1)
        self.assertEqual(results[8].rows_received, 2)
        self.assertTrue(all(stream.closed for stream in self.streams))
        self.assertEqual(self.client._max_results, 100)
        self.assertIs(self.client._http, original_http)
        self.handler = lambda request: response([row()])
        await self.client._collect('products')
        self.assertEqual(
            json.loads(self.requests[-1].content), {'page': 1, 'limit': 50},
        )

    async def test_invalid_operation_and_parameters_do_not_send(self):
        for operation, page, limit in (
            ('login', 1, 10), ('products', True, 10),
            ('products', 0, 10), ('products', 1, 0),
            ('products', 1, 101), ('products', 1, '10'),
        ):
            with self.subTest(operation=operation, page=page, limit=limit):
                with self.assertRaises(BlockedOperationError):
                    await self.client._query(operation, page, cast(Any, limit))
        self.assertEqual(self.requests, [])

    async def test_guard_blocks_methods_origins_paths_queries_and_host(self):
        path = '/app-web/api/v2/produto/reduzidos'
        cases = [
            ('GET', path, {}), ('PUT', path, {}),
            ('POST', 'https://other.invalid' + path, {}),
            ('POST', '/app-web/api/v2/auth/login', {}),
            ('POST', path + '?page=1', {}),
            ('POST', path, {'Host': 'other.invalid'}),
            ('POST', '/app-web/api/v2/produto/%72eduzidos', {}),
        ]
        for method, url, headers in cases:
            with self.subTest(method=method, url=url, headers=headers):
                with self.assertRaises(BlockedOperationError):
                    await self.client._http.request(
                        method, url, json={'page': 1, 'limit': 1},
                        headers=headers,
                    )
        self.assertEqual(self.requests, [])

    async def test_http_errors_never_retry_or_follow_redirects(self):
        statuses = {
            401: 'authentication_error', 403: 'authorization_error',
            404: 'not_found', 429: 'rate_limited', 500: 'upstream_error',
            302: 'upstream_error', 307: 'upstream_error',
        }
        for status, code in statuses.items():
            self.handler = lambda request: httpx.Response(
                status, stream=Stream(), headers={
                    'Location': 'https://other.invalid', 'Retry-After': '1',
                },
            )
            before = len(self.requests)
            with self.assertRaises(ResponseError) as caught:
                await self.client._query('products', 1, 10)
            self.assertEqual(caught.exception.code, code)
            self.assertEqual(len(self.requests), before + 1)
            self.assertTrue(self.streams[-1].closed)

    async def test_json_validation_and_exact_decimal(self):
        self.handler = lambda request: httpx.Response(200, stream=Stream(
            b'{"result": [{"valor": 0.123456789012345678901}]}'
        ))
        result = await self.client._query('prices', 1, 10)
        self.assertEqual(cast(Any, result['result'])[0]['valor'], Decimal(
            '0.123456789012345678901'
        ))
        for data in (b'[]', b'{', b'{"result":null}', b'{"result":NaN}',
                     b'{"result":[],"result":[]}', b' ' * 1_048_577):
            self.handler = lambda request: httpx.Response(
                200, stream=Stream(data),
            )
            with self.subTest(data_length=len(data)):
                with self.assertRaises(ResponseError) as caught:
                    await self.client._query('products', 1, 10)
                self.assertEqual(caught.exception.code, 'invalid_response')
                self.assertTrue(self.streams[-1].closed)

    async def test_compressed_response_is_rejected_before_decoding(self):
        self.handler = lambda request: httpx.Response(
            200, stream=Stream(b'not compressed data'),
            headers={'Content-Encoding': 'gzip'},
        )
        with self.assertRaises(ResponseError) as caught:
            await self.client._query('products', 1, 10)
        self.assertEqual(caught.exception.code, 'invalid_response')
        self.assertTrue(self.streams[-1].closed)

    async def test_transport_errors_are_sanitized(self):
        for error, code in (
            (httpx.ReadTimeout('SENSITIVE_SENTINEL'), 'timeout'),
            (httpx.ConnectError('SENSITIVE_SENTINEL'), 'connection_error'),
            (RuntimeError('SENSITIVE_SENTINEL'), 'upstream_error'),
        ):
            def fail(request):
                raise error
            self.handler = fail
            with self.subTest(code=code):
                with self.assertRaises(ResponseError) as caught:
                    await self.client._query('products', 1, 10)
                self.assertEqual(caught.exception.code, code)
                self.assertNotIn('SENSITIVE_SENTINEL', str(caught.exception))
                self.assertIsNone(caught.exception.__context__)

    async def test_stream_failure_preserves_completed_cleanup(self):
        self.handler = lambda request: httpx.Response(
            200, stream=Stream(error=httpx.ReadTimeout('SENSITIVE_SENTINEL')),
        )
        with self.assertRaises(ResponseError) as caught:
            await self.client._query('products', 1, 10)
        self.assertEqual(caught.exception.code, 'timeout')
        self.assertTrue(self.streams[-1].closed)

    async def test_external_cancellation_waits_for_response_cleanup(self):
        started = anyio.Event()

        class WaitingStream(Stream):
            async def __aiter__(self):
                started.set()
                await anyio.sleep_forever()
                yield b''

        stream = WaitingStream(close_delay=0.01)
        self.handler = lambda request: httpx.Response(200, stream=stream)

        async def cancel_when_started(scope):
            await started.wait()
            scope.cancel()

        async with anyio.create_task_group() as group:
            group.start_soon(cancel_when_started, group.cancel_scope)
            await self.client._query('products', 1, 10)
        self.assertTrue(stream.closed)
        self.assertEqual(stream.close_count, 1)

    async def test_total_deadline_is_distinct_from_phase_timeouts(self):
        class WaitingStream(Stream):
            async def __aiter__(self):
                await anyio.sleep_forever()
                yield b''

        stream = WaitingStream(close_delay=0.01)
        self.handler = lambda request: httpx.Response(200, stream=stream)
        setattr(self.client, '_deadline', 0.02)
        with self.assertRaises(ResponseError) as caught:
            await self.client._query('products', 1, 10)
        self.assertEqual(caught.exception.code, 'timeout')
        self.assertTrue(stream.closed)

    async def test_two_page_collection_preserves_distinct_reduced_ids(self):
        def pages(request):
            page = json.loads(request.content)['page']
            return response([row(f'00{page}')], page, 2, totalElements=2)
        self.handler = pages
        result = await self.client._collect('products', page_size=1)
        self.assertEqual(result.status, 'found')
        self.assertTrue(result.complete_dataset)
        self.assertEqual([r.reduced_id for r in result.items], ['001', '002'])
        self.assertEqual(len(self.requests), 2)

    async def test_empty_terminal_query_is_not_found(self):
        self.handler = lambda request: response([], totalElements=0)
        result = await self.client._collect('products')
        self.assertEqual(result.status, 'not_found')
        self.assertFalse(result.partial)

    async def test_missing_metadata_and_repeated_terminal_are_partial(self):
        self.handler = lambda request: httpx.Response(
            200, stream=Stream(b'{"result": []}'),
        )
        self.assertTrue((await self.client._collect('products')).partial)
        self.handler = lambda request: response(
            [row()], json.loads(request.content)['page'], 2,
        )
        result = await self.client._collect('products', page_size=1)
        self.assertTrue(result.partial)
        self.assertEqual(len(result.items), 1)
        self.assertIn('pagination_no_progress', result.warnings)

    async def test_contradictory_page_is_rejected_atomically(self):
        self.handler = lambda request: response([row()], totalElements=0)
        result = await self.client._collect('products')
        self.assertEqual(result.status, 'error')
        self.assertEqual(result.items, ())
        self.assertEqual(result.error, 'invalid_response')

    async def test_later_http_error_keeps_previous_records(self):
        def pages(request):
            if json.loads(request.content)['page'] == 1:
                return response([row()], 1, 2)
            return httpx.Response(401, stream=Stream())
        self.handler = pages
        result = await self.client._collect('products', page_size=1)
        self.assertEqual(result.status, 'partial')
        self.assertEqual(len(result.items), 1)
        self.assertEqual(result.error, 'authentication_error')

    async def test_duplicate_conflict_preserved_without_completeness(self):
        self.handler = lambda request: response([
            row(descricao='first'), row(descricao='first'),
            row(descricao='second'),
        ])
        result = await self.client._collect('products')
        self.assertEqual(len(result.items), 2)
        self.assertTrue(result.partial)
        self.assertIn('duplicate_rows_removed', result.warnings)
        self.assertIn('conflicting_rows_preserved', result.warnings)

    async def test_row_budget_keeps_fixed_page_size(self):
        self.client._max_results = 3
        self.handler = lambda request: response([row('001'), row('002')], 1, 2)
        result = await self.client._collect('products', page_size=2)
        self.assertTrue(result.partial)
        self.assertEqual(len(self.requests), 1)
        self.assertEqual(result.rows_received, 2)
        self.assertIn('result_limit_reached', result.warnings)

    async def test_per_call_budget_one_bounds_default_request(self):
        self.handler = lambda request: response([row()], 1, 2)
        result = await self.client._collect('products', max_results=1)
        self.assertEqual(
            [json.loads(request.content) for request in self.requests],
            [{'page': 1, 'limit': 1}],
        )
        self.assertEqual(result.rows_received, 1)
        self.assertEqual(len(result.items), 1)
        self.assertTrue(result.partial)
        self.assertFalse(result.complete_dataset)
        self.assertIn('result_limit_reached', result.warnings)
        self.assertEqual(self.client._max_results, 100)

    async def test_per_call_budget_rejects_invalid_values_without_send(self):
        class IntegerSubclass(int):
            pass

        for budget in (True, False, 0, -1, 1001, 1.0, '1',
                       Decimal('1'), IntegerSubclass(1)):
            with self.subTest(budget=budget):
                with self.assertRaises(BlockedOperationError):
                    await self.client._collect(
                        'products', max_results=cast(Any, budget),
                    )
        self.assertEqual(self.requests, [])
        self.assertEqual(self.client._max_results, 100)

    async def test_per_call_budget_is_capped_by_configuration(self):
        configured = settings(max_results=2)
        instance = NetOneClient(configured)
        self.addAsyncCleanup(instance.aclose)
        self.handler = lambda request: response([row('001'), row('002')], 1, 2)
        result = await instance._collect('products', max_results=1000)
        self.assertEqual(
            [json.loads(request.content) for request in self.requests],
            [{'page': 1, 'limit': 2}],
        )
        self.assertEqual(result.rows_received, 2)
        self.assertIn('result_limit_reached', result.warnings)
        self.assertEqual(instance._max_results, 2)
        self.assertEqual(configured.max_results, 2)

    async def test_per_call_budget_keeps_fixed_page_size(self):
        def pages(request):
            page = json.loads(request.content)['page']
            return response(
                [row(f'{page}01'), row(f'{page}02')], page, 3,
            )

        self.handler = pages
        result = await self.client._collect(
            'products', page_size=2, max_results=5,
        )
        self.assertEqual(
            [json.loads(request.content) for request in self.requests],
            [{'page': 1, 'limit': 2}, {'page': 2, 'limit': 2}],
        )
        self.assertEqual(result.rows_received, 4)
        self.assertEqual(len(result.items), 4)
        self.assertIn('result_limit_reached', result.warnings)
        self.assertFalse(result.complete_dataset)

    async def test_per_call_budget_counts_duplicate_received_rows(self):
        self.handler = lambda request: response([row(), row()], 1, 2)
        result = await self.client._collect(
            'products', page_size=2, max_results=3,
        )
        self.assertEqual(len(self.requests), 1)
        self.assertEqual(result.rows_received, 2)
        self.assertEqual(len(result.items), 1)
        self.assertIn('duplicate_rows_removed', result.warnings)
        self.assertIn('result_limit_reached', result.warnings)

    async def test_page_size_must_fit_per_call_budget_without_send(self):
        for size in (True, 0, 2, '1'):
            with self.subTest(page_size=size):
                with self.assertRaises(BlockedOperationError):
                    await self.client._collect(
                        'products', page_size=cast(Any, size), max_results=1,
                    )
        self.assertEqual(self.requests, [])

    async def test_none_budget_preserves_default_collection(self):
        for kwargs in ({}, {'max_results': None}):
            with self.subTest(kwargs=kwargs):
                result = await self.client._collect('products', **kwargs)
                self.assertTrue(result.complete_dataset)
        self.assertEqual(
            [json.loads(request.content) for request in self.requests],
            [{'page': 1, 'limit': 50}, {'page': 1, 'limit': 50}],
        )
        self.assertEqual(self.client._max_results, 100)

    async def test_concurrent_budgets_are_isolated_on_original_client(self):
        both_started = anyio.Event()
        started = 0
        results = {}
        original_http = self.client._http

        class OverlappingStream(Stream):
            async def __aiter__(self):
                nonlocal started
                started += 1
                if started == 2:
                    both_started.set()
                await both_started.wait()
                async for chunk in super().__aiter__():
                    yield chunk

        def pages(request):
            limit = json.loads(request.content)['limit']
            envelope = {
                'result': [row(str(index)) for index in range(limit)],
                'page': 1, 'totalPages': 2,
            }
            return httpx.Response(200, stream=OverlappingStream(
                json.dumps(envelope).encode(),
            ))

        async def collect(budget):
            results[budget] = await self.client._collect(
                'products', max_results=budget,
            )

        self.handler = pages
        with anyio.fail_after(2):
            async with anyio.create_task_group() as group:
                group.start_soon(collect, 1)
                group.start_soon(collect, 2)
        self.assertEqual(results[1].rows_received, 1)
        self.assertEqual(results[2].rows_received, 2)
        self.assertEqual(
            sorted(json.loads(request.content)['limit']
                   for request in self.requests),
            [1, 2],
        )
        self.assertTrue(all(stream.closed for stream in self.streams))
        self.assertEqual(self.client._max_results, 100)
        self.assertIs(self.client._http, original_http)
        self.handler = lambda request: response([row()])
        await self.client._collect('products')
        self.assertEqual(
            json.loads(self.requests[-1].content), {'page': 1, 'limit': 50},
        )

    async def test_phase_timeout_and_redirect_policy(self):
        self.assertEqual(self.client._http.timeout, httpx.Timeout(15))
        self.assertFalse(self.client._http.follow_redirects)

    async def test_stalled_client_cleanup_is_bounded_and_reported(self):
        async def stalled_close():
            await anyio.sleep(2)

        with patch.object(self.client._http, 'aclose', stalled_close):
            with anyio.fail_after(1.5):
                with self.assertRaises(NetOneClientError):
                    await self.client.aclose()

    async def test_client_cleanup_finishes_under_cancelled_anyio_scope(self):
        completed = False
        original_close = self.client._http.aclose

        async def delayed_close():
            nonlocal completed
            await anyio.sleep(0.01)
            await original_close()
            completed = True

        with patch.object(self.client._http, 'aclose', delayed_close):
            with anyio.CancelScope() as scope:
                scope.cancel()
                await self.client.aclose()
        self.assertTrue(completed)
        self.assertTrue(self.client.is_closed)

    async def test_response_cleanup_failure_does_not_hide_authentication(self):
        class BrokenClose(Stream):
            async def aclose(self):
                raise ValueError('SENSITIVE_CLOSE_SENTINEL')

        for status, expected in ((401, 'authentication_error'),
                                 (200, 'upstream_error')):
            self.handler = lambda request: httpx.Response(
                status, stream=BrokenClose(b'{"result": []}'),
            )
            with self.assertRaises(ResponseError) as caught:
                await self.client._query('products', 1, 10)
            self.assertEqual(caught.exception.code, expected)
            self.assertIsNone(caught.exception.__context__)

    async def test_successful_slow_stream_closes_exactly_once(self):
        stream = Stream(b'{"result": []}', close_delay=0.01)
        self.handler = lambda request: httpx.Response(200, stream=stream)
        await self.client._query('products', 1, 10)
        self.assertTrue(stream.closed)
        self.assertEqual(stream.close_count, 1)

    async def test_page_ceiling_never_claims_complete_dataset(self):
        self.client._max_pages = 1
        self.handler = lambda request: response([row()], 1, 2)
        result = await self.client._collect('products', page_size=1)
        self.assertEqual(len(self.requests), 1)
        self.assertTrue(result.partial)
        self.assertFalse(result.complete_dataset)
        self.assertIn('page_limit_reached', result.warnings)

    async def test_stalled_exit_preserves_original_body_exception(self):
        primary = ValueError('synthetic body failure')

        async def stalled_close():
            await anyio.sleep_forever()

        with patch.object(self.client._http, 'aclose', stalled_close):
            with self.assertRaises(Exception) as caught:
                async with self.client:
                    raise primary
        self.assertIs(caught.exception, primary)

    async def test_stalled_exit_preserves_anyio_cancellation(self):
        observed = None

        async def stalled_close():
            await anyio.sleep_forever()

        with patch.object(self.client._http, 'aclose', stalled_close):
            with anyio.CancelScope() as scope:
                try:
                    async with self.client:
                        scope.cancel()
                        await anyio.sleep_forever()
                except BaseException as error:
                    observed = type(error)
                    if not isinstance(error, NetOneClientError):
                        raise
        self.assertIs(observed, anyio.get_cancelled_exc_class())


class ClientArchitectureTests(unittest.TestCase):
    def test_application_does_not_write_httpx_response_state(self):
        tree = ast.parse(inspect.getsource(client_module))
        forbidden = {'is_stream_consumed', 'is_closed', '_state'}
        writes = [
            node.attr for node in ast.walk(tree)
            if isinstance(node, ast.Attribute)
            and isinstance(node.ctx, ast.Store) and node.attr in forbidden
        ]
        self.assertEqual(writes, [], 'HTTPX must own its lifecycle state')

    def test_client_constructor_does_not_disable_process_loggers(self):
        import logging
        logger = logging.getLogger('httpx')
        original = logger.disabled
        try:
            logger.disabled = False
            instance = NetOneClient(settings())
            anyio.run(instance.aclose)
            self.assertFalse(logger.disabled)
        finally:
            logger.disabled = original


if __name__ == '__main__':
    unittest.main()
