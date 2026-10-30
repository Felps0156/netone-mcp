"""Synthetic-only stdio entrypoint; never load installation configuration."""

from pathlib import Path
import json
import os
import sys

import anyio
import httpx
from pydantic import SecretStr

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import server
from config import Settings


original_read = Path.read_text


def protected_read(path, *args, **kwargs):
    if path.name == '.env':
        raise AssertionError('Real environment access forbidden')
    return original_read(path, *args, **kwargs)


Path.read_text = protected_read
sys.modules['langchain'] = None
sys.modules['langgraph'] = None
for key in tuple(os.environ):
    if key.endswith('API_KEY') or key.startswith('LANGCHAIN'):
        del os.environ[key]

counts = {'requests': 0, 'responses_closed': 0, 'clients_closed': 0}
search_pages = '--search-pages' in sys.argv


class Stream(httpx.AsyncByteStream):
    def __init__(self, data):
        self.data = data

    async def __aiter__(self):
        yield self.data

    async def aclose(self):
        await anyio.sleep(0)
        counts['responses_closed'] += 1


def send(request):
    counts['requests'] += 1
    assert request.method == 'POST'
    assert request.url.host == 'example.invalid'
    assert request.url.path == '/app-web/api/v2/produto/reduzidos'
    body = json.loads(request.content)
    data = (
        b'{"result":[{"idProduto":7,"idReduzido":"001",'
        b'"mascara":"0007","descricao":"Synthetic item",'
        b'"valor":123456789012345678.2300,"quantidade":0}],'
        b'"page":1,"totalPages":1,"totalElements":1}'
    )
    if search_pages:
        page = counts['requests']
        assert page in (1, 2)
        assert body == {'page': page, 'limit': 50}
        if page == 1:
            data = json.dumps({
                'result': [{'idProduto': 7, 'idReduzido': str(i),
                            'descricao': 'Other'} for i in range(50)],
                'page': 1, 'totalPages': 2, 'totalElements': 51,
            }).encode()
        else:
            data = data.replace(
                b'"page":1,"totalPages":1,"totalElements":1',
                b'"page":2,"totalPages":2,"totalElements":51',
            )
    else:
        assert body == {'page': 1, 'limit': 1}
    return httpx.Response(200, stream=Stream(data))


class Transport(httpx.MockTransport):
    async def aclose(self):
        await anyio.sleep(0)
        await super().aclose()
        counts['clients_closed'] += 1


async def forbidden_send(*args, **kwargs):
    raise AssertionError('External HTTP send forbidden')


httpx.AsyncHTTPTransport.handle_async_request = forbidden_send
httpx.AsyncHTTPTransport = lambda **kwargs: Transport(send)
server.load_config = lambda: Settings(
    base_url='https://example.invalid',
    token=SecretStr('SYNTHETIC_PRIVATE_TOKEN'), log_level='DEBUG',
)

try:
    result = server.main()
finally:
    print('offline_fixture ' + json.dumps(counts, sort_keys=True),
          file=sys.stderr)
raise SystemExit(result)
