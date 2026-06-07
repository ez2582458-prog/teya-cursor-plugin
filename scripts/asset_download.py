#!/usr/bin/env python3
"""Robust image download helpers for MCP/CDN asset URLs."""
from __future__ import annotations

import re
import time
import urllib.request


DEFAULT_HEADERS = {
    "User-Agent": "TeyaAssetDownloader/1.0",
    "Cache-Control": "no-cache",
}


def _request(url: str, *, headers: dict[str, str] | None = None, timeout: int = 20) -> urllib.response.addinfourl:
    merged = dict(DEFAULT_HEADERS)
    if headers:
        merged.update(headers)
    return urllib.request.urlopen(urllib.request.Request(url, headers=merged), timeout=timeout)


def _read_exact_range(url: str, start: int, end: int, *, retries: int, timeout: int) -> bytes:
    expected = end - start + 1
    last_error: Exception | None = None

    for attempt in range(1, retries + 1):
        try:
            with _request(url, headers={"Range": f"bytes={start}-{end}"}, timeout=timeout) as response:
                data = response.read(expected)
                if len(data) != expected:
                    raise TimeoutError(f"short range read {start}-{end}: got {len(data)} of {expected}")
                return data
        except Exception as exc:  # noqa: BLE001 - retry network/CDN failures.
            last_error = exc
            time.sleep(min(2.0, 0.25 * attempt))

    raise RuntimeError(f"failed to read range {start}-{end} from {url}: {last_error}")


def _content_range_total(value: str | None) -> int | None:
    if not value:
        return None
    match = re.search(r"/(\d+)\s*$", value)
    if not match:
        return None
    return int(match.group(1))


def probe_url(url: str, *, timeout: int = 15) -> dict[str, str | int | None]:
    """Return cheap evidence about a remote asset without reading the full body."""
    with _request(url, headers={"Range": "bytes=0-15"}, timeout=timeout) as response:
        first = response.read(16)
        return {
            "status": response.status,
            "content_type": response.headers.get("content-type"),
            "content_length": response.headers.get("content-length"),
            "content_range": response.headers.get("content-range"),
            "total_bytes": _content_range_total(response.headers.get("content-range")),
            "signature_hex": first.hex(),
        }


def download_url_bytes(
    url: str,
    *,
    timeout: int = 20,
    retries: int = 4,
    chunk_size: int = 16 * 1024,
    max_bytes: int = 25 * 1024 * 1024,
) -> tuple[bytes, dict[str, str | int | None]]:
    """Download URL bytes using Range chunks when the CDN is unstable."""
    evidence = probe_url(url, timeout=timeout)
    total = evidence.get("total_bytes")

    if isinstance(total, int) and total > 0:
        if total > max_bytes:
            raise RuntimeError(f"remote asset is too large: {total} bytes > {max_bytes}")

        chunks: list[bytes] = []
        for start in range(0, total, chunk_size):
            end = min(total - 1, start + chunk_size - 1)
            chunks.append(_read_exact_range(url, start, end, retries=retries, timeout=timeout))
        data = b"".join(chunks)
        if len(data) != total:
            raise RuntimeError(f"range download length mismatch: got {len(data)} of {total}")
        return data, evidence

    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            with _request(url, timeout=timeout) as response:
                data = response.read(max_bytes + 1)
                if len(data) > max_bytes:
                    raise RuntimeError(f"remote asset exceeds max_bytes={max_bytes}")
                evidence.update(
                    {
                        "status": response.status,
                        "content_type": response.headers.get("content-type"),
                        "content_length": response.headers.get("content-length"),
                    }
                )
                return data, evidence
        except Exception as exc:  # noqa: BLE001 - retry network/CDN failures.
            last_error = exc
            time.sleep(min(2.0, 0.25 * attempt))

    raise RuntimeError(f"failed to download {url}: {last_error}")

