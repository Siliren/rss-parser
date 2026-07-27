"""Tests for URL safety validation (SSRF protection).

UA: Тести перевірки безпеки URL (захист від SSRF).

Uses IP literals so no DNS/network is needed.
"""

import pytest

from app.utils.url_safety import UnsafeUrlError, validate_url


@pytest.mark.parametrize(
    "url",
    [
        "ftp://example.com/file",       # wrong scheme
        "file:///etc/passwd",           # wrong scheme
        "javascript:alert(1)",          # wrong scheme
        "notaurl",                      # no scheme/host
        "http://localhost/",            # loopback by name
        "http://127.0.0.1/",            # loopback
        "http://[::1]/",                # IPv6 loopback
        "http://169.254.169.254/",      # cloud metadata (link-local)
        "http://10.0.0.5/",             # private
        "http://192.168.1.1/",          # private
        "http://0.0.0.0/",              # unspecified
    ],
)
def test_rejects_unsafe_urls(url):
    """Unsafe schemes and non-public addresses are blocked. / Блокує небезпечні."""
    with pytest.raises(UnsafeUrlError):
        validate_url(url)


def test_accepts_public_url():
    """A public address is allowed. / Публічна адреса дозволена."""
    assert validate_url("https://1.1.1.1/article") == "https://1.1.1.1/article"
