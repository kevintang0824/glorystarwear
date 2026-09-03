#!/usr/bin/env python3
"""Render authored language editions. No network calls or translation services."""
from pathlib import Path
from html import escape
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit
import json
import re
import xml.etree.ElementTree as ET
from site_chrome import site_header_markup

ROOT = Path(__file__).resolve().parent.parent
ORIGIN = 'https://glorystarwears.com'
VERSION = '20260903-2'
LOCALES = [('fr','fr','Français','🇫🇷','FR'),('es','es','Español','🇪🇸','ES'),('pt','pt','Português','🇵🇹','PT'),('ru','ru','Русский','🇷🇺','RU'),('zh-cn','zh-CN','简体中文','🇨🇳','中文')]

def table(name):
    result = {}
    for line in (ROOT / 'scripts/locales' / name).read_text().splitlines():
        if not line.strip(): continue
        key, *values = line.split('|')
        if key in result: raise ValueError(f'Duplicate key: {key}')
        if len(values) != (6 if name == 'pages.tsv' else 5): raise ValueError(f'Invalid columns: {key}')
        result[key] = values
    return result

PAGES = table('pages.tsv')
UI = table('ui.tsv')
GROUPS = table('groups.tsv')

def path_for(key):
    return '/' + (key[:-5] if key.endswith('index') else key + '.html')

def local_path(key, locale=''):
    return ('/' + locale if locale else '') + path_for(key)

class Source(HTMLParser):
    def __init__(self, key):
        super().__init__(); self.key=key; self.images=[]; self.downloads=[]; self.in_main=False; self.noindex=False
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=='main':self.in_main=True
        if tag=='meta' and a.get('name')=='robots': self.noindex='noindex' in a.get('content','')
        if tag=='img' and self.in_main and a.get('src'):
            image=dict(a); image['src']=urlsplit(urljoin(ORIGIN+path_for(self.key),a['src'])).path
            if (ROOT/image['src'].lstrip('/')).exists():self.images.append(image)
        if tag=='a' and self.in_main and re.search(r'\.(csv|pdf|xlsx?)(?:\?|$)',a.get('href','')):
            url=urljoin(ORIGIN+path_for(self.key),a['href'])
            if url.startswith(ORIGIN):self.downloads.append(urlsplit(url).path)
    def handle_endtag(self,tag):
        if tag=='main':self.in_main=False

SOURCES={}
for key in PAGES:
    source_path=ROOT/(key+'.html')
    if not source_path.exists():raise ValueError(f'Missing English source: {key}')
    parser=Source(key);parser.feed(source_path.read_text());SOURCES[key]=parser
english_pages={p.relative_to(ROOT).with_suffix('').as_posix() for folder in ['', 'products', 'resources', 'blog'] for p in (ROOT/folder).glob('*.html')}
if english_pages != set(PAGES): raise ValueError(f'Incomplete route catalogue: {english_pages ^ set(PAGES)}')

def e(value):return escape(str(value),quote=True)
def picture(key, lazy=False):
    images=SOURCES[key].images
    item=images[0] if images else {'src':'/assets/images/hero-brand-campaign.jpg','width':'1672','height':'941'}
    src=item['src']; avif=str(Path(src).with_suffix('.avif'))
    source=f'<source srcset="{e(avif)}" type="image/avif">' if (ROOT/avif.lstrip('/')).exists() else ''
    return f'<picture>{source}<img src="{e(src)}" alt="{e(title(key))}" width="{e(item.get("width",1672))}" height="{e(item.get("height",941))}" {"loading=lazy" if lazy else "fetchpriority=high"} decoding="async"></picture>'

def text(key):return UI[key][INDEX]
def group_text(group,part):return GROUPS[group+'.'+part][INDEX]
def title(key):return PAGES[key][INDEX+1]
def link(key,label=None,cls=''):
    return f'<a class="{cls}" href="{local_path(key,LOCALE)}">{e(label or title(key))}</a>'
def button(key,label):return link(key,label,'button primary')

def alternate_links(key):
    entries=[('en','')]+[(lang,slug) for slug,lang,*_ in LOCALES]+[('x-default','')]
    return '\n'.join(f'    <link rel="alternate" hreflang="{lang}" href="{ORIGIN}{local_path(key,slug)}">' for lang,slug in entries)

