"""Page-specific SEO and truthful business structured data, managed in JSON."""
import html
import json
import re
from clean_urls import public_path


def apply_seo(markup, path, source):
    config=json.loads((source/'seo.json').read_text())
    business=json.loads((source/'site.json').read_text())
    primary=config['aliases'].get(path,path)
    settings=config['pages'][primary]
    domain=config['domain'].rstrip('/')
    canonical=domain+'/'+public_path(primary)
    title,description=settings['title'],settings['description']
    markup=re.sub(r'<title>.*?</title>','<title>'+html.escape(title)+'</title>',markup,flags=re.S)
    # Remove old SEO metadata, retaining image and locale metadata.
    def remove(m):
        tag=m[0]
        keys=['description','robots','og:title','og:description','og:url','twitter:title','twitter:description']
        return '' if any(re.search(r'''\b(?:name|property)=["']'''+re.escape(k)+r'''["']''',tag) for k in keys) else tag
    markup=re.sub(r'<meta\b[^>]*>',remove,markup)
    markup=re.sub(r'''<link\b[^>]*rel=["']canonical["'][^>]*>''','',markup)
    robots='index, follow, max-image-preview:large' if settings['index'] else 'noindex, follow'
    tags=[f'<meta name="description" content="{html.escape(description,quote=True)}">',f'<meta name="robots" content="{robots}">',f'<link rel="canonical" href="{canonical}">']
    for prop,value in [('og:title',title),('og:description',description),('og:url',canonical)]:
        tags.append(f'<meta property="{prop}" content="{html.escape(value,quote=True)}">')
    for prop,value in [('twitter:title',title),('twitter:description',description)]:
        tags.append(f'<meta name="{prop}" content="{html.escape(value,quote=True)}">')
    org_id=domain+'/#academy'
    org={'@type':['EducationalOrganization','LocalBusiness'],'@id':org_id,'name':business['business_name'],'url':domain+'/',
         'telephone':business['contact_tel'].removeprefix('tel:'),'email':business['contact_email'],
         'logo':domain+'/assets/kuantum/akademi-logo-atom-k.png',
         'image':domain+'/assets/kuantum/paylasim-atom-k.jpg',
         'address':{'@type':'PostalAddress','streetAddress':business['address_street'],'addressLocality':business['address_locality'],'addressRegion':business['address_region'],'addressCountry':business['address_country']},
         'hasMap':html.unescape(business['contact_map']),
         'areaServed':{'@type':'City','name':'Eskişehir'}}
    website={'@type':'WebSite','@id':domain+'/#website','url':domain+'/','name':business['business_name'],'inLanguage':'tr-TR','publisher':{'@id':org_id}}
    webpage={'@type':settings['type'],'@id':canonical+'#webpage','url':canonical,'name':title,'description':description,'inLanguage':'tr-TR','isPartOf':{'@id':domain+'/#website'},'about':{'@id':org_id}}
    graph=[org,website,webpage]
    if primary!='index.html':
        crumbs=[{'@type':'ListItem','position':1,'name':'Anasayfa','item':domain+'/'}]
        if settings.get('course_name'):
            crumbs.append({'@type':'ListItem','position':2,'name':'Kurslarımız','item':domain+'/kurslar/'})
        crumbs.append({'@type':'ListItem','position':len(crumbs)+1,'name':settings.get('course_name',title.split(' | ')[0]),'item':canonical})
        graph.append({'@type':'BreadcrumbList','@id':canonical+'#breadcrumb','itemListElement':crumbs})
        webpage['breadcrumb']={'@id':canonical+'#breadcrumb'}
    if settings.get('course_name'):
        graph.append({'@type':'Course','@id':canonical+'#course','name':settings['course_name'],'description':description,'url':canonical,'provider':{'@id':org_id},'inLanguage':'tr-TR'})
    data=json.dumps({'@context':'https://schema.org','@graph':graph},ensure_ascii=False).replace('<','\\u003c')
    tags.append('<script type="application/ld+json" id="kuantum-structured-data">'+data+'</script>')
    return markup.replace('</head>','\n'.join(tags)+'\n</head>')
