"""Nonvisual performance and accessibility improvements for generated pages."""
import html
from functools import lru_cache
import json
from pathlib import Path
import posixpath
import re
import struct
from urllib.parse import unquote, urlsplit


def improve(markup, path, root, source):
    prefix = '../' * (len(Path(path).parts)-1)
    mapping = json.loads((source/'image-optimizations.json').read_text())
    for old,new in mapping.items():
        markup = markup.replace(prefix+old, prefix+new)
    def image(match):
        tag=match[0]
        if not re.search(r'\balt=',tag):tag=tag[:-1]+' alt="">'
        if 'id="okapi-wasb-icon"' in tag:
            tag=tag.replace(' alt=""',' alt="WhatsApp"')
        src=re.search(r'\bsrc="([^"]+)"',tag)
        if src and not re.search(r'\bwidth=',tag):
            target=(root/Path(path).parent/unquote(src[1])).resolve()
            if target.is_file():
                data=target.read_bytes();size=None
                if target.suffix=='.svg':
                    dims=re.search(r'<svg[^>]*width="([0-9.]+)"[^>]*height="([0-9.]+)"',data.decode())
                    if dims:size=tuple(round(float(v)) for v in dims.groups())
                elif data[:8]==b'\x89PNG\r\n\x1a\n':size=struct.unpack('>II',data[16:24])
                elif data[:4]==b'RIFF' and data[8:12]==b'WEBP':
                    # sips is used only at build time for image metadata.
                    info=image_info(str(target))
                    nums=re.findall(r'pixel(?:Width|Height): (\d+)',info)
                    if len(nums)==2:size=tuple(map(int,nums))
                if size:tag=tag[:-1]+f' width="{size[0]}" height="{size[1]}">'
        return tag
    markup=re.sub(r'<img\b[^>]*>',image,markup)
    if path == 'index.html':
        for container,media in [('ef76a59','(min-width: 1025px)'),('47da38ea','(max-width: 1024px)')]:
            section=markup.split('data-id="'+container+'"',1)[-1]
            first=re.search(r'<img[^>]*src="([^"]+)"',section)
            if first:
                preload='<link rel="preload" as="image" href="'+first[1]+'" media="'+media+'" fetchpriority="high">'
                markup=markup.replace('</head>',preload+'\n</head>')

    for name in ('all.css','v4-shims.css'):
        markup=markup.replace('https://use.fontawesome.com/releases/v7.0.1/css/'+name,prefix+'assets/kuantum/fontawesome/css/'+name)
    # Font Awesome's default block period is unnecessary for decorative icons.
    # Search and icon-only links need an explicit accessible name.
    markup=re.sub(r'<a\b[^>]*>.*?</a>', lambda m: name_link(m[0]),markup,flags=re.S)
    # Keep heading tags/styles; repair the accessible heading outline independently.
    if path=='index.html':
        previous=0
        def heading(m):
            nonlocal previous
            tag=m[0];original=int(m[1]);level=min(original,previous+1) if previous else 1
            if previous and original==1:level=2
            if 'kuantum-home-title' in tag:level=1
            previous=level
            return tag[:-1]+f' aria-level="{level}">'
        markup=re.sub(r'<h([1-6])\b[^>]*>',heading,markup)
    # No forms on the home page: their styles cannot affect its layout.
    if path=='index.html':
        markup=re.sub(r'<link\b[^>]*(?:contact-form-7|wpcf7-redirect)[^>]*>','',markup)
    markup=markup.replace('</head>',f'<link rel="stylesheet" href="{prefix}assets/kuantum/site-quality.css">\n<script src="{prefix}assets/kuantum/site-quality.js" defer></script>\n</head>')
    return bundle_styles(markup, path, root)


def name_link(tag):
    if re.search(r'\baria-label=|\baria-labelledby=',tag):return tag
    open_end=tag.index('>');body=tag[open_end+1:]
    text=html.unescape(re.sub(r'<[^>]+>','',body)).strip()
    if text:return tag
    alts=[html.unescape(a).strip() for a in re.findall(r'\balt="([^"]*)"',body)]
    if any(alts):return tag
    href=re.search(r'\bhref="([^"]*)"',tag[:open_end])
    if not href:return tag
    url=href[1]
    label='Kurs ara' if 'kurs-arama' in url else 'Programı incele' if 'kursu' in url else 'Hakkımızda' if 'hakkimizda' in url else 'Bilgi al' if 'kayit' in url else 'Anasayfa' if 'index.html' in url else 'Detayları görüntüle'
    return tag[:open_end]+f' aria-label="{label}"'+tag[open_end:]