def language_menu(key):
    menu=re.search(r'<details class="language-switcher"[\s\S]*?</details>',site_header_markup(path_for(key))).group()
    menu=menu.replace('aria-current="true"','')
    menu=menu.replace(f'data-site-language="{LANG}"',f'data-site-language="{LANG}" aria-current="true"')
    menu=menu.replace('Select website language',text('language_label'))
    menu=menu.replace('>🇺🇸</span><span class="language-current-name"','>'+FLAG+'</span><span class="language-current-name"',1)
    menu=menu.replace('data-language-name>English','data-language-name>'+NAME).replace('data-language-code aria-hidden="true">EN','data-language-code aria-hidden="true">'+CODE)
    return menu

def header(key):
    nav=[('products/index','nav_products'),('sportswear-manufacturer','nav_manufacturing'),('customization','nav_customization'),('fabrics','nav_fabrics'),('process','nav_process'),('resources/index','nav_resources')]
    nav_markup=''.join(link(page,text(label)) for page,label in nav)
    brand=f'<a class="brand" href="/{LOCALE}/"><span class="brand-mark">GS</span><span class="brand-name">GloryStarWear<small>{e(text("brand_tagline"))}</small></span></a>'
    return f'''<a class="skip-link" href="#main-content">{e(text('skip'))}</a>
<header class="site-header" data-header><div class="site-header-shell">{brand}<nav class="desktop-nav" aria-label="{e(text('nav_label'))}">{nav_markup}</nav><div class="header-actions">{language_menu(key)}<a class="header-cta" href="/{LOCALE}/contact.html#quote-form">{e(text('quote'))}</a><button class="menu-toggle" type="button" data-menu-toggle aria-label="{e(text('menu_label'))}" aria-controls="mobile-navigation" aria-expanded="false"><i data-lucide="menu"></i></button></div></div></header>
<nav class="mobile-nav" id="mobile-navigation" data-mobile-nav aria-hidden="true" inert aria-label="{e(text('mobile_label'))}">{nav_markup}{link('quality',text('nav_quality'))}{link('faq',text('nav_faq'))}{link('contact',text('nav_contact'))}</nav>'''

def footer():
    return f'''<footer class="site-footer"><div class="site-footer-shell"><div class="footer-brand"><a class="brand" href="/{LOCALE}/"><span class="brand-mark">GS</span><span class="brand-name">GloryStarWear</span></a><p>{e(text('footer_body'))}</p><a href="mailto:kevin@glorystarwears.com">kevin@glorystarwears.com</a><p><a href="https://wa.me/8618020755949" target="_blank" rel="noreferrer">WhatsApp · +86 18020755949</a></p></div><nav class="footer-links"><div class="footer-link-group">{link('products/index',text('all_products'))}{link('sportswear-manufacturer',text('nav_manufacturing'))}{link('quality',text('nav_quality'))}</div><div class="footer-link-group">{link('resources/index',text('nav_resources'))}{link('blog/index',text('nav_blog'))}{link('faq',text('nav_faq'))}</div><div class="footer-link-group">{link('contact',text('nav_contact'))}{link('privacy',text('nav_privacy'))}{link('editorial-policy',text('nav_editorial'))}<span>© 2026 GloryStarWear. {e(text('rights'))}</span></div></nav></div></footer>'''

def hero(key,description,image=True):
    return f'''<section class="locale-hero {'locale-hero-text' if not image else ''}"><div class="locale-hero-copy"><nav class="breadcrumbs">{link('index',text('nav_home'))}<span aria-hidden="true"> / </span><span>{e(title(key))}</span></nav><p class="eyebrow">{e(text('home_eyebrow') if key=='index' else text('product_eyebrow'))}</p><h1>{e(title(key))}</h1><p>{e(description)}</p><div class="hero-actions">{button('contact',text('quote'))}{link('products/index',text('explore'),'button secondary')}</div></div>{f'<figure>{picture(key)}<figcaption>{e(text("image_note"))}</figcaption></figure>' if image else ''}</section>'''

def steps():
    cards=''.join(f'<article><span class="locale-step-number">0{i}</span><h3>{e(text(f"step{i}"))}</h3><p>{e(text(f"step{i}_body"))}</p></article>' for i in range(1,5))
    return f'<section class="section"><div class="section-heading"><h2>{e(text("process_heading"))}</h2></div><div class="locale-steps">{cards}</div></section>'

