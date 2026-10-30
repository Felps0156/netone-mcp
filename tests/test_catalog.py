"""Synthetic normalization and serialization contracts."""

from decimal import Decimal
import json
import unittest
from typing import Any, cast

from catalog import NormalizationError, QueryResult, normalize_record


class CatalogTests(unittest.TestCase):
    def test_serialization_does_not_deepcopy_immutable_source_amounts(self):
        class Amount(Decimal):
            def __deepcopy__(self, memo):
                raise AssertionError('Redundant recursive copy')

        record = normalize_record('products', {
            'idProduto': '0001', 'idReduzido': '002',
            'valor': Amount('1.2300'), 'quantidade': 0,
            'bloqueado': False, 'observacao': 'Café "quoted"\n',
        })
        data = QueryResult(status='found', items=(record,)).as_json()
        self.assertEqual(data['items'][0]['price'], '1.2300')
        self.assertEqual(data['items'][0]['quantity'], '0')
        self.assertIs(data['items'][0]['blocked'], False)
        self.assertEqual(data['items'][0]['notes'], 'Café "quoted"\n')
        self.assertIn('ean', data['items'][0]['missing_fields'])
        json.dumps(data, allow_nan=False)

    def test_codes_text_decimal_null_and_missing_are_distinct(self):
        record = normalize_record('products', {
            'idProduto': '0001', 'idReduzido': '0002', 'mascara': '0003',
            'codigoSku': '0004', 'ean': '0005', 'descricao': '  Text\n',
            'valor': Decimal('1234567890.123456789'), 'quantidade': 0,
            'linhaDescricao': None, 'ultimaAlteracaoTimestamp': 'opaque',
        })
        data = record.as_json()
        self.assertEqual(data['product_id'], '0001')
        self.assertEqual(data['product_mask'], '0003')
        self.assertEqual(data['sku'], '0004')
        self.assertEqual(data['ean'], '0005')
        self.assertEqual(data['description'], '  Text\n')
        self.assertEqual(data['price'], '1234567890.123456789')
        self.assertEqual(data['quantity'], '0')
        self.assertIsNone(data['line'])
        self.assertNotIn('linhaDescricao', cast(Any, data['missing_fields']))
        self.assertIn('grupoDescricao', cast(Any, data['missing_fields']))
        self.assertEqual(data['last_changed_raw'], 'opaque')
        json.dumps(data)

    def test_missing_price_and_stock_are_not_zero(self):
        record = normalize_record('stock', {'idReduzido': 2})
        self.assertIsNone(record.product_id)
        self.assertIsNone(record.price)
        self.assertIsNone(record.quantity)
        self.assertEqual(record.reduced_id, '2')

    def test_invalid_projected_types_are_rejected(self):
        for field, value in (
            ('idProduto', True), ('idReduzido', None), ('ean', 123),
            ('valor', 1.2), ('quantidade', '1'),
            ('valor', Decimal('NaN')), ('ultimaAlteracaoTimestamp', 123),
        ):
            with self.subTest(field=field, value=value):
                with self.assertRaises(NormalizationError):
                    normalize_record('products', {
                        'idProduto': 1, 'idReduzido': 2, field: value,
                    })

    def test_unprojected_fields_do_not_expand_public_contract(self):
        record = normalize_record('products', {
            'idProduto': 1, 'idReduzido': 2, 'foto': 'synthetic',
            'cor': 'synthetic', 'valorAtacado': 3,
        })
        data = record.as_json()
        self.assertNotIn('foto', data)
        self.assertNotIn('cor', data)
        self.assertNotIn('valorAtacado', data)

    def test_query_result_serializes_without_decimal_loss(self):
        record = normalize_record('prices', {
            'idProduto': 1, 'idReduzido': 2, 'valor': Decimal('1.2300'),
        })
        result = QueryResult(status='found', items=(record,))
        data = result.as_json()
        self.assertEqual(data['returned_count'], 1)
        self.assertEqual(cast(Any, data['items'])[0]['price'], '1.2300')
        self.assertEqual(data['source'], 'netone_api')
        json.dumps(data)


if __name__ == '__main__':
    unittest.main()
