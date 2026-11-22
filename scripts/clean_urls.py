"""Map source page names to directory URLs without touching visual markup."""
import html
import json
import posixpath
import re
from urllib.parse import urlsplit, urlunsplit


def output_path(path):
    return path if path.endswith('/index.html') or path == 'index.html' else path[:-5] + '/index.html'


def public_path(path):
    output = output_path(path)
    return output[:-10] if output != 'index.html' else ''


def rewrite_page(markup, source, pages, aliases=None):
    aliases = aliases or {}
    old_dir = posixpath.dirname(source)
    new_dir = posixpath.dirname(output_path(source))

    def rewrite(value):
        decoded = html.unescape(value)
        parts = urlsplit(decoded)
        if parts.scheme or parts.netloc or not parts.path:
            # Canonical and social metadata on this site's own host.
            if parts.scheme in ('https', 'http') and parts.netloc in ('kuantum.abdullahaltun.com.tr', 'kuantumsayisalakademi.com', 'www.kuantumsayisalakademi.com'):
                key = parts.path.lstrip('/')
                if key in pages:
                    return value.replace(parts.path, '/' + public_path(key), 1)
            return value
        if parts.path.startswith('/'):
            resolved = parts.path.lstrip('/')
        else:
            resolved = posixpath.normpath(posixpath.join(old_dir, parts.path))
        destination = public_path(aliases.get(resolved, resolved)) if resolved in pages else resolved
        is_directory = resolved in pages or parts.path.endswith('/')
        if parts.path.startswith('/'):
            path = '/' + destination
        else:
            path = posixpath.relpath(destination or '.', new_dir or '.')
            if is_directory:
                path = './' if path == '.' else path.rstrip('/') + '/'
        return html.escape(urlunsplit(('', '', path, parts.query, parts.fragment)), quote=False)

    markup = re.sub(r'''(\b(?:href|src|action|data-sticky)=)(["'])(.*?)\2''',
                    lambda m: m[1] + m[2] + rewrite(m[3]) + m[2], markup)
    markup = re.sub(r'\bsrcset="([^"]+)"', lambda m: 'srcset="' + ', '.join(
        rewrite(item.strip().split()[0]) + ' ' + ' '.join(item.strip().split()[1:])
        for item in m[1].split(',')) + '"', markup)
    # CSS background URLs inside the document (external CSS paths stay unchanged).
    markup = re.sub(r'''url\((["']?)([^)'"\s]+)\1\)''', lambda m: 'url(' + m[1] + rewrite(m[2]) + m[1] + ')', markup)
    # Runtime asset roots are embedded in Elementor JSON, not in HTML attributes.
    def script(match):
        body = match[2]
        def asset(m):
            raw = m[2].replace('\\/', '/')
            fixed = rewrite(raw)
            return m[1] + fixed.replace('/', '\\/') + m[3]
        body = re.sub(r'''(["'])((?:\.\./)*(?:assets|wp-content|wp-includes)(?:/|\\/)[^"']*)(["'])''', asset, body)
        return match[1] + body + match[3]
    markup = re.sub(r'(<script\b[^>]*>)(.*?)(</script>)', script, markup, flags=re.S)
    # SEO URLs in metadata and JSON are changed only when they refer to known pages.
    for path in sorted(pages, key=len, reverse=True):
        for domain in ('https://kuantum.abdullahaltun.com.tr/', 'https://kuantumsayisalakademi.com/', 'https://www.kuantumsayisalakademi.com/'):
            markup = markup.replace(domain + path, domain + public_path(path))
    return markup


def legacy_redirect(source):
    target = './' + posixpath.basename(source)[:-5] + '/'
    return ('<!doctype html>\n<html lang="tr"><head><meta charset="utf-8">'
            '<meta name="robots" content="noindex">'
            '<meta http-equiv="refresh" content="0;url=' + target + '">'
            '<link rel="canonical" href="' + target + '"><title>Yönlendiriliyor</title>'
            '<script>location.replace(' + json.dumps(target) + ' + location.search + location.hash);</script>'
            '</head><body><a href="' + target + '">Sayfaya devam et</a></body></html>\n')
