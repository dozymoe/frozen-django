from functools import partial
import logging
from mimetypes import guess_type
import os
from urllib.parse import urljoin, urlparse
#-
from bs4 import BeautifulSoup
from django.conf import settings
from django.test.client import RequestFactory
from django.urls import get_resolver, URLResolver
from django.urls import resolve, reverse, NoReverseMatch, Resolver404
from django.utils.module_loading import import_string

_logger = logging.getLogger(__name__)


def walk_resolvers(view_name, *patterns):
    for pat in patterns:
        if isinstance(pat, URLResolver):
            for name in walk_resolvers(view_name, *pat.url_patterns):
                yield name
            continue

        if not pat.name:
            continue
        callback = pat.callback
        cls = getattr(callback, 'view_class', callback)
        if view_name == cls.__module__ + '.' + cls.__qualname__:
            yield pat.name


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


def follow_url(url, host, dest):
    try:
        route_match = resolve(url)
    except Resolver404:
        return None
    view = partial(route_match.func, *route_match.args, **route_match.kwargs)

    middlewares = settings.FROZEN_MIDDLEWARE or ()
    middlewares = (import_string(x) for x in middlewares)
    for middleware in middlewares:
        view = middleware(view)

    request = RequestFactory().get(urljoin(host, url.lstrip('/')))
    response = view(request)
    content = response.render().content.decode()

    filepath = urlparse(url).path
    fullpath = os.path.join(dest, filepath.lstrip('/'))
    os.makedirs(os.path.dirname(fullpath), exist_ok=True)
    with open(fullpath, 'w') as f:
        f.write(content)

    mime, _ = guess_type(url)
    if mime == 'text/html':
        next_url = find_next_html_page(response, content)
    else:
        next_url = find_next_http_page(response)
    if next_url:
        return urlparse(next_url).path
    return None


def generate_static_view(view_name, frozen_host, frozen_dest=None,
        **kwargs):
    base_dir = frozen_dest or settings.FROZEN_ROOT
    resolver = get_resolver()

    for route_name in walk_resolvers(view_name, *resolver.url_patterns):
        try:
            url = reverse(route_name, kwargs=kwargs)
        except NoReverseMatch:
            continue
        # Only if they already have file extensions
        if not os.path.splitext(url)[1]:
            continue

        while url:
            url = follow_url(url, frozen_host, base_dir)
