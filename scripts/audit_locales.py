#!/usr/bin/env python3
"""Validate all authored language pages, links, metadata, and locale parity."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit
import json
import re
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent.parent
ORIGIN='https://glorystarwears.com'
LOCALES={'fr':'fr','es':'es','pt':'pt','ru':'ru','zh-cn':'zh-CN'}
entries={}
for line in (ROOT/'scripts/locales/pages.tsv').read_text().splitlines():
    key,*values=line.split('|');entries[key]=values

def route(key,locale=''):
    path='/' + (key[:-5] if key.endswith('index') else key+'.html')
    return ('/'+locale if locale else '')+path

class Parser(HTMLParser):
    def __init__(self):super().__init__();self.lang='';self.title='';self.intitle=False;self.desc='';self.canonical='';self.alt=[];self.h1=0;self.links=[];self.images=[];self.scripts=[];self.styles=[];self.json=[];self.injson=False;self.jsonparts=[];self.visible=[];self.skip=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='html':self.lang=a.get('lang','')
        if tag=='title':self.intitle=True
        if tag=='meta' and a.get('name')=='description':self.desc=a.get('content','')
        if tag=='link' and a.get('rel')=='canonical':self.canonical=a.get('href','')
        if tag=='link' and a.get('rel')=='alternate' and a.get('hreflang'):self.alt.append((a.get('hreflang'),a.get('href')))
        if tag=='h1':self.h1+=1
        if tag=='a' and a.get('href'):self.links.append(a['href'])
        if tag=='img' and a.get('src'):self.images.append(a['src'])
        if tag=='script':
            if a.get('src'):self.scripts.append(a['src'])
            if a.get('type') in ['application/ld+json','application/json']:self.injson=True;self.jsonparts=[]
            else:self.skip+=1
        if tag=='style':self.skip+=1
        if not self.skip:
            for k in ['src','href']:
                if k in a and str(a[k]).lower().startswith('javascript:'):raise ValueError('javascript URL')
    def handle_endtag(self,tag):
        if tag=='title':self.intitle=False
        if tag=='script':
            if self.injson:self.json.append(''.join(self.jsonparts));self.injson=False
            elif self.skip:self.skip-=1
        if tag=='style' and self.skip:self.skip-=1
    def handle_data(self,data):
        if self.intitle:self.title+=data
        if self.injson:self.jsonparts.append(data)
        elif not self.skip and data.strip():self.visible.append(data.strip())

def local_file(url,current):
    parsed=urlsplit(urljoin(ORIGIN+current,url))
    if parsed.netloc and parsed.netloc!='glorystarwears.com':return None
    path=parsed.path
    if path.endswith('/'):path+='index.html'
    return ROOT/path.lstrip('/')

errors=[];titles={locale:set() for locale in LOCALES};descriptions={locale:set() for locale in LOCALES};parsed={}
for locale,lang in LOCALES.items():
    for index,key in enumerate(entries):
        path=ROOT/locale/(key+'.html');
        if not path.exists():errors.append(f'{path}: missing');continue
        source=path.read_text();p=Parser();p.feed(source);parsed[(locale,key)]=p
        expected_title=entries[key][list(LOCALES).index(locale)+1]+' | GloryStarWear'
        if p.lang!=lang:errors.append(f'{path}: lang {p.lang!r} != {lang!r}')
        if p.title!=expected_title:errors.append(f'{path}: title mismatch')
        if p.title in titles[locale]:errors.append(f'{path}: duplicate title')
        titles[locale].add(p.title)
        if len(p.desc)<(25 if locale=='zh-cn' else 70):errors.append(f'{path}: short description')
        if p.desc in descriptions[locale]:errors.append(f'{path}: duplicate description')
        descriptions[locale].add(p.desc)
        expected_canonical=ORIGIN+route(key,locale)
        if p.canonical!=expected_canonical:errors.append(f'{path}: canonical mismatch')
        expected_alt=[('en',ORIGIN+route(key))]+[(l,ORIGIN+route(key,s)) for s,l in LOCALES.items()]+[('x-default',ORIGIN+route(key))]
        if p.alt!=expected_alt:errors.append(f'{path}: hreflang mismatch')
        if p.h1!=1:errors.append(f'{path}: expected one h1, found {p.h1}')
        menu_links = re.findall(r'<a href="([^"]+)" data-site-language="([^"]+)"[^>]*>', source)
        expected_menu = [(route(key), 'en')]+[(route(key, slug), language) for slug,language in LOCALES.items()]
        if menu_links != expected_menu:errors.append(f'{path}: language menu target mismatch')
        current_links = re.findall(r'<a href="[^"]+" data-site-language="([^"]+)"[^>]*aria-current="true"', source)
        if current_links != [lang]:errors.append(f'{path}: current language state mismatch')
        if '/assets/locales.js?v=20260903-2' not in p.scripts or '/assets/language.js?v=20260903-2' not in p.scripts:errors.append(f'{path}: missing local runtime')
        if '/assets/locales.css?v=20260903-2' not in p.styles and '/assets/locales.css?v=20260903-2' not in source:errors.append(f'{path}: missing locale styles')
        for block in p.json:
            try:json.loads(block)
            except Exception as error:errors.append(f'{path}: invalid JSON: {error}')
        for ref in p.images+p.scripts+[href for href in p.links if not href.startswith(('mailto:','tel:','javascript:'))]:
            target=local_file(ref,route(key,locale))
            if target is not None and not target.exists():errors.append(f'{path}: missing target {ref} -> {target}')
        visible=' '.join(p.visible)
        if locale=='zh-cn' and len(re.findall(r'[\u4e00-\u9fff]',visible))<80:errors.append(f'{path}: insufficient Chinese content')
        if locale=='ru' and len(re.findall(r'[А-Яа-яЁё]',visible))<150:errors.append(f'{path}: insufficient Russian content')
        if locale in ['fr','es','pt'] and len(visible)<500:errors.append(f'{path}: insufficient localized content')
        forbidden=['translate.google','gtranslate','goog-te-combo','gloryStarTranslateInit','Automatic translation']
        for marker in forbidden:
            if marker.lower() in source.lower():errors.append(f'{path}: translation-service marker {marker}')

# English pages must provide the same reciprocal routes and no external translator runtime.
for key in entries:
    path=ROOT/(key+'.html');source=path.read_text();p=Parser();p.feed(source)
    expected=[('en',ORIGIN+route(key))]+[(l,ORIGIN+route(key,s)) for s,l in LOCALES.items()]+[('x-default',ORIGIN+route(key))]
    if p.alt!=expected:errors.append(f'{path}: English hreflang mismatch')
    menu_links = re.findall(r'<a href="([^"]+)" data-site-language="([^"]+)"[^>]*>', source)
    expected_menu = [(route(key), 'en')]+[(route(key, slug), language) for slug,language in LOCALES.items()]
    if menu_links != expected_menu:errors.append(f'{path}: English language menu target mismatch')
    current_links = re.findall(r'<a href="[^"]+" data-site-language="([^"]+)"[^>]*aria-current="true"', source)
    if current_links != ['en']:errors.append(f'{path}: English current language mismatch')
    menu={lang:href for lang,href in re.findall(r'data-site-language="([^"]+)"[^>]*|', '')} if False else None
    for marker in ['translate.google','gtranslate','goog-te-combo','gloryStarTranslateInit']:
        if marker.lower() in source.lower():errors.append(f'{path}: translator marker {marker}')

# Sitemap must contain every indexable localized canonical once.
ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
try:urls=[node.text for node in ET.parse(ROOT/'sitemap-languages.xml').getroot().findall('s:url/s:loc',ns)]
except Exception as error:errors.append(f'sitemap-languages.xml: {error}');urls=[]
if len(urls)!=len(set(urls)):errors.append('sitemap-languages.xml: duplicate URLs')
for (locale,key),page in parsed.items():
    is_noindex='noindex' in (ROOT/locale/(key+'.html')).read_text().split('</head>',1)[0]
    expected=ORIGIN+route(key,locale)
    if (expected in urls)==is_noindex:errors.append(f'sitemap membership mismatch: {expected}')
if f'Sitemap: {ORIGIN}/sitemap-languages.xml' not in (ROOT/'robots.txt').read_text():errors.append('robots.txt: missing language sitemap')

summary={'languages':len(LOCALES),'source_routes':len(entries),'localized_pages':len(parsed),'localized_sitemap_urls':len(urls),'errors':errors}
print(json.dumps(summary,ensure_ascii=False,indent=2))
raise SystemExit(bool(errors))
