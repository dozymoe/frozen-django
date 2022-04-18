"""App entry point, main function

.. module:: frozen_django.main
.. moduleauthor:: Fahri Reza <i@dozy.moe>

"""
from functools import partial
import logging
from mimetypes import guess_type
import os
from typing import Mapping
from urllib.parse import urljoin, urlparse
#-
from bs4 import BeautifulSoup
from django.conf import settings
from django.test.client import RequestFactory
from django.urls import get_resolver, URLResolver
from django.urls import get_script_prefix, resolve, Resolver404
from django.urls.resolvers import get_ns_resolver
from django.utils import translation
from django.utils.encoding import iri_to_uri
from django.utils.module_loading import import_string

_logger = logging.getLogger(__name__)


def walk_resolvers(view_name, resolver, ns_pattern, ns_converters):
    """Traverse all of Django routes for find specific view.

    :param view_name: Fully qualified name of view
    :type view_name: str.

    .. note::

       An example of view_name: website.views.Home

    """
    if resolver.pattern.converters:
        sub_ns_converters = ns_converters.copy()
        sub_ns_converters.update(resolver.pattern.converters)
    else:
        sub_ns_converters = ns_converters

    for pat in resolver.url_patterns:
        if isinstance(pat, URLResolver):
            sub_ns_pattern = ns_pattern + pat.pattern.regex.pattern.lstrip('^')\
                    .rstrip('$')
            for result in walk_resolvers(view_name, pat, sub_ns_pattern,
                    sub_ns_converters):
                yield result
            continue

        if pat.lookup_str == view_name:
            if ns_pattern:
                resolver = get_ns_resolver(ns_pattern, resolver,
                        tuple(ns_converters.items()))
            yield resolver, pat.name


def find_next_http_page(response):
    """Check Response's HTTP Headers for Link header.

    :param response: Return value from view
    :type view_name: HttpResponse.

    """
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
    """Check Response's html content for `link` tag with attribute rel="next"

    :param response: Return value from view
    :type view_name: HttpResponse.
    :param content: Text content of response
    :type content: str.

    """
    next_link = find_next_http_page(response)
    if next_link:
        return next_link

    # Scan content for next link (pagination)
    bs = BeautifulSoup(content, 'html.parser') # pylint:disable=invalid-name
    link = bs.find('link', {'rel': 'next'})
    if link:
        return link['href']
    return None


def follow_url(url, host, dest):
    """Capture response body from a url, follow next pagination page

    :param url: Relative url, valid Django route
    :type url: str.
    :param host: Absolute url, base url
    :type host: str.
    :param dest: Output directory for generated files
    :type dest: str.

    .. note::

       An example of url: /index.html

       An example of host: https://example.com/

       An example of dest: /var/www/html

    """
    try:
        route_match = resolve(url)
    except Resolver404:
        return None
    view = partial(route_match.func, *route_match.args, **route_match.kwargs)

    middlewares = getattr(settings, 'FROZEN_MIDDLEWARE', ())
    middlewares = (import_string(x) for x in middlewares)
    for middleware in middlewares:
        view = middleware(view)

    request = RequestFactory(SERVER_NAME=host)\
            .get(urljoin(host, url.lstrip('/')))
    response = view(request)
    content = response.render().content.decode()

    filepath = urlparse(url).path
    fullpath = os.path.join(dest, filepath.lstrip('/'))
    os.makedirs(os.path.dirname(fullpath), exist_ok=True)
    with open(fullpath, 'w', encoding='utf-8') as f: # pylint:disable=invalid-name
        f.write(content)

    mime, _ = guess_type(url)
    if mime == 'text/html':
        next_url = find_next_html_page(response, content)
    else:
        next_url = find_next_http_page(response)
    if next_url:
        return urlparse(next_url).path
    return None


def generate_static_view(view_name, frozen_host, frozen_dest=None, urlconf=None,
        **kwargs):
    """Capture the contents of all urls related to specific view

    :param view_name: Fully qualified name of view
    :type view_name: str
    :param frozen_host: absolute url, base url
    :type frozen_host: str
    :param frozen_dest: output directory for generated files
    :type frozen_dest: str
    :param urlconf: django urls module
    :type urlconf: str

    .. note::

       An example of view_name: website.views.Home

       An example of frozen_host: https://example.com/

       An example of frozen_dest: /var/www/html

       An example of urlconf: project.urls

    """
    if frozen_dest:
        base_dir = frozen_dest
    elif isinstance(settings.FROZEN_ROOT, Mapping):
        domain = urlparse(frozen_host).netloc.split(':')[0]
        base_dir = settings.FROZEN_ROOT[domain]
    else:
        base_dir = settings.FROZEN_ROOT

    resolver = get_resolver(urlconf)
    prefix = get_script_prefix()

    for langcode, _ in settings.LANGUAGES:
        translation.activate(langcode)

        done_urls = set()
        for solver, view in walk_resolvers(view_name, resolver, '', {}):
            url = iri_to_uri(solver._reverse_with_prefix(view, prefix,
                    **kwargs))
            if url in done_urls:
                continue
            done_urls.add(url)

            # Only if they already have file extensions
            if not os.path.splitext(url)[1]:
                continue

            while url:
                url = follow_url(url, frozen_host, base_dir)