def faqs():
    items=''.join(f'<details><summary>{e(text("faq_"+key+"_q"))}</summary><p>{e(text("faq_"+key+"_a"))}</p></details>' for key in ['moq','sample','time'])
    return f'<section class="section locale-faq"><div class="section-heading"><h2>{e(text("faq_heading"))}</h2></div>{items}</section>'

def cta(key):
    href=local_path('contact',LOCALE)+'?product='+key.split('/')[-1]+'#quote-form'
    return f'<section class="product-cta"><div><h2>{e(text("cta_heading"))}</h2><p>{e(text("cta_body"))}</p></div><a class="button primary" href="{href}">{e(text("ask_product"))}</a></section>'

PRODUCTS=[k for k,v in PAGES.items() if k.startswith('products/') and v[0]!='catalog']

def cards(keys,filters=False):
    return '<div class="locale-product-grid">'+''.join(f'<article class="locale-product-card" {"data-local-product" if filters else ""}><a href="{local_path(key,LOCALE)}">{picture(key,True)}<div><span>{e(group_text(PAGES[key][0],"title")) if key in PRODUCTS else e(text("guide_label"))}</span><h3>{e(title(key))}</h3><p>{e(text("details"))} <span aria-hidden="true">↗</span></p></div></a></article>' for key in keys)+'</div>'

def specs(group):
    items=group_text(group,'points').split(';')
    return f'<section class="section locale-specs"><div class="section-heading"><p class="eyebrow">{e(group_text(group,"title"))}</p><h2>{e(text("spec_heading"))}</h2><p>{e(text("spec_intro"))}</p></div><div class="locale-spec-grid">'+''.join(f'<article><span>0{i+1}</span><h3>{e(item)}</h3></article>' for i,item in enumerate(items))+'</div></section>'

def contact():
    fields=[('name','name','text',True),('email','email','email',True),('phone','phone','tel',False),('quantity','quantity','text',False),('market','market','text',False),('timeline','timeline','text',False)]
    inputs=''.join(f'<label>{e(text(label))}<input name="{name}" type="{kind}" maxlength="{180 if name=="email" else 120}" autocomplete="{name if name in ["name","email"] else "tel" if name=="phone" else "off"}" {"required" if required else ""}></label>' for name,label,kind,required in fields)
    options=''.join(f'<option value="{key.split("/")[-1]}">{e(title(key))}</option>' for key in PRODUCTS)
    return hero('contact',text('contact_intro'),False)+f'''<section class="section locale-contact" id="quote-form"><form class="quote-form" data-native-quote><h2>{e(text('quote'))}</h2><div class="quote-form-grid">{inputs}<label>{e(text('buyer'))}<select name="buyerType" required><option value="Established brand">{e(text('buyer_brand'))}</option><option value="Club, school or team">{e(text('buyer_team'))}</option><option value="Dealer or distributor">{e(text('buyer_distributor'))}</option></select></label><label>{e(text('product'))}<select name="product" required>{options}</select></label></div><label>{e(text('message'))}<textarea name="message" rows="6" maxlength="3000" placeholder="{e(text('message_hint'))}" required></textarea></label><label>{e(text('reference'))}<input name="referenceLink" type="url" maxlength="500" placeholder="https://"></label><label>{e(text('files'))}<input name="referenceFiles" type="file" accept=".pdf,.csv,.xlsx,.xls,.doc,.docx,.png,.jpg,.jpeg,.webp" multiple><small>{e(text('files_note'))}</small></label><label class="form-honeypot" aria-hidden="true">Website<input name="companyWebsite" type="text" tabindex="-1" autocomplete="off"></label><label class="quote-consent"><input type="checkbox" name="consent" required><span>{e(text('consent'))} {link('privacy',text('nav_privacy'))}</span></label><div data-native-turnstile hidden></div><div class="quote-form-actions"><button type="submit" class="button primary" data-native-submit hidden>{e(text('submit'))}</button><button type="button" class="button whatsapp" data-native-action="whatsapp">{e(text('whatsapp'))}</button><button type="button" class="button secondary" data-native-action="email">{e(text('email_action'))}</button><button type="button" class="button secondary" data-native-action="copy">{e(text('copy'))}</button><button type="button" class="button secondary" data-native-action="share" hidden>{e(text('share'))}</button></div><p class="form-note" role="status" aria-live="polite" data-native-status>{e(text('contact_intro'))}</p><noscript><p><a href="mailto:kevin@glorystarwears.com">kevin@glorystarwears.com</a> · <a href="https://wa.me/8618020755949">WhatsApp</a></p></noscript></form></section>'''+specs('commercial')

