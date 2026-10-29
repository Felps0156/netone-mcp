"""Offline configuration contracts; never read the operator's .env."""

from dataclasses import FrozenInstanceError
import os
from pathlib import Path
import runpy
import unittest
from unittest.mock import patch

import config
from pydantic import SecretStr


class ConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.environment = patch.dict(os.environ, {}, clear=True)
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.file = patch.object(
            Path, 'read_text', autospec=True, return_value=''
        )
        self.read_text = self.file.start()
        self.addCleanup(self.file.stop)

    def values(self, **overrides) -> dict[str, str | None]:
        return {
            'NETONE_BASE_URL': 'https://erp.example.invalid',
            'TOKEN_NETONE': 'synthetic-token',
            **overrides,
        }

    def test_defaults_secret_and_frozen_settings(self):
        settings = config._validate(self.values())
        self.assertEqual(settings.base_url, 'https://erp.example.invalid')
        self.assertIsInstance(settings.token, SecretStr)
        self.assertEqual(settings.token.get_secret_value(), 'synthetic-token')
        self.assertEqual(
            (settings.timeout_seconds, settings.max_results,
             settings.max_pages, settings.log_level),
            (15, 100, 5, 'WARNING'),
        )
        self.assertNotIn('synthetic-token', repr(settings))
        self.assertNotIn('erp.example.invalid', repr(settings))
        with self.assertRaises(FrozenInstanceError):
            setattr(settings, 'max_pages', 7)

    def test_import_does_not_read_environment_file(self):
        self.read_text.side_effect = AssertionError('Unexpected file read')
        runpy.run_path(config.__file__)

    def test_root_dotenv_precedence_without_mutation_or_interpolation(self):
        self.read_text.return_value = (
            'NETONE_BASE_URL=https://file.example.invalid\n'
            'TOKEN_NETONE=${DO_NOT_EXPAND}\nNETONE_MAX_PAGES=7\n'
            'LOGIN_NETONE=ignored\nSENHA_NETONE=ignored\n'
        )
        os.environ.update({
            key: value for key, value in self.values(
                NETONE_MAX_RESULTS='19'
            ).items() if value is not None
        })
        before = dict(os.environ)
        settings = config.load_config()
        self.assertEqual(settings.base_url, 'https://erp.example.invalid')
        self.assertEqual(settings.max_pages, 7)
        self.assertEqual(settings.max_results, 19)
        self.assertEqual(dict(os.environ), before)
        self.read_text.assert_called_once_with(
            config.PROJECT_ROOT / '.env', encoding='utf-8-sig'
        )
        os.environ.pop('TOKEN_NETONE')
        self.assertEqual(
            config.load_config().token.get_secret_value(), '${DO_NOT_EXPAND}'
        )

    def test_missing_file_uses_process_environment(self):
        self.read_text.side_effect = FileNotFoundError
        os.environ.update({
            key: value for key, value in self.values().items()
            if value is not None
        })
        self.assertEqual(config.load_config().max_pages, 5)

    def test_file_errors_and_invalid_syntax_are_sanitized(self):
        errors = (PermissionError('sensitive-path'), UnicodeError('secret'))
        for error in errors:
            with self.subTest(error=type(error).__name__):
                self.read_text.side_effect = error
                with self.assertRaises(config.ConfigurationError) as caught:
                    config.load_config()
                self.assertEqual(
                    str(caught.exception),
                    'Unable to read the configuration file.',
                )
        self.read_text.side_effect = None
        for text in (
            'TOKEN_NETONE="unclosed', 'TOKEN_NETONE=a\nTOKEN_NETONE=b'
        ):
            with self.subTest(text=text):
                self.read_text.return_value = text
                with self.assertRaises(config.ConfigurationError):
                    config.load_config()

    def test_legacy_exact_routes_and_equivalent_origins(self):
        settings = config._validate(self.values(
            NETONE_BASE_URL='https://ERP.EXAMPLE.INVALID:443/',
            REDUCED_PRODUCTS_URL=(
                'https://erp.example.invalid/app-web/api/v2/produto/reduzidos'
            ),
            STOCK_URL=(
                'https://erp.example.invalid:443'
                '/app-web/api/v2/produto/estoque'
            ),
        ))
        self.assertEqual(settings.base_url, 'https://erp.example.invalid')
        values = self.values(STOCK_URL=(
            'https://erp.example.invalid/app-web/api/v2/produto/estoque'
        ))
        del values['NETONE_BASE_URL']
        self.assertEqual(config._validate(values).base_url, settings.base_url)
        for url in (
            'https://other.example.invalid/app-web/api/v2/produto/estoque',
            'https://erp.example.invalid/app-web/api/v2/produto/estoque/',
            'https://erp.example.invalid/app-web/api/v2/produto/precos',
        ):
            with self.subTest(url=url), self.assertRaises(
                config.ConfigurationError
            ):
                config._validate(self.values(STOCK_URL=url))

    def test_invalid_urls_rejected_without_echoing_values(self):
        for url in (
            '', 'http://sensitive.invalid', 'https://',
            'https://user:secret@sensitive.invalid',
            'https://@sensitive.invalid', 'https://sensitive.invalid/path',
            'https://sensitive.invalid/a/../',
            'https://sensitive.invalid?', 'https://sensitive.invalid#',
            'https://sensitive.invalid?secret',
            'https://sensitive.invalid#secret',
            'https://sensitive.invalid\\path', 'https://sensitive.invalid/\n',
            'https://sensitive.invalid/%2f', 'https://sensitive.invalid:',
            'https://sensitive.invalid:0', 'https://sensitive.invalid:65536',
            'https://sensitive.invalid:secret', 'https://[broken',
            ' https://sensitive.invalid', 'https://sensitive.invalid/\x7f',
        ):
            with self.subTest(url=url):
                with self.assertRaises(config.ConfigurationError) as caught:
                    config._validate(self.values(NETONE_BASE_URL=url))
                self.assertNotIn('sensitive', str(caught.exception))
                self.assertNotIn('secret', str(caught.exception))

    def test_token_and_required_configuration_errors(self):
        for token in ('', 'has space', 'tab\t', '\x7f', 'é', 'x' * 8193, None):
            with self.subTest(token_type=type(token).__name__):
                with self.assertRaises(config.ConfigurationError):
                    config._validate(self.values(TOKEN_NETONE=token))
        for values in ({}, self.values(TOKEN_NETONE=None)):
            with self.assertRaises(config.ConfigurationError):
                config._validate(values)

    def test_integer_boundaries_and_invalid_lexemes(self):
        for key, field, low, high in (
            ('NETONE_TIMEOUT_SECONDS', 'timeout_seconds', 1, 120),
            ('NETONE_MAX_RESULTS', 'max_results', 1, 1000),
            ('NETONE_MAX_PAGES', 'max_pages', 1, 100),
        ):
            for value in (low, high):
                with self.subTest(key=key, value=value):
                    settings = config._validate(
                        self.values(**{key: str(value)})
                    )
                    self.assertEqual(getattr(settings, field), value)
            for value in (
                str(low - 1), str(high + 1), '1.0', '+1', '-1', ' 1',
                '١', '', None, '9' * 5000,
            ):
                with self.subTest(key=key, value_type=type(value).__name__):
                    with self.assertRaises(config.ConfigurationError):
                        config._validate(self.values(**{key: value}))

    def test_legacy_retry_setting_remains_range_validated(self):
        for value in ('0', '1', '3'):
            config._validate(self.values(NETONE_MAX_RETRIES=value))
        for value in ('-1', '4', '1.0', '', None):
            with self.subTest(value=value), self.assertRaises(
                config.ConfigurationError
            ):
                config._validate(self.values(NETONE_MAX_RETRIES=value))

    def test_standard_log_levels_and_unknown_rejection(self):
        for level in ('WARNING', 'INFO', 'ERROR', 'CRITICAL'):
            settings = config._validate(self.values(NETONE_LOG_LEVEL=level))
            self.assertEqual(settings.log_level, level)
        for level in ('debug', '', 'NOTSET', 'secret'):
            with self.subTest(level=level), self.assertRaises(
                config.ConfigurationError
            ):
                config._validate(self.values(NETONE_LOG_LEVEL=level))

    def test_debug_logging_is_accepted(self):
        settings = config._validate(self.values(NETONE_LOG_LEVEL='DEBUG'))
        self.assertEqual(settings.log_level, 'DEBUG')

    def test_operator_private_and_single_label_hosts_are_accepted(self):
        for url, expected in (
            ('https://erp', 'https://erp'),
            ('https://localhost:8443/', 'https://localhost:8443'),
            ('https://erp.local', 'https://erp.local'),
            ('https://192.168.1.20', 'https://192.168.1.20'),
            ('https://127.0.0.1', 'https://127.0.0.1'),
            ('https://[::1]', 'https://[::1]'),
            ('https://[2001:0db8:0:0:0:0:0:1]:443/', 'https://[2001:db8::1]'),
        ):
            with self.subTest(url=url):
                settings = config._validate(self.values(NETONE_BASE_URL=url))
                self.assertEqual(settings.base_url, expected)

    def test_legacy_private_ipv6_origins_are_canonical(self):
        settings = config._validate(self.values(
            NETONE_BASE_URL='https://[2001:db8::1]',
            STOCK_URL=(
                'https://[2001:0db8:0:0:0:0:0:1]:443'
                '/app-web/api/v2/produto/estoque'
            ),
        ))
        self.assertEqual(settings.base_url, 'https://[2001:db8::1]')

    def test_legacy_retry_option_does_not_enter_runtime_settings(self):
        settings = config._validate(self.values(NETONE_MAX_RETRIES='3'))
        self.assertFalse(hasattr(settings, 'max_retries'))


if __name__ == '__main__':
    unittest.main()