@lru_cache(maxsize=512)
def image_info(path):
    data=Path(path).read_bytes()
    kind=data[12:16]
    if kind==b'VP8X':
        width=int.from_bytes(data[24:27],'little')+1
        height=int.from_bytes(data[27:30],'little')+1
    elif kind==b'VP8L':
        bits=int.from_bytes(data[21:25],'little')
        width=(bits & 0x3fff)+1
        height=((bits >> 14) & 0x3fff)+1
    elif kind==b'VP8 ':
        i=data.find(b'\x9d\x01\x2a',20)+3
        width=int.from_bytes(data[i:i+2],'little') & 0x3fff
        height=int.from_bytes(data[i+2:i+4],'little') & 0x3fff
    else:
        return ''
    return f'pixelWidth: {width}\npixelHeight: {height}' 


def bundle_styles(markup, path, root):
    """Keep stylesheet cascade order, rebase CSS URLs, use a content-hashed bundle."""
    import hashlib
    from urllib.parse import urlsplit
    pieces=[]
    bundle_dir=root/'assets/kuantum/generated'
    def collect(match):
        tag=match[0]
        if tag.startswith('<style'):
            css=re.sub(r'^<style\b[^>]*>|</style>$','',tag,flags=re.S)
            base=root/Path(path).parent
        else:
            if not re.search(r'''\brel=["']stylesheet["']''',tag):return tag
            src=re.search(r'''\bhref=(["'])(.*?)\1''',tag)
            if not src:return tag
            parts=urlsplit(html.unescape(src[2]))
            if parts.scheme or parts.netloc:return tag
            file=root/Path(path).parent/unquote(parts.path)
            if not file.is_file():return tag
            css=file.read_text();base=file.parent
        def css_url(m):
            value=m[2];parts=urlsplit(value)
            if parts.scheme or parts.netloc or value.startswith('#'):return m[0]
            target=root/unquote(parts.path).lstrip('/') if parts.path.startswith('/') else base/unquote(parts.path)
            fixed=posixpath.relpath(target,bundle_dir)
            # Files exported with encoded '?' must keep that character encoded.
            from urllib.parse import quote
            fixed=quote(fixed,safe='/._-')
            if parts.query:fixed+='?'+parts.query
            if parts.fragment:fixed+='#'+parts.fragment
            return 'url("'+fixed+'")'
        css=re.sub(r'''url\(\s*(["']?)([^)"']+)\1\s*\)''',css_url,css)
        css=re.sub(r'/\*(?!\!).*?\*/','',css,flags=re.S)
        css=css.replace('font-display:block','font-display:swap')
        css=re.sub(r'@charset\s+[^;]+;','',css)
        css=re.sub(r'\s+',' ',css).strip()
        # Do not rewrite tokens/calculations or selectors; only remove comments/whitespace.
        pieces.append(css)
        return ''
    result=re.sub(r'<style\b[^>]*>.*?</style>|<link\b[^>]*>',collect,markup,flags=re.S)
    data='\n'.join(pieces)+'\n';digest=hashlib.sha256(data.encode()).hexdigest()[:16]
    bundle_dir.mkdir(parents=True,exist_ok=True);file=bundle_dir/(digest+'.css')
    if not file.exists():file.write_text(data)
    prefix='../'*(len(Path(path).parts)-1)
    result=re.sub(r'(?m)^[\t ]+$','',result)
    return result.replace('</head>',f'<link rel="stylesheet" href="{prefix}assets/kuantum/generated/{digest}.css">\n</head>')


def defer_scripts(markup, path, root):
    import hashlib
    directory=root/'assets/kuantum/generated'
    prefix='../'*(len(Path(path).parts)-1)
    def script(m):
        attrs,body=m[1],m[2]
        if re.search(r'type=["\'](?:application/|speculationrules|module)',attrs):return m[0]
        if re.search(r'\bsrc=',attrs):
            attrs=re.sub(r'\s+(?:defer|async)(?:=["\'][^"\']*["\'])?','',attrs)
            return '<script'+attrs+' defer>'+body+'</script>'
        if not body.strip():return m[0]
        digest=hashlib.sha256(body.encode()).hexdigest()[:16]
        file=directory/(digest+'.js')
        if not file.exists():file.write_text(body)
        return '<script'+attrs+' src="'+prefix+'assets/kuantum/generated/'+digest+'.js" defer></script>'
    return re.sub(r'<script\b([^>]*)>(.*?)</script>',script,markup,flags=re.S)
