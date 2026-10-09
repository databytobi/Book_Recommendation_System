"""
Book cover URL normalization.

The catalog was built from the legacy Goodreads/Amazon export, which stores
cover art at::

    http://images.amazon.com/images/P/<isbn>.01.MZZZZZZZ.jpg

That host now answers **HTTP 403** for every request, so every book cover in
the UI failed to render even though the underlying image still exists.

The same image is served from the modern TLS hostname::

    https://images-na.ssl-images-amazon.com/images/P/<isbn>.01.MZZZZZZZ.jpg

Verified against several ISBNs: the legacy host returned 403 and the rewritten
host returned 200 for each one.

This module performs the rewrite in one place so the books, favorites,
history and recommendations endpoints all stay consistent. Anything that is
not a recognized Amazon cover URL is returned unchanged, so a dataset that is
later migrated to a different image source keeps working.
"""

from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Legacy hosts that no longer serve images.
_DEAD_HOSTS = (
    "http://images.amazon.com/",
    "https://images.amazon.com/",
)

# Working TLS host that serves the identical objects.
_LIVE_HOST = "https://images-na.ssl-images-amazon.com/"


def normalize_cover_url(url: Optional[str]) -> Optional[str]:
    """
    Rewrite a legacy Amazon cover URL to the working TLS hostname.

    Parameters
    ----------
    url : Optional[str]
        Raw `image_url_*` value taken from the catalog.

    Returns
    -------
    Optional[str]
        A browser-loadable https URL, or the original value when no rewrite
        applies. ``None`` and empty strings pass through unchanged so callers
        can keep using ``?? placeholder`` fallbacks.
    """
    if not url or not isinstance(url, str):
        return url

    for dead in _DEAD_HOSTS:
        if url.startswith(dead):
            return _LIVE_HOST + url[len(dead) :]

    return url