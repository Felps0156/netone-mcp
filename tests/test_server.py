"""Exercise real stdio and safe logging without reading installation config."""

import io
import json
import logging
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import server
from config import ConfigurationError


ROOT = Path(__file__).resolve().parents[1]
CHILD = '''
import os
import sys
from pathlib import Path
sys.modules['langchain'] = None
sys.modules['langgraph'] = None
import httpx
from pydantic import SecretStr
import server
from config import Settings

original_read = Path.read_text

def protected_read(path, *args, **kwargs):
    if path.name == '.env':
        raise AssertionError('Environment file access forbidden')
    return original_read(path, *args, **kwargs)

Path.read_text = protected_read

async def forbidden_send(*args, **kwargs):
    raise AssertionError('Network forbidden')

httpx.AsyncHTTPTransport.handle_async_request = forbidden_send
for key in tuple(os.environ):
    if key.endswith('API_KEY') or key.startswith('LANGCHAIN'):
        del os.environ[key]
server.load_config = lambda: Settings(
    base_url='https://example.invalid',
    token=SecretStr('SYNTHETIC_PRIVATE_TOKEN'),
    log_level='DEBUG',
)
raise SystemExit(server.main())
'''


def initialize():
    return {
        'jsonrpc': '2.0', 'id': 1, 'method': 'initialize',
        'params': {
            'protocolVersion': '2025-03-26', 'capabilities': {},
            'clientInfo': {'name': 'offline-tests', 'version': '1'},
        },
    }


class ServerTests(unittest.TestCase):
    def stdio(self, invalid=False):
        messages = []
        if invalid:
            messages.append({
                'jsonrpc': '2.0', 'id': 99, 'method': 'initialize',
                'params': {'capabilities': 'SENSITIVE_INPUT_SENTINEL'},
            })
        messages.extend([
            initialize(),
            {'jsonrpc': '2.0', 'method': 'notifications/initialized'},
            {'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list', 'params': {}},
        ])
        return subprocess.run(
            [sys.executable, '-B', '-c', CHILD], cwd=ROOT,
            input=''.join(json.dumps(m) + '\n' for m in messages),
            capture_output=True, text=True, timeout=20,
        )

    def test_stdio_has_empty_registry_and_no_network_or_llm(self):
        result = self.stdio()
        self.assertEqual(result.returncode, 0, result.stderr)
        replies = [json.loads(line) for line in result.stdout.splitlines()]
        self.assertEqual({reply['id'] for reply in replies}, {1, 2})
        tools = next(r['result']['tools'] for r in replies if r['id'] == 2)
        self.assertEqual(tools, [])
        self.assertNotIn(
            'SYNTHETIC_PRIVATE_TOKEN', result.stdout + result.stderr,
        )
        self.assertNotIn('example.invalid', result.stdout + result.stderr)

    def test_malformed_mcp_input_is_not_logged_and_session_recovers(self):
        result = self.stdio(invalid=True)
        self.assertEqual(result.returncode, 0)
        replies = [json.loads(line) for line in result.stdout.splitlines()]
        self.assertTrue(any(r['id'] == 99 and 'error' in r for r in replies))
        self.assertTrue(any(r['id'] == 2 and r['result']['tools'] == []
                            for r in replies))
        self.assertNotIn(
            'SENSITIVE_INPUT_SENTINEL', result.stdout + result.stderr,
        )
        self.assertNotIn('SYNTHETIC_PRIVATE_TOKEN', result.stderr)
        self.assertNotIn('Traceback', result.stderr)

    def test_configuration_error_is_safe_and_stdout_empty(self):
        out, err = io.StringIO(), io.StringIO()
        with patch.object(server, 'load_config', side_effect=(
            ConfigurationError('Missing required configuration.')
        )), patch('sys.stdout', out), patch('sys.stderr', err):
            self.assertEqual(server.main(), 1)
        self.assertEqual(out.getvalue(), '')
        self.assertEqual(
            err.getvalue(),
            'configuration_error: Missing required configuration.\n',
        )

    def test_library_diagnostics_have_level_component_and_safe_code(self):
        root = logging.getLogger()
        original_handlers, original_level = root.handlers[:], root.level
        names = ('mcp', 'httpx', 'httpcore', 'mcp.synthetic_child')
        loggers = [logging.getLogger(name) for name in names]
        states = [
            (log, log.handlers[:], log.level, log.propagate, log.disabled)
            for log in loggers
        ]
        captured = io.StringIO()
        try:
            for logger in loggers:
                logger.disabled = True
                logger.addHandler(logging.StreamHandler(io.StringIO()))
            with patch('sys.stderr', captured):
                server._configure_safe_logging('DEBUG')
                for logger in loggers:
                    logger.warning('SENSITIVE_INPUT_SENTINEL %s', 'TOKEN')
                try:
                    raise ValueError('SENSITIVE_EXCEPTION_SENTINEL')
                except ValueError:
                    logging.exception('SENSITIVE_ROOT_SENTINEL')
            lines = captured.getvalue().splitlines()
            self.assertEqual(len(lines), 5)
            for line in lines:
                self.assertIn('level=', line)
                self.assertIn('component=', line)
                self.assertIn('code=', line)
                self.assertNotIn('SENSITIVE', line)
                self.assertNotIn('TOKEN', line)
            self.assertIn('component=httpx', captured.getvalue())
            self.assertIn('component=mcp', captured.getvalue())
            self.assertFalse(any(logger.disabled for logger in loggers))
        finally:
            root.handlers, root.level = original_handlers, original_level
            for log, handlers, level, propagate, disabled in states:
                log.handlers = handlers
                log.level = level
                log.propagate, log.disabled = propagate, disabled


if __name__ == '__main__':
    unittest.main()