def body(key):
    role=PAGES[key][0]
    if role=='home':
        featured=['products/yoga-wear','products/training-wear','products/basketball-wear','products/football-kits','products/running-wear','products/cycling-wear','products/athleisure','products/accessories']
        return hero(key,text('home_intro'))+f'<section class="section"><div class="section-heading"><p class="eyebrow">GloryStarWear</p><h2>{e(text("collections"))}</h2><p>{e(text("collections_intro"))}</p></div>{cards(featured)}<div class="locale-section-action">{link("products/index",text("all_products"),"button secondary")}</div></section>'+steps()+faqs()+cta(key)
    if role=='contact':return contact()
    if role=='catalog':
        keys=PRODUCTS
        if key.endswith('new-products'):
            expanded={item['slug'] for item in json.loads((ROOT/'scripts/product_expansion_catalog.json').read_text())};keys=[k for k in PRODUCTS if k.split('/')[-1] in expanded]
        return hero(key,text('collections_intro'),False)+f'<section class="section"><label class="locale-search">{e(text("search_label"))}<input type="search" data-native-search placeholder="{e(text("search"))}"></label><p role="status" data-native-count>{len(keys)} {e(text("search_count"))}</p>{cards(keys,True)}<p data-native-empty hidden>{e(text("search_empty"))}</p></section>'+cta(key)
    if role in ['resources','blog']:
        keys=[k for k in PAGES if k.startswith('resources/' if role=='resources' else 'blog/') and not k.endswith('/index')]
        items=''.join(f'<article><span>{e(group_text(PAGES[k][0],"title"))}</span><h2>{link(k)}</h2><p>{e(group_text(PAGES[k][0],"intro"))}</p>{link(k,text("read_guide"))}</article>' for k in keys)
        return hero(key,text('guide_intro'),False)+f'<section class="section"><div class="locale-guide-grid">{items}</div></section>'+cta(key)
    if role=='faq':return hero(key,text('cta_body'),False)+faqs()+specs('commercial')+cta(key)
    if role in ['receipt','missing']:
        return hero(key,text('receipt_empty' if role=='receipt' else 'missing_body'),False)
    is_product=key in PRODUCTS
    result=hero(key,group_text(role,'intro'),is_product or key in ['fabrics','about-factory','case-studies'])+specs(role)
    if role not in ['editorial','privacy']:result+=steps()
    if is_product:
        related=[k for k in PRODUCTS if k!=key and PAGES[k][0]==role][:4]
        if related:result+=f'<section class="section"><div class="section-heading"><h2>{e(text("related"))}</h2></div>{cards(related)}</section>'
        result+=faqs()
    if key.startswith(('resources/','blog/')) or role in ['editorial','privacy']:
        downloads=''.join(f'<a class="button secondary" href="{e(path)}" download>{e(text("download_english"))}</a>' for path in dict.fromkeys(SOURCES[key].downloads))
        result+=f'<aside class="section locale-source"><a href="{path_for(key)}" lang="en">{e(text("source_english"))}</a>{downloads}</aside>'
    return result+cta(key)

def description_for(key):
    role = PAGES[key][0]
    if role == 'home': return text('home_intro')
    if role == 'contact': return text('contact_intro')
    if role == 'receipt': return f'{title(key)}. {text("receipt_empty")}'
    if role == 'missing': return f'{title(key)}. {text("missing_body")}'
    if role == 'catalog': return f'{title(key)}. {text("collections_intro")}'
    if role in ['resources', 'blog', 'faq']: return f'{title(key)}. {text("guide_intro")}'
    if role + '.intro' in GROUPS: return f'{title(key)}. {group_text(role,"intro")}'
    return f'{title(key)}. {text("guide_intro")}'

