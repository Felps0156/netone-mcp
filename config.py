"""Load process-owned configuration without network or environment writes."""

from dataclasses import dataclass, field
from io import StringIO
from ipaddress import ip_address
import os
from pathlib import Path
import re
from urllib.parse import urlsplit

from dotenv.parser import parse_stream
from pydantic import SecretStr


PROJECT_ROOT = Path(__file__).resolve().parent
_LEGACY_ROUTES = {
    'REDUCED_PRODUCTS_URL': '/app-web/api/v2/produto/reduzidos',
    'STOCK_URL': '/app-web/api/v2/produto/estoque',
}
_CONFIG_KEYS = (
    'NETONE_BASE_URL', 'TOKEN_NETONE', 'NETONE_TIMEOUT_SECONDS',
    'NETONE_MAX_RESULTS', 'NETONE_MAX_PAGES', 'NETONE_MAX_RETRIES',
    'NETONE_LOG_LEVEL', *_LEGACY_ROUTES,
)


class ConfigurationError(Exception):
    """Report only fixed, non-sensitive configuration diagnostics."""

    code = 'configuration_error'


@dataclass(frozen=True, slots=True)
class Settings:
    """Validated installation settings; never expose them through MCP."""

    base_url: str = field(repr=False)
    token: SecretStr = field(repr=False)
    timeout_seconds: int = 15
    max_results: int = 100
    max_pages: int = 5
    max_retries: int = 0
    log_level: str = 'WARNING'


def _read_environment() -> dict[str, str | None]:
    """Read the root file without interpolation or environment writes."""
    values: dict[str, str | None] = {}
    try:
        text = (PROJECT_ROOT / '.env').read_text(encoding='utf-8-sig')
    except FileNotFoundError:
        text = ''
    except (OSError, UnicodeError):
        raise ConfigurationError(
            'Unable to read the configuration file.'
        ) from None

    for binding in parse_stream(StringIO(text)):
        if binding.error:
            raise ConfigurationError('Invalid configuration file syntax.')
        if binding.key in _CONFIG_KEYS:
            if binding.key in values:
                raise ConfigurationError('Duplicate configuration variable.')
            values[binding.key] = binding.value

    for key in _CONFIG_KEYS:
        if key in os.environ:
            values[key] = os.environ[key]
    return values


def _url_origin(value: str | None, key: str, route: str = '') -> str:
    """Validate an HTTPS origin and an exact, internally selected path."""
    message = f'{key} must be a valid HTTPS URL with the expected path.'
    if (
        not isinstance(value, str) or not value
        or any(ord(char) <= 32 or ord(char) >= 127 for char in value)
        or any(char in value for char in ('\\', '%', '?', '#'))
    ):
        raise ConfigurationError(message)
    try:
        parsed = urlsplit(value)
        host = parsed.hostname
        port = parsed.port
    except ValueError:
        raise ConfigurationError(message) from None
    if (
        parsed.scheme != 'https' or not host
        or parsed.username is not None or parsed.password is not None
        or (port is not None and not 1 <= port <= 65535)
        or parsed.netloc.endswith(':')
        or parsed.path not in ((route,) if route else ('', '/'))
    ):
        raise ConfigurationError(message)

    try:
        address = ip_address(host)
    except ValueError:
        if '[' in parsed.netloc or ']' in parsed.netloc:
            raise ConfigurationError(message) from None
        labels = host.split('.')
        if (
            len(labels) < 2 or len(host) > 253
            or all(label.isdigit() for label in labels)
            or any(not re.fullmatch(
                r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?', label
            ) for label in labels)
            or host.endswith(('.localhost', '.local'))
        ):
            raise ConfigurationError(message) from None
        normalized_host = host
    else:
        if not address.is_global:
            raise ConfigurationError(message)
        normalized_host = (
            f'[{address}]' if address.version == 6 else str(address)
        )

    suffix = f':{port}' if port is not None and port != 443 else ''
    return f'https://{normalized_host}{suffix}'


def _integer(
    values: dict[str, str | None], key: str, default: int, minimum: int,
    maximum: int,
) -> int:
    value = values.get(key, str(default))
    if (
        not isinstance(value, str) or not re.fullmatch(r'[0-9]{1,6}', value)
        or not minimum <= int(value) <= maximum
    ):
        raise ConfigurationError(
            f'{key} must be an integer between {minimum} and {maximum}.'
        )
    return int(value)


def _validate(values: dict[str, str | None]) -> Settings:
    """Validate only recognized process configuration, never tool arguments."""
    base = None
    if 'NETONE_BASE_URL' in values:
        base = _url_origin(values['NETONE_BASE_URL'], 'NETONE_BASE_URL')
    for key, route in _LEGACY_ROUTES.items():
        if key not in values:
            continue
        origin = _url_origin(values[key], key, route)
        if base is not None and origin != base:
            raise ConfigurationError('Configured URL origins must match.')
        base = origin
    if base is None:
        raise ConfigurationError(
            'Set NETONE_BASE_URL or a supported legacy resource URL.'
        )

    token = values.get('TOKEN_NETONE')
    if (
        not isinstance(token, str) or not 1 <= len(token) <= 8192
        or any(not 33 <= ord(char) <= 126 for char in token)
    ):
        raise ConfigurationError(
            'TOKEN_NETONE must contain a non-empty printable ASCII token '
            'without whitespace.'
        )

    log_level = values.get('NETONE_LOG_LEVEL', 'WARNING')
    if log_level not in ('WARNING', 'INFO', 'ERROR', 'CRITICAL'):
        raise ConfigurationError(
            'NETONE_LOG_LEVEL must be WARNING, INFO, ERROR or CRITICAL.'
        )

    return Settings(
        base_url=base,
        token=SecretStr(token),
        timeout_seconds=_integer(values, 'NETONE_TIMEOUT_SECONDS', 15, 1, 120),
        max_results=_integer(values, 'NETONE_MAX_RESULTS', 100, 1, 1000),
        max_pages=_integer(values, 'NETONE_MAX_PAGES', 5, 1, 100),
        max_retries=_integer(values, 'NETONE_MAX_RETRIES', 0, 0, 3),
        log_level=log_level,
    )


def load_config() -> Settings:
    """Load configuration explicitly, without contacting NetOne."""
    return _validate(_read_environment())
