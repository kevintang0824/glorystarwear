/* Interactions for authored language editions. All visible strings come from locale data. */
(() => {
  'use strict';
  const uiElement = document.getElementById('locale-ui');
  if (!uiElement) return;
  const ui = JSON.parse(uiElement.textContent);
  const header = document.querySelector('[data-header]');
  const toggle = document.querySelector('[data-menu-toggle]');
  const mobile = document.querySelector('[data-mobile-nav]');

  const syncHeader = () => header?.classList.toggle('is-scrolled', scrollY > 24);
  addEventListener('scroll', syncHeader, { passive: true });
  syncHeader();

  const setMenu = (open) => {
    if (!toggle || !mobile) return;
    toggle.setAttribute('aria-expanded', String(open));
    mobile.setAttribute('aria-hidden', String(!open));
    mobile.classList.toggle('is-open', open);
    if (open) mobile.removeAttribute('inert'); else mobile.setAttribute('inert', '');
    toggle.innerHTML = `<i data-lucide="${open ? 'x' : 'menu'}"></i>`;
    window.lucide?.createIcons();
  };
  toggle?.addEventListener('click', () => setMenu(toggle.getAttribute('aria-expanded') !== 'true'));
  mobile?.addEventListener('click', (event) => { if (event.target.closest('a')) setMenu(false); });
  addEventListener('resize', () => { if (innerWidth > 1280) setMenu(false); });
  document.addEventListener('keydown', (event) => { if (event.key === 'Escape') setMenu(false); });

  const normalize = (url) => new URL(url, location.href).pathname.replace(/index\.html$/, '');
  document.querySelectorAll('.desktop-nav a, .mobile-nav a, .footer-links a').forEach((link) => {
    if (normalize(link.href) === normalize(location.href)) link.setAttribute('aria-current', 'page');
  });

  const search = document.querySelector('[data-native-search]');
  const products = [...document.querySelectorAll('[data-local-product]')];
  const count = document.querySelector('[data-native-count]');
  const empty = document.querySelector('[data-native-empty]');
  const filter = () => {
    const query = search?.value.trim().toLocaleLowerCase(ui.lang) || '';
    let visible = 0;
    products.forEach((card) => {
      const matches = !query || card.textContent.toLocaleLowerCase(ui.lang).includes(query);
      card.hidden = !matches;
      if (matches) visible += 1;
    });
    if (count) count.textContent = `${visible} ${ui.search_count}`;
    if (empty) empty.hidden = visible !== 0;
  };
  search?.addEventListener('input', filter);

  const form = document.querySelector('[data-native-quote]');
  if (form) setupForm(form);

  const receiptKey = `glorystarwear-lead-receipt-${ui.locale}`;
  if (document.body.dataset.pageKey === 'thank-you') {
    try {
      const receipt = JSON.parse(sessionStorage.getItem(receiptKey) || 'null');
      sessionStorage.removeItem(receiptKey);
      if (receipt?.confirmedAt && Date.now() - receipt.confirmedAt < 15 * 60 * 1000) {
        document.querySelector('.locale-hero h1').textContent = ui.sent;
        document.querySelector('.locale-hero-copy > p:not(.eyebrow)').textContent = ui.sent;
      }
    } catch { /* The default page never claims a submission. */ }
  }

  window.lucide?.createIcons();

  function setupForm(form) {
    const status = form.querySelector('[data-native-status]');
    const submit = form.querySelector('[data-native-submit]');
    const turnstileSlot = form.querySelector('[data-native-turnstile]');
    const fileInput = form.elements.referenceFiles;
    const shareButton = form.querySelector('[data-native-action="share"]');
    let turnstileToken = '';
    let turnstileWidget = null;

    const setStatus = (message) => { status.textContent = message; };
    const selectedFiles = () => [...(fileInput?.files || [])];
    const filesValid = () => selectedFiles().length <= 5 && selectedFiles().reduce((sum, file) => sum + file.size, 0) <= 20 * 1024 * 1024;
    fileInput?.addEventListener('change', () => {
      if (!filesValid()) setStatus(ui.file_error);
      shareButton.hidden = !navigator.share || selectedFiles().length === 0;
    });

    const queryProduct = new URL(location.href).searchParams.get('product');
    if (queryProduct && [...form.elements.product.options].some((option) => option.value === queryProduct)) form.elements.product.value = queryProduct;

    const value = (name) => String(form.elements[name]?.value || '').trim();
    const lines = () => [
      `GloryStarWear · ${document.querySelector('h1')?.textContent || ''}`,
      `${ui.name}: ${value('name')}`,
      `${ui.email}: ${value('email')}`,
      `${ui.phone}: ${value('phone')}`,
      `${ui.buyer}: ${value('buyerType')}`,
      `${ui.product}: ${form.elements.product?.selectedOptions[0]?.textContent || value('product')}`,
      `${ui.quantity}: ${value('quantity')}`,
      `${ui.market}: ${value('market')}`,
      `${ui.timeline}: ${value('timeline')}`,
      `${ui.message}: ${value('message')}`,
      `${ui.reference}: ${value('referenceLink')}`,
      `${ui.files}: ${selectedFiles().map((file) => file.name).join(', ')}`,
      `Page: ${location.href}`,
    ].filter((line) => !line.endsWith(': ')).join('\n');

    const validate = () => {
      if (!filesValid()) { setStatus(ui.file_error); return false; }
      if (!form.reportValidity()) return false;
      return true;
    };

    form.querySelector('[data-native-action="whatsapp"]')?.addEventListener('click', () => {
      if (!validate()) return;
      open(`https://wa.me/8618020755949?text=${encodeURIComponent(lines())}`, '_blank', 'noopener,noreferrer');
    });
    form.querySelector('[data-native-action="email"]')?.addEventListener('click', () => {
      if (!validate()) return;
      location.href = `mailto:kevin@glorystarwears.com?subject=${encodeURIComponent(document.querySelector('h1')?.textContent || 'GloryStarWear')}&body=${encodeURIComponent(lines())}`;
    });
    form.querySelector('[data-native-action="copy"]')?.addEventListener('click', async () => {
      if (!validate()) return;
      try { await navigator.clipboard.writeText(lines()); setStatus(ui.copied); }
      catch {
        try {
          const area = document.createElement('textarea'); area.value = lines(); document.body.append(area); area.select();
          if (!document.execCommand('copy')) throw new Error(); area.remove(); setStatus(ui.copied);
        } catch { setStatus(ui.copy_error); }
      }
    });
    shareButton?.addEventListener('click', async () => {
      if (!validate() || !navigator.share) return;
      const files = selectedFiles();
      try { await navigator.share({ title: document.querySelector('h1')?.textContent || 'GloryStarWear', text: lines(), files: navigator.canShare?.({ files }) ? files : undefined }); }
      catch (error) { if (error.name !== 'AbortError') setStatus(ui.submit_error); }
    });

    const loadTurnstile = (sitekey) => new Promise((resolve, reject) => {
      window.gloryStarLocaleTurnstileReady = () => {
        try {
          turnstileSlot.hidden = false;
          turnstileWidget = turnstile.render(turnstileSlot, {
            sitekey,
            language: ui.lang,
            callback: (token) => { turnstileToken = token; },
            'expired-callback': () => { turnstileToken = ''; },
            'error-callback': () => { turnstileToken = ''; setStatus(ui.verify); },
          });
          resolve();
        } catch (error) { reject(error); }
      };
      const script = document.createElement('script');
      script.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js?onload=gloryStarLocaleTurnstileReady&render=explicit';
      script.async = true; script.defer = true; script.onerror = reject; document.head.append(script);
    });

    fetch('/api/lead', { headers: { Accept: 'application/json' } })
      .then((response) => response.ok ? response.json() : null)
      .then(async (config) => {
        if (!config?.configured || !config.turnstileSiteKey) return;
        await loadTurnstile(config.turnstileSiteKey);
        submit.hidden = false;
      }).catch(() => { /* WhatsApp and email remain available. */ });

    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      if (!validate()) return;
      if (!turnstileToken) { setStatus(ui.verify); return; }
      submit.disabled = true; setStatus(ui.sending);
      const submissionId = crypto.randomUUID?.() || `${Date.now()}-${Math.random().toString(16).slice(2)}`;
      const payload = {
        payloadVersion: 2, submissionId, turnstileToken,
        name: value('name'), email: value('email'), phone: value('phone'), buyerType: value('buyerType'),
        developmentRoute: 'Native language website inquiry', briefReadiness: { version: 1, completed: 0, total: 7, level: 'unavailable' },
        product: value('product'), quantity: value('quantity'), market: value('market'), timeline: value('timeline'),
        projectDetails: value('message'), message: value('message'), companyWebsite: value('companyWebsite'), consent: form.elements.consent.checked,
        sourcePage: `${document.title} (${location.pathname})`, landingPage: location.pathname, referrer: document.referrer,
        trafficChannel: 'Direct / localized site', trafficSource: ui.locale, campaign: {},
      };
      try {
        const response = await fetch('/api/lead', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
        if (!response.ok) throw new Error();
        try { sessionStorage.setItem(receiptKey, JSON.stringify({ confirmedAt: Date.now() })); } catch { /* Redirect remains valid. */ }
        location.href = `/${ui.locale}/thank-you.html`;
      } catch {
        setStatus(ui.submit_error); submit.disabled = false; turnstileToken = '';
        if (turnstileWidget !== null) window.turnstile?.reset(turnstileWidget);
      }
    });
  }
})();
