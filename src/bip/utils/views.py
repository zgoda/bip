from typing import Optional
from urllib.parse import urljoin, urlparse

from flask import request, session, url_for


def next_redirect(fallback_endpoint: str, *args, **kwargs) -> str:
    """Find redirect url. The order of search is request params, session and
    finally url for fallback endpoint is returned if none found. Args and
    kwargs are passed intact to endpoint.

    :param fallback_endpoint: full endpoint specification
    :type fallback_endpoint: str
    :return: HTTP path to redirect to
    :rtype: str
    """

    for c in [request.args.get('next'), session.pop('next', None)]:
        if is_redirect_safe(c):
            return c
    return url_for(fallback_endpoint, *args, **kwargs)


def is_redirect_safe(target: Optional[str]) -> bool:
    """Check if redirect is safe, that is using HTTP protocol and is pointing
    to the same site.

    :param target: redirect target url
    :type target: str
    :return: flag signalling whether redirect is safe
    :rtype: bool
    """

    if not target:
        return False
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc
