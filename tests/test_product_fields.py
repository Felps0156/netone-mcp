"""Product-field priorities without false availability or value coercion."""
from dataclasses import FrozenInstanceError, fields
from decimal import Decimal
import json
from typing import Any, cast
import unittest

from catalog import CatalogRecord, NormalizationError, normalize_record
from test_client import response, row
from test_tools import ProductToolsTestCase
import tools


class ProductFieldTests(unittest.TestCase):
    def test_useful_source_fields_are_projected_exactly(self):
        record = normalize_record('products', {
            'idProduto': '0001', 'idReduzido': '0002', 'mascara': '00-Ab',
            'subgrupoDescricao': ' Synthetic subgroup ',
            'observacao': ' Note\n', 'tabelaPrecoAtacado': ' Synthetic table ',
            'valorAtacado': Decimal('1234567890.1234567890'),
            'bloqueado': False,
        })
        data = record.as_json()
        self.assertEqual(data.get('subgroup'), ' Synthetic subgroup ')
        self.assertEqual(data.get('notes'), ' Note\n')
        self.assertEqual(
            data.get('wholesale_price_table'), ' Synthetic table ',
        )
        self.assertEqual(data.get('wholesale_price'), '1234567890.1234567890')
        self.assertIs(data.get('blocked'), False)
        self.assertEqual(data['product_id'], '0001')
        self.assertEqual(data['product_mask'], '00-Ab')
        self.assertIn('codigoSku', cast(Any, data['missing_fields']))
        self.assertNotIn('bloqueado', cast(Any, data['missing_fields']))
        with self.assertRaises(FrozenInstanceError):
            cast(Any, record).description = 'mutation'
        json.dumps(data, allow_nan=False)

    def test_populated_first_preserves_blank_null_zero_and_false(self):
        record = normalize_record('products', {
            'idProduto': 1, 'idReduzido': 2, 'mascara': '00-Ab',
            'descricao': 'Synthetic item', 'codigoSku': None, 'ean': '  ',
            'grupoDescricao': 'Synthetic group', 'subgrupoDescricao': '',
            'observacao': ' ', 'valor': 0, 'valorAtacado': Decimal('0.00'),
            'quantidade': 0, 'bloqueado': False,
        })
        data = record.as_json()
        keys = list(data)
        self.assertEqual(keys[:3], ['product_mask', 'description', 'blocked'])
        self.assertLess(keys.index('price'), keys.index('ean'))
        self.assertLess(keys.index('quantity'), keys.index('sku'))
        self.assertEqual(keys[-1], 'missing_fields')
        self.assertEqual(data['price'], '0')
        self.assertEqual(data.get('wholesale_price'), '0.00')
        self.assertEqual(data['quantity'], '0')
        self.assertIs(data.get('blocked'), False)
        self.assertEqual(data['ean'], '  ')
        self.assertEqual(data.get('subgroup'), '')
        self.assertEqual(data.get('notes'), ' ')
        self.assertIsNone(data['sku'])
        self.assertEqual(set(data), {field.name for field in fields(record)})

    def test_absent_and_explicit_null_have_distinct_metadata(self):
        absent = normalize_record('products', {
            'idProduto': 1, 'idReduzido': 2,
        }).as_json()
        null = normalize_record('products', {
            'idProduto': 1, 'idReduzido': 2, 'subgrupoDescricao': None,
            'observacao': None, 'tabelaPrecoAtacado': None,
            'valorAtacado': None, 'bloqueado': None,
        }).as_json()
        for public, source in (
            ('subgroup', 'subgrupoDescricao'), ('notes', 'observacao'),
            ('wholesale_price_table', 'tabelaPrecoAtacado'),
            ('wholesale_price', 'valorAtacado'), ('blocked', 'bloqueado'),
        ):
            with self.subTest(field=public):
                self.assertIn(public, absent)
                self.assertIsNone(absent[public])
                self.assertIsNone(null[public])
                self.assertIn(source, cast(Any, absent['missing_fields']))
                self.assertNotIn(source, cast(Any, null['missing_fields']))

    def test_new_projected_types_reject_coercion_without_echo(self):
        for operation in ('products', 'prices', 'stock'):
            for source, value in (
                ('subgrupoDescricao', {'PRIVATE': 'not text'}),
                ('observacao', 1), ('tabelaPrecoAtacado', True),
                ('valorAtacado', 1.25), ('valorAtacado', True),
                ('valorAtacado', Decimal('NaN')),
                ('valorAtacado', Decimal('Infinity')),
                ('bloqueado', 0), ('bloqueado', 1),
                ('bloqueado', 'PRIVATE'), ('bloqueado', []),
            ):
                with self.subTest(operation=operation, source=source):
                    with self.assertRaises(NormalizationError) as caught:
                        normalize_record(operation, {
                            'idProduto': 1, 'idReduzido': 2, source: value,
                        })
                    self.assertNotIn('PRIVATE', str(caught.exception))

    def test_true_is_not_a_stock_or_scope_decision(self):
        for blocked in (True, False):
            data = normalize_record('products', {
                'idProduto': 1, 'idReduzido': 2, 'bloqueado': blocked,
            }).as_json()
            self.assertIn('blocked', data)
            self.assertIs(data['blocked'], blocked)
            self.assertIsNone(data['quantity'])
            self.assertNotIn('available', data)
            self.assertNotIn('in_stock', data)

    def test_all_fields_survive_presentation_with_no_raw_expansion(self):
        record = CatalogRecord(product_id='1', reduced_id='2')
        data = record.as_json()
        self.assertEqual(set(data), {field.name for field in fields(record)})
        self.assertIsNone(data['price'])
        raw = normalize_record('products', {
            'idProduto': 1, 'idReduzido': 2, 'foto': 'synthetic',
            'categoriasIds': [1], 'unknown': {'synthetic': 'value'},
        }).as_json()
        self.assertNotIn('foto', raw)
        self.assertNotIn('categoriasIds', raw)
        self.assertNotIn('unknown', raw)


class ProductFieldIntegrationTests(ProductToolsTestCase):
    async def test_commercial_function_uses_enriched_projection(self):
        self.handler = lambda request: response([row(
            mascara='00-Ab', descricao='Synthetic item', bloqueado=False,
            subgrupoDescricao='Synthetic subgroup', observacao='',
            tabelaPrecoAtacado='Synthetic wholesale table', valorAtacado=0,
        )], 1, 1, totalElements=1)
        result = await tools.search_product_by_code(self.client, '00-Ab')
        self.assertEqual(result['status'], 'found')
        item = cast(Any, result['items'])[0]
        self.assertEqual(list(item)[:3], [
            'product_mask', 'description', 'blocked',
        ])
        self.assertEqual(item.get('wholesale_price'), '0')
        self.assertEqual(item.get('subgroup'), 'Synthetic subgroup')
        self.assertIs(item.get('blocked'), False)
        self.assertTrue(result['complete_dataset'])
        self.assertEqual(self.bodies(), [
            {'page': 1, 'limit': 20, 'mascara': '00-Ab'},
        ])

    async def test_invalid_enrichment_keeps_safe_error_and_cleanup(self):
        self.handler = lambda request: response([row(
            mascara='00-Ab', bloqueado='PRIVATE',
        )], 1, 1, totalElements=1)
        result = await tools.search_product_by_code(self.client, '00-Ab')
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['items'], [])
        self.assertIsNotNone(result['error'])
        self.assertNotIn('PRIVATE', json.dumps(result))
        self.assertFalse(result['complete_dataset'])
