#!/usr/bin/env python3

"""Shared, site-wide header and footer markup.

All links are root-relative so the same chrome can be used on root pages and
inside product, resource, and editorial directories without per-page forks.
"""


def site_header_markup() -> str:
    return """    <header class="site-header" data-header data-site-chrome>
      <a class="brand" href="/" aria-label="GloryStarWear home"><span class="brand-mark" aria-hidden="true">GS</span><span class="brand-name">GloryStarWear<small>Custom sportswear programs</small></span></a>
      <nav class="desktop-nav" aria-label="Primary navigation">
        <div class="nav-dropdown"><a class="nav-trigger" href="/products/" aria-haspopup="true">Products <i data-lucide="chevron-down"></i></a><div class="nav-menu"><a href="/products/">All Products</a><a href="/products/new-products.html">New Products</a><a href="/products/lookbook.html">Product Gallery</a><a href="/products/private-label-gym-clothing.html">Private Label Activewear</a><a href="/custom-teamwear-uniforms.html">Custom Teamwear</a><a href="/products/running-wear.html">Running &amp; Endurance</a><a href="/products/cycling-wear.html">Cycling Wear</a><a href="/products/racket-sports-apparel.html">Racket Sports</a><a href="/products/accessories.html">Accessories &amp; Packaging</a><a href="/products/more-sports.html">More Sports</a></div></div>
        <a href="/sportswear-manufacturer.html">Manufacturing</a><a href="/customization.html">Customization</a><a href="/fabrics.html">Fabrics</a><a href="/process.html">Process</a><a href="/resources/">Resources</a>
      </nav>
      <a class="header-cta" href="/contact.html#quote-form"><i data-lucide="send"></i><span>Build Your Brief</span></a>
      <button class="menu-toggle" type="button" aria-label="Open menu" aria-expanded="false" data-menu-toggle><i data-lucide="menu"></i></button>
    </header>
    <nav class="mobile-nav" aria-label="Mobile navigation" data-mobile-nav data-site-chrome aria-hidden="true"><div class="mobile-nav-actions"><a class="button primary" href="/contact.html#quote-form"><i data-lucide="send"></i>Build Your Brief</a><a class="button whatsapp" href="https://wa.me/8618020755949" target="_blank" rel="noreferrer"><i data-lucide="message-circle"></i>WhatsApp</a></div><a href="/products/">Products</a><a href="/sportswear-manufacturer.html">Manufacturing</a><a href="/customization.html">Customization</a><a href="/fabrics.html">Fabrics &amp; Colors</a><a href="/process.html">Process</a><a href="/quality.html">Quality</a><a href="/resources/">Buyer Resources</a><a href="/faq.html">FAQ</a><a href="/contact.html#quote-form">Contact</a></nav>"""


def site_footer_markup() -> str:
    return """    <footer class="site-footer" data-site-chrome>
      <div class="site-footer-shell">
        <div class="footer-brand"><a class="brand" href="/" aria-label="GloryStarWear home"><span class="brand-mark" aria-hidden="true">GS</span><span class="brand-name">GloryStarWear<small>Custom sportswear programs</small></span></a><p>Plan activewear, teamwear, specialist sports apparel, labels, packaging, samples, and repeat orders through one controlled buyer brief.</p><a class="footer-brief-link" href="/contact.html#quote-form">Start a project brief <span aria-hidden="true">→</span></a></div>
        <nav class="footer-links" aria-label="Footer navigation">
          <div class="footer-link-group"><strong>Products</strong><a href="/products/">All Products</a><a href="/products/new-products.html">New Products</a><a href="/products/lookbook.html">Product Gallery</a><a href="/products/private-label-gym-clothing.html">Activewear</a><a href="/custom-teamwear-uniforms.html">Teamwear</a><a href="/products/more-sports.html">More Sports</a></div>
          <div class="footer-link-group"><strong>Plan &amp; Verify</strong><a href="/sportswear-manufacturer.html">Manufacturing Routes</a><a href="/low-moq-sportswear-manufacturer.html">MOQ Planning</a><a href="/process.html">Development Process</a><a href="/quality.html">Quality Controls</a><a href="/about-factory.html">Factory Evidence</a><a href="/certificates.html">Compliance Evidence</a></div>
          <div class="footer-link-group"><strong>Resources</strong><a href="/resources/">Buyer Guides</a><a href="/quote-checklist.html">Quote Checklist</a><a href="/faq.html">FAQ</a><a href="/case-studies.html">Planning Examples</a><a href="/contact.html#quote-form">Contact</a><a href="https://wa.me/8618020755949" target="_blank" rel="noreferrer">WhatsApp</a></div>
          <div class="footer-link-group footer-legal"><strong>Site</strong><a href="/editorial-policy.html">Editorial Policy</a><a href="/privacy.html">Privacy</a><button class="footer-choice-link" type="button" data-manage-analytics-consent>Analytics Choices</button><span>© 2026 GloryStarWear</span></div>
        </nav>
      </div>
    </footer>"""
