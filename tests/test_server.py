"""Exercise real stdio and safe logging without reading installation config."""

import io
import json
import logging
from pathlib import Path
import queue
import subprocess
import sys
import threading
from typing import TextIO, cast
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
        process = subprocess.Popen(
            [sys.executable, '-B', '-c', CHILD], cwd=ROOT,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True,
        )
        stdin_pipe = cast(TextIO, process.stdin)
        stdout_pipe = cast(TextIO, process.stdout)
        stderr_pipe = cast(TextIO, process.stderr)
        stdout, stderr = [], []
        completed = queue.Queue()
        errors = []

        def send(message):
            stdin_pipe.write(json.dumps(message) + '\n')
            stdin_pipe.flush()

        def receive(reply_id, field):
            line = stdout_pipe.readline()
            self.assertTrue(line, 'Unexpected stdio EOF before reply')
            stdout.append(line)
            reply = json.loads(line)
            self.assertEqual(reply['id'], reply_id)
            self.assertIn(field, reply)

        def exchange():
            try:
                if invalid:
                    send({
                        'jsonrpc': '2.0', 'id': 99, 'method': 'initialize',
                        'params': {'capabilities': 'SENSITIVE_INPUT_SENTINEL'},
                    })
                    receive(99, 'error')
                send(initialize())
                receive(1, 'result')
                send({'jsonrpc': '2.0', 'method': 'notifications/initialized'})
                send({
                    'jsonrpc': '2.0', 'id': 2,
                    'method': 'tools/list', 'params': {},
                })
                receive(2, 'result')
                # EOF is safe only after the last required response arrived.
                stdin_pipe.close()
                stdout.extend(stdout_pipe)
            except BaseException as exc:
                completed.put(exc)
            else:
                completed.put(None)

        def drain_stderr():
            try:
                stderr.extend(stderr_pipe)
            except BaseException as exc:
                errors.append(exc)

        threads = []
        try:
            for target in (exchange, drain_stderr):
                thread = threading.Thread(target=target, daemon=True)
                thread.start()
                threads.append(thread)
            # This bounds the entire exchange, including writes and EOF drain,
            # not just individual reads. stderr is drained concurrently.
            try:
                error = completed.get(timeout=20)
            except queue.Empty:
                self.fail('Stdio exchange exceeded 20 seconds')
            if error is not None:
                raise error
            process.wait(timeout=5)
        finally:
            try:
                if process.poll() is None:
                    process.kill()
                process.wait(timeout=5)
            finally:
                # Reaping the child releases blocked pipe operations before
                # joining workers or closing their buffered pipe objects.
                for thread in threads:
                    thread.join(timeout=2)
                alive = [thread for thread in threads if thread.is_alive()]
                if not alive:
                    for pipe in (stdin_pipe, stdout_pipe, stderr_pipe):
                        try:
                            pipe.close()
                        except BaseException as exc:
                            errors.append(exc)
                self.assertFalse(alive, 'Stdio worker failed to stop')
        if errors:
            raise errors[0]
        return subprocess.CompletedProcess(
            process.args, process.returncode, ''.join(stdout), ''.join(stderr),
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

    def test_stdio_awaits_delayed_tools_list_before_eof(self):
        # Regression scheduling only: expose EOF cancellation of an in-flight
        # handler, as in the review diagnostic. Never delay the parent helper.
        child = CHILD.replace('raise SystemExit(server.main())', '''
import anyio
from mcp import types
original_create = server.create_server

def instrumented_create(settings):
    app = original_create(settings)
    handlers = app._mcp_server.request_handlers
    original_list = handlers[types.ListToolsRequest]
    async def delayed_list(request):
        await anyio.sleep(0.1)
        return await original_list(request)
    handlers[types.ListToolsRequest] = delayed_list
    return app

server.create_server = instrumented_create
raise SystemExit(server.main())
''')
        with patch(__name__ + '.CHILD', child):
            result = self.stdio(invalid=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        replies = [json.loads(line) for line in result.stdout.splitlines()]
        self.assertEqual({reply['id'] for reply in replies}, {99, 1, 2})
        self.assertIn('error', replies[0])
        self.assertIn('result', replies[1])
        self.assertEqual(replies[2]['result']['tools'], [])
        for sentinel in (
            'SENSITIVE_INPUT_SENTINEL', 'SYNTHETIC_PRIVATE_TOKEN',
            'example.invalid', 'Traceback',
        ):
            self.assertNotIn(sentinel, result.stdout + result.stderr)

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
