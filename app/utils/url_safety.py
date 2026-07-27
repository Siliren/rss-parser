"""URL safety checks — only allow fetching safe, public http(s) URLs.

UA: Перевірка безпеки URL — дозволяємо лише безпечні публічні http(s) посилання.

Protects against SSRF (Server-Side Request Forgery): a user could otherwise make
our server fetch internal addresses like http://localhost or the cloud metadata
endpoint http://169.254.169.254. We block non-http(s) schemes and any private /
loopback / link-local / reserved IP address.
"""

from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlsplit

ALLOWED_SCHEMES = {"http", "https"}


class UnsafeUrlError(ValueError):
    """Raised when a URL is not safe to fetch. / URL небезпечний для завантаження."""


def validate_url(url: str) -> str:
    """Return the URL if it is safe to fetch, else raise UnsafeUrlError.

    UA: Повертає URL, якщо його безпечно завантажувати, інакше викидає помилку.
    """
    url = (url or "").strip()
    parts = urlsplit(url)

    if parts.scheme not in ALLOWED_SCHEMES:
        raise UnsafeUrlError("URL must start with http:// or https://")
    if not parts.hostname:
        raise UnsafeUrlError("URL has no host")

    try:
        infos = socket.getaddrinfo(parts.hostname, parts.port or 0, proto=socket.IPPROTO_TCP)
    except socket.gaierror as exc:
        raise UnsafeUrlError("could not resolve host") from exc

    for info in infos:
        address = ipaddress.ip_address(info[4][0])
        if (
            address.is_private
            or address.is_loopback
            or address.is_link_local
            or address.is_reserved
            or address.is_multicast
            or address.is_unspecified
        ):
            raise UnsafeUrlError("URL points to a non-public address")

    return url