def render(key):
    role=PAGES[key][0]
    description=description_for(key)
    canonical=ORIGIN+local_path(key,LOCALE)
    noindex=SOURCES[key].noindex
    image_src=SOURCES[key].images[0]['src'] if SOURCES[key].images else '/assets/images/hero-brand-campaign.jpg'
    metadata={'@context':'https://schema.org','@type':'WebPage','name':title(key),'description':description,'url':canonical,'inLanguage':LANG,'isPartOf':{'@type':'WebSite','name':'GloryStarWear','url':ORIGIN+'/'+LOCALE+'/'}}
    runtime={k:text(k) for k in ['search_count','sending','sent','submit_error','verify','copied','copy_error','file_error','submit','name','email','phone','buyer','product','quantity','market','timeline','message','reference','files']}
    runtime['locale']=LOCALE;runtime['lang']=LANG
    metadata_json = json.dumps(metadata, ensure_ascii=False).replace('<', '\\u003c')
    runtime_json = json.dumps(runtime, ensure_ascii=False).replace('<', '\\u003c')
    return f'''<!doctype html>
<html lang="{LANG}"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{e(title(key))} | GloryStarWear</title><meta name="description" content="{e(description)}"><meta name="robots" content="{'noindex, follow' if noindex else 'index, follow, max-image-preview:large'}"><link rel="canonical" href="{canonical}">
{alternate_links(key)}
<meta property="og:title" content="{e(title(key))} | GloryStarWear"><meta property="og:description" content="{e(description)}"><meta property="og:type" content="website"><meta property="og:url" content="{canonical}"><meta property="og:locale" content="{LANG.replace('-','_')}"><meta property="og:image" content="{ORIGIN}{image_src}"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{e(title(key))} | GloryStarWear"><meta name="twitter:description" content="{e(description)}"><meta name="twitter:image" content="{ORIGIN}{image_src}"><link rel="icon" href="/assets/logo-mark.svg"><link rel="stylesheet" href="/styles.css?v=20260903-1"><link rel="stylesheet" href="/assets/locales.css?v={VERSION}"><script src="/assets/vendor/lucide.min.js?v=20260722-1" defer></script><script src="/assets/locales.js?v={VERSION}" defer></script><script src="/assets/language.js?v={VERSION}" defer></script><script type="application/ld+json">{metadata_json}</script><script type="application/json" id="locale-ui">{runtime_json}</script></head><body class="product-page locale-page" data-page-key="{key}">{header(key)}<main id="main-content">{body(key)}</main>{footer()}</body></html>'''

def main():
    global INDEX,LOCALE,LANG,NAME,FLAG,CODE
    for INDEX,(LOCALE,LANG,NAME,FLAG,CODE) in enumerate(LOCALES):
        for key in PAGES:
            dest=ROOT/LOCALE/(key+'.html');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(render(key))
    # English and native editions advertise the same reciprocal set.
    for key in PAGES:
        p=ROOT/(key+'.html');source=p.read_text()
        source=re.sub(r'\s*<!-- LOCALE_ALTERNATES_START -->[\s\S]*?<!-- LOCALE_ALTERNATES_END -->','',source)
        block='\n    <!-- LOCALE_ALTERNATES_START -->\n'+alternate_links(key)+'\n    <!-- LOCALE_ALTERNATES_END -->'
        source=re.sub(r'\s*</head>',block+'\n  </head>',source,count=1);p.write_text(source)
    ET.register_namespace('','http://www.sitemaps.org/schemas/sitemap/0.9')
    ns='{http://www.sitemaps.org/schemas/sitemap/0.9}'
    root=ET.Element(ns+'urlset')
    for slug,*_ in LOCALES:
        for key in PAGES:
            if SOURCES[key].noindex:continue
            node=ET.SubElement(root,ns+'url');ET.SubElement(node,ns+'loc').text=ORIGIN+local_path(key,slug)
    ET.indent(root);ET.ElementTree(root).write(ROOT/'sitemap-languages.xml',encoding='utf-8',xml_declaration=True)
    robots=ROOT/'robots.txt';source=robots.read_text();line=f'Sitemap: {ORIGIN}/sitemap-languages.xml'
    if line not in source:robots.write_text(source.rstrip()+'\n'+line+'\n')
    print(f'Rendered {len(PAGES)*len(LOCALES)} native pages across {len(LOCALES)} languages.')

if __name__=='__main__':main()
