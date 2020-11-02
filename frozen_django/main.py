import logging
from mimetypes import guess_type
import os
from urllib.parse import urljoin, urlparse
#-
from bs4 import BeautifulSoup
from django.conf import settings
from django.test.client import RequestFactory
from django.urls import get_urlconf, get_resolver, URLPattern
from django.urls import reverse, NoReverseMatch
from django.utils.module_loading import import_string

_logger = logging.getLogger(__name__)


def walk_resolvers(view_name, *patterns):
    for pat in patterns:
        if isinstance(pat, URLPattern):
            if not pat.name:
                continue
            callback = pat.callback
            cls = getattr(callback, 'view_class', callback)
            if view_name == cls.__module__ + '.' + cls.__qualname__:
                yield pat.name, callback
            continue

        for name, callback in walk_resolvers(view_name, *pat.url_patterns):
            yield name, callback


def find_next_http_page(response):
    try:
        header = response['Link']
    except KeyError:
        header = None
    if not header:
        return None
    links = [x.strip() for x in header.split(',')]
    for link in links:
        url, *opts = [x.strip() for x in link.split(';')]
        for opt in opts:
            key, val = opt.split('=')
            val = val.strip('\'"')
            if key == 'rel' and val == 'next':
                return url.strip('<>')
    return None


def find_next_html_page(response, content):
    next_link = find_next_http_page(response)
    if next_link:
        return next_link

    # Scan content for next link (pagination)
    bs = BeautifulSoup(content, 'html.parser')
    link = bs.find('link', {'rel': 'next'})
    if link:
        return link['href']
    return None


def follow_url(url, view, frozen_dest):
    request = RequestFactory().get(url)

    middlewares = settings.FROZEN_MIDDLEWARE or ()
    middlewares = (import_string(x) for x in middlewares)
    for middleware in middlewares:
        view = middleware(view)

    response = view(request)
    content = response.render().content.decode()

    filepath = urlparse(url).path
    fullpath = os.path.join(frozen_dest, filepath.lstrip('/'))
    os.makedirs(os.path.dirname(fullpath), exist_ok=True)
    with open(fullpath, 'w') as f:
        f.write(content)

    mime, _ = guess_type(url)
    if mime == 'text/html':
        return find_next_html_page(response, content)
    return find_next_http_page(response)


def generate_static_view(view_name, frozen_host=None, frozen_dest=None,
        **kwargs):
    base_url = frozen_host or settings.FROZEN_URL
    base_dir = frozen_dest or settings.FROZEN_ROOT
    urlconf = get_urlconf()
    resolver = get_resolver(urlconf)

    for route_name, view in walk_resolvers(view_name, *resolver.url_patterns):
        try:
            url = reverse(route_name, kwargs=kwargs)
        except NoReverseMatch:
            continue
        # Only if they already have file extensions
        if not os.path.splitext(url)[1]:
            continue
        url = urljoin(base_url, url.lstrip('/'))

        while url:
            url = follow_url(url, view, base_dir)
