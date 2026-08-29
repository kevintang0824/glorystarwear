const header = document.querySelector("[data-header]");
const menuToggle = document.querySelector("[data-menu-toggle]");
const mobileNav = document.querySelector("[data-mobile-nav]");
const quoteForms = document.querySelectorAll("[data-quote-form]");
const catalogGrid = document.querySelector("[data-catalog-grid]");
const whatsappNumber = "8618020755949";
const isContactPage = window.location.pathname.endsWith("/contact.html");
const isThankYouPage = window.location.pathname.endsWith("/thank-you.html");
const inquirySourceKey = "glorystarwear-inquiry-source";
const buyerPathStorageKey = "glorystarwear-buyer-path";
const productDirectionStorageKey = "glorystarwear-product-direction";
const productShortlistStorageKey = "glorystarwear-product-shortlist";
const fabricShortlistStorageKey = "glorystarwear-fabric-shortlist";
const attributionStorageKey = "glorystarwear-attribution";
const leadReceiptStorageKey = "glorystarwear-lead-receipt";
const quoteSubmissionIds = new WeakMap();
const turnstileStates = new WeakMap();
let turnstileScriptPromise = null;
const leadReceiptLifetimeMilliseconds = 15 * 60 * 1000;
const googleAnalyticsMeasurementId = "G-3QHK9TGCHQ";
const analyticsConsentStorageKey = "glorystarwear-analytics-consent-v1";
const analyticsConsentOptions = new Set(["granted", "denied"]);
const campaignParameterNames = [
  "utm_source",
  "utm_medium",
  "utm_campaign",
  "utm_term",
  "utm_content",
  "gclid",
  "msclkid",
];

window.dataLayer = window.dataLayer || [];
window.siteDataLayer = window.siteDataLayer || [];
window.gtag = window.gtag || function gtag() {
  window.dataLayer.push(arguments);
};

const readAnalyticsConsent = () => {
  try {
    const preference = localStorage.getItem(analyticsConsentStorageKey) || "";
    return analyticsConsentOptions.has(preference) ? preference : "";
  } catch {
    return "";
  }
};

let analyticsConsentPreference = readAnalyticsConsent();
let googleAnalyticsLoaded = false;

window.gtag("consent", "default", {
  ad_storage: "denied",
  ad_user_data: "denied",
  ad_personalization: "denied",
  analytics_storage: "denied",
  wait_for_update: 500,
});

if (analyticsConsentPreference) {
  window.gtag("consent", "update", {
    ad_storage: "denied",
    ad_user_data: "denied",
    ad_personalization: "denied",
    analytics_storage: analyticsConsentPreference,
  });
}

const loadGoogleAnalytics = () => {
  if (googleAnalyticsLoaded || analyticsConsentPreference !== "granted") return;
  googleAnalyticsLoaded = true;

  const googleTag = document.createElement("script");
  googleTag.async = true;
  googleTag.src = `https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(googleAnalyticsMeasurementId)}`;
  googleTag.dataset.googleAnalytics = googleAnalyticsMeasurementId;
  document.head.append(googleTag);

  window.gtag("js", new Date());
  window.gtag("config", googleAnalyticsMeasurementId, {
    allow_google_signals: false,
    allow_ad_personalization_signals: false,
    cookie_flags: "SameSite=Lax;Secure",
    send_page_view: true,
  });
};

if (analyticsConsentPreference === "granted") {
  loadGoogleAnalytics();
}

const saveAnalyticsConsent = (preference) => {
  analyticsConsentPreference = analyticsConsentOptions.has(preference) ? preference : "denied";
  try {
    localStorage.setItem(analyticsConsentStorageKey, analyticsConsentPreference);
  } catch {
    // The choice remains active for this page when browser storage is unavailable.
  }

  window.gtag("consent", "update", {
    ad_storage: "denied",
    ad_user_data: "denied",
    ad_personalization: "denied",
    analytics_storage: analyticsConsentPreference,
  });

  if (analyticsConsentPreference === "granted") {
    loadGoogleAnalytics();
    window.gtag("event", "analytics_consent_update", {
      consent_state: "granted",
      page_path: window.location.pathname,
    });
  }
};

const setupAnalyticsConsentControls = () => {
  const banner = document.createElement("div");
  banner.className = "analytics-consent-banner";
  banner.setAttribute("data-analytics-consent-banner", "");
  banner.setAttribute("role", "dialog");
  banner.setAttribute("aria-modal", "false");
  banner.setAttribute("aria-labelledby", "analytics-consent-title");
  banner.hidden = true;
  banner.innerHTML = `
    <div>
      <p class="eyebrow">Optional analytics</p>
      <h2 id="analytics-consent-title">Help us understand which pages are useful</h2>
      <p>With your permission, Google Analytics measures page visits and actions such as quote starts, confirmed inquiries, contact clicks, and checklist downloads. We do not send contact names, email addresses, phone numbers, or message text to Analytics.</p>
      <a href="${new URL("/privacy.html", window.location.href).href}">Read the privacy details</a>
    </div>
    <div class="analytics-consent-actions">
      <button class="button primary" type="button" data-analytics-accept>Allow analytics</button>
      <button class="button secondary" type="button" data-analytics-decline>Decline</button>
    </div>
  `;
  document.body.append(banner);

  const openConsentControls = () => {
    banner.hidden = false;
    window.requestAnimationFrame(() => banner.querySelector("[data-analytics-accept]")?.focus());
  };

  const closeConsentControls = () => {
    banner.hidden = true;
  };

  banner.querySelector("[data-analytics-accept]")?.addEventListener("click", () => {
    saveAnalyticsConsent("granted");
    closeConsentControls();
  });
  banner.querySelector("[data-analytics-decline]")?.addEventListener("click", () => {
    saveAnalyticsConsent("denied");
    closeConsentControls();
  });

  document.querySelectorAll("[data-manage-analytics-consent]").forEach((control) => {
    control.addEventListener("click", openConsentControls);
  });

  if (!analyticsConsentPreference) {
    openConsentControls();
  }
};

const attributionHostGroups = {
  ai_assistant: [
    ["chatgpt", ["chatgpt.com", "chat.openai.com"]],
    ["perplexity", ["perplexity.ai"]],
    ["gemini", ["gemini.google.com"]],
    ["copilot", ["copilot.microsoft.com"]],
    ["claude", ["claude.ai"]],
    ["you.com", ["you.com"]],
  ],
  organic_search: [
    ["google", ["google.com", "google.co.uk", "google.ca", "google.com.au", "google.de", "google.fr"]],
    ["bing", ["bing.com"]],
    ["yahoo", ["search.yahoo.com"]],
    ["duckduckgo", ["duckduckgo.com"]],
    ["yandex", ["yandex.com", "yandex.ru"]],
    ["baidu", ["baidu.com"]],
  ],
  organic_social: [
    ["linkedin", ["linkedin.com", "lnkd.in"]],
    ["youtube", ["youtube.com", "youtu.be"]],
    ["facebook", ["facebook.com", "m.facebook.com"]],
    ["instagram", ["instagram.com"]],
    ["pinterest", ["pinterest.com"]],
    ["reddit", ["reddit.com"]],
    ["x", ["x.com", "twitter.com", "t.co"]],
    ["tiktok", ["tiktok.com"]],
  ],
};

const getHostname = (value) => {
  if (!value) return "";

  try {
    return new URL(value).hostname.toLowerCase().replace(/^www\./, "");
  } catch {
    return "";
  }
};

const hostnameMatches = (hostname, domain) =>
  hostname === domain || hostname.endsWith(`.${domain}`);

const findAttributionHost = (hostname, group) => {
  if (!hostname) return "";
  if (group === "organic_search" && /(^|\.)google\.[a-z.]+$/.test(hostname)) {
    return "google";
  }

  const match = attributionHostGroups[group].find(([, domains]) =>
    domains.some((domain) => hostnameMatches(hostname, domain)));
  return match?.[0] || "";
};

const classifyAttribution = (attribution) => {
  const campaign = attribution?.campaign || {};
  const source = String(campaign.utm_source || "").trim().toLowerCase();
  const medium = String(campaign.utm_medium || "").trim().toLowerCase();
  const referrerHost = getHostname(attribution?.referrer);
  const campaignHost = getHostname(
    source.includes(".") ? `https://${source.replace(/^https?:\/\//, "")}` : "",
  );
  const sourceHost = campaignHost || referrerHost;
  const aiSource = findAttributionHost(sourceHost, "ai_assistant") ||
    (/chatgpt|openai|perplexity|gemini|copilot|claude/.test(source) ? source : "");

  if (
    campaign.gclid ||
    campaign.msclkid ||
    /^(cpc|ppc|paid|paid_search|display|cpm)$/.test(medium)
  ) {
    return {
      channel: "paid_search",
      source: source || (campaign.gclid ? "google_ads" : "microsoft_ads"),
      referrerHost,
    };
  }

  if (/^(email|newsletter)$/.test(medium)) {
    return { channel: "email", source: source || "email", referrerHost };
  }

  if (/^(affiliate|partner)$/.test(medium)) {
    return { channel: "partner", source: source || referrerHost, referrerHost };
  }

  if (/^(social|organic_social)$/.test(medium)) {
    return {
      channel: "organic_social",
      source: source || findAttributionHost(referrerHost, "organic_social") || referrerHost,
      referrerHost,
    };
  }

  if (/^(organic|organic_search)$/.test(medium)) {
    return {
      channel: "organic_search",
      source: source || findAttributionHost(referrerHost, "organic_search") || referrerHost,
      referrerHost,
    };
  }

  if (aiSource) {
    return { channel: "ai_assistant", source: aiSource, referrerHost };
  }

  const socialSource = findAttributionHost(sourceHost, "organic_social");
  if (socialSource) {
    return {
      channel: "organic_social",
      source: socialSource,
      referrerHost,
    };
  }

  const searchSource = findAttributionHost(sourceHost, "organic_search");
  if (searchSource) {
    return {
      channel: "organic_search",
      source: searchSource || source || referrerHost,
      referrerHost,
    };
  }

  if (source || medium) {
    return { channel: "campaign", source: source || medium, referrerHost };
  }

  if (referrerHost) {
    return { channel: "referral", source: referrerHost, referrerHost };
  }

  return { channel: "direct", source: "direct", referrerHost: "" };
};

const readAttribution = () => {
  try {
    return JSON.parse(sessionStorage.getItem(attributionStorageKey));
  } catch {
    return null;
  }
};

const captureAttribution = () => {
  const storedAttribution = readAttribution();
  const searchParameters = new URLSearchParams(window.location.search);
  const campaign = Object.fromEntries(
    campaignParameterNames
      .filter((name) => searchParameters.has(name))
      .map((name) => [name, searchParameters.get(name).slice(0, 160)]),
  );
  const attribution = {
    landingPage: storedAttribution?.landingPage || window.location.href,
    referrer: storedAttribution?.referrer || document.referrer || "",
    firstSeenAt: storedAttribution?.firstSeenAt || new Date().toISOString(),
    campaign: Object.keys(campaign).length ? campaign : storedAttribution?.campaign || {},
  };

  try {
    sessionStorage.setItem(attributionStorageKey, JSON.stringify(attribution));
  } catch {
    // Attribution remains available for this page when storage is unavailable.
  }

  return { attribution, isNewSession: !storedAttribution };
};

const { attribution: pageAttribution, isNewSession: isNewAttributionSession } = captureAttribution();
const pageTrafficAttribution = classifyAttribution(pageAttribution);

const getPageContext = () => {
  const path = window.location.pathname.toLowerCase();
  if (path === "/" || path.endsWith("/index.html") && !path.includes("/blog/") && !path.includes("/products/") && !path.includes("/resources/")) {
    return { pageType: "home", contentGroup: "home" };
  }
  if (path === "/blog/" || path.endsWith("/blog/index.html")) {
    return { pageType: "blog_hub", contentGroup: "editorial" };
  }
  if (path.includes("/blog/")) {
    return { pageType: "blog_article", contentGroup: "editorial" };
  }
  if (path === "/products/" || path.endsWith("/products/index.html")) {
    return { pageType: "product_hub", contentGroup: "product_catalog" };
  }
  if (path.includes("/products/")) {
    return { pageType: "product_page", contentGroup: "product_catalog" };
  }
  if (path === "/resources/" || path.endsWith("/resources/index.html")) {
    return { pageType: "resource_hub", contentGroup: "buyer_resources" };
  }
  if (path.includes("/resources/")) {
    return { pageType: "resource_guide", contentGroup: "buyer_resources" };
  }
  if (/\/(contact|quote-checklist|thank-you)\.html$/.test(path)) {
    return { pageType: "conversion_page", contentGroup: "conversion" };
  }
  if (/\/(about-factory|certificates|case-studies|factory-video|editorial-policy)\.html$/.test(path)) {
    return { pageType: "trust_page", contentGroup: "trust" };
  }
  if (/\/(process|quality|fabrics|customization|one-stop-service)\.html$/.test(path)) {
    return { pageType: "operations_page", contentGroup: "operations" };
  }
  if (/\/(sportswear-manufacturer|private-label-activewear-manufacturer|custom-teamwear-uniforms|low-moq-sportswear-manufacturer)\.html$/.test(path)) {
    return { pageType: "commercial_landing", contentGroup: "manufacturing_services" };
  }
  return { pageType: "site_page", contentGroup: "site_information" };
};

const pageContext = getPageContext();

const trackEvent = (eventName, details = {}) => {
  const eventDetails = {
    event: eventName,
    page_path: window.location.pathname,
    page_type: pageContext.pageType,
    content_group: pageContext.contentGroup,
    traffic_channel: pageTrafficAttribution.channel,
    traffic_source: pageTrafficAttribution.source,
    referrer_host: pageTrafficAttribution.referrerHost,
    ...details,
  };
  window.siteDataLayer.push(eventDetails);

  if (analyticsConsentPreference !== "granted") return;
  window.dataLayer.push({ ...eventDetails, event: `gsw_${eventName}` });
  const { event: _dataLayerEvent, ...googleEventDetails } = eventDetails;
  window.gtag("event", eventName, googleEventDetails);

  if (eventName === "lead_submit_success") {
    window.gtag("event", "generate_lead", {
      lead_source: "website_form",
      form_location: details.form_location || window.location.pathname,
      product_interest: details.product_interest || "",
      page_type: pageContext.pageType,
      content_group: pageContext.contentGroup,
      traffic_channel: pageTrafficAttribution.channel,
      traffic_source: pageTrafficAttribution.source,
    });
  }

  if (eventName === "catalog_search" && details.search_term) {
    window.gtag("event", "search", { search_term: details.search_term });
  }
};

const storeLeadReceipt = () => {
  try {
    sessionStorage.setItem(
      leadReceiptStorageKey,
      JSON.stringify({
        version: 1,
        confirmedAt: Date.now(),
        sourcePath: window.location.pathname,
      }),
    );
    return true;
  } catch {
    return false;
  }
};

const consumeLeadReceipt = () => {
  try {
    const storedReceipt = sessionStorage.getItem(leadReceiptStorageKey);
    sessionStorage.removeItem(leadReceiptStorageKey);
    if (!storedReceipt) return null;

    const receipt = JSON.parse(storedReceipt);
    const receiptAge = Date.now() - receipt.confirmedAt;
    const isValid = receipt.version === 1 &&
      Number.isFinite(receipt.confirmedAt) &&
      receiptAge >= 0 &&
      receiptAge <= leadReceiptLifetimeMilliseconds;
    return isValid ? receipt : null;
  } catch {
    return null;
  }
};

if (isNewAttributionSession) {
  trackEvent("session_landing", {
    campaign_source: pageAttribution.campaign.utm_source || "",
    campaign_medium: pageAttribution.campaign.utm_medium || "",
    campaign_name: pageAttribution.campaign.utm_campaign || "",
  });
}

if (isThankYouPage) {
  const leadReceipt = consumeLeadReceipt();
  if (leadReceipt) {
    document.title = "Inquiry Received | GloryStarWear";
    document.querySelector('meta[name="description"]')?.setAttribute(
      "content",
      "Confirmation and next-step guidance for a GloryStarWear custom sportswear inquiry received by the secure server form.",
    );

    const eyebrow = document.querySelector("[data-thank-you-eyebrow]");
    const heading = document.querySelector("[data-thank-you-heading]");
    const message = document.querySelector("[data-thank-you-message]");
    const breadcrumb = document.querySelector("[data-thank-you-breadcrumb]");
    const primaryAction = document.querySelector("[data-thank-you-primary]");
    const primaryActionLabel = primaryAction?.querySelector("span");
    const unconfirmedGuidance = document.querySelector("[data-thank-you-unconfirmed]");
    const confirmedGuidance = document.querySelector("[data-thank-you-confirmed]");

    if (eyebrow) eyebrow.textContent = "Server-confirmed submission";
    if (heading) heading.textContent = "Thank You — Your Inquiry Was Received";
    if (message) {
      message.textContent = "The receiving service confirmed your project brief. Keep this page for your records and add any urgent delivery date or reference-file note by WhatsApp.";
    }
    if (breadcrumb) breadcrumb.textContent = "Inquiry Received";
    if (primaryAction) {
      primaryAction.href = `https://wa.me/${whatsappNumber}`;
      primaryAction.target = "_blank";
      primaryAction.rel = "noreferrer";
      primaryAction.classList.remove("primary");
      primaryAction.classList.add("whatsapp");
    }
    if (primaryActionLabel) primaryActionLabel.textContent = "Add Details on WhatsApp";
    if (unconfirmedGuidance) unconfirmedGuidance.hidden = true;
    if (confirmedGuidance) confirmedGuidance.hidden = false;

    trackEvent("thank_you_view", {
      confirmation_source: "server_redirect",
      submission_source_path: leadReceipt.sourcePath || "",
    });
  }
}

const mainContent = document.querySelector("main");
if (mainContent && !document.querySelector(".skip-link")) {
  if (!mainContent.id) mainContent.id = "main-content";
  if (!mainContent.hasAttribute("tabindex")) mainContent.tabIndex = -1;
  const skipLink = document.createElement("a");
  skipLink.className = "skip-link";
  skipLink.href = `#${mainContent.id}`;
  skipLink.textContent = "Skip to main content";
  document.body.prepend(skipLink);
}

document.documentElement.classList.add("has-enhanced-contact");
if (catalogGrid) {
  document.documentElement.classList.add("has-enhanced-catalog");
}

let headerSyncScheduled = false;

const syncHeader = () => {
  header?.classList.toggle("is-scrolled", window.scrollY > 24);
  headerSyncScheduled = false;
};

const scheduleHeaderSync = () => {
  if (headerSyncScheduled) return;
  headerSyncScheduled = true;
  window.requestAnimationFrame(syncHeader);
};

window.addEventListener("scroll", scheduleHeaderSync, { passive: true });
scheduleHeaderSync();

menuToggle?.setAttribute("aria-expanded", "false");
if (mobileNav && !mobileNav.id) {
  mobileNav.id = "mobile-navigation";
}
if (mobileNav?.id) {
  menuToggle?.setAttribute("aria-controls", mobileNav.id);
}
mobileNav?.setAttribute("aria-hidden", "true");

const normalizeChromePath = (href) => {
  try {
    const target = new URL(href, window.location.href);
    if (target.origin !== window.location.origin) return "";
    const normalized = target.pathname.replace(/\/index\.html$/, "/");
    return normalized.length > 1 ? normalized.replace(/\/$/, "/") : normalized;
  } catch {
    return "";
  }
};

const currentChromePath = normalizeChromePath(window.location.href);
document.querySelectorAll("[data-site-chrome] a[href]").forEach((link) => {
  const linkPath = normalizeChromePath(link.href);
  if (linkPath && linkPath === currentChromePath) {
    link.setAttribute("aria-current", "page");
  }
});

const productsNavigationLink = document.querySelector('.nav-trigger[href="/products/"]');
productsNavigationLink?.classList.toggle(
  "is-section-current",
  currentChromePath.startsWith("/products/"),
);
const resourcesNavigationLink = document.querySelector('.desktop-nav > a[href="/resources/"]');
resourcesNavigationLink?.classList.toggle(
  "is-section-current",
  currentChromePath.startsWith("/resources/") || currentChromePath.startsWith("/blog/"),
);

const desktopNavDropdowns = [...document.querySelectorAll("[data-nav-dropdown]")];
const desktopNavigationQuery = window.matchMedia("(min-width: 1041px)");
const hoverNavigationQuery = window.matchMedia("(hover: hover) and (pointer: fine)");

const setDesktopNavDropdown = (dropdown, isOpen, isDismissed = false) => {
  dropdown.classList.toggle("is-open", isOpen);
  dropdown.classList.toggle("is-dismissed", !isOpen && isDismissed);
  dropdown.querySelector(".nav-trigger")?.setAttribute("aria-expanded", String(isOpen));
};

const closeDesktopNavDropdowns = (restoreFocus = false, isDismissed = false) => {
  desktopNavDropdowns.forEach((dropdown) => {
    const containedFocus = dropdown.contains(document.activeElement);
    if (restoreFocus && containedFocus) {
      dropdown.querySelector(".nav-trigger")?.focus();
    }
    setDesktopNavDropdown(dropdown, false, isDismissed);
  });
};

desktopNavDropdowns.forEach((dropdown) => {
  const trigger = dropdown.querySelector(".nav-trigger");
  dropdown.addEventListener("mouseenter", () => setDesktopNavDropdown(dropdown, true));
  dropdown.addEventListener("mouseleave", () => {
    if (!dropdown.contains(document.activeElement)) setDesktopNavDropdown(dropdown, false);
  });
  dropdown.addEventListener("focusin", () => setDesktopNavDropdown(dropdown, true));
  dropdown.addEventListener("focusout", () => {
    window.requestAnimationFrame(() => {
      if (!dropdown.contains(document.activeElement)) setDesktopNavDropdown(dropdown, false);
    });
  });
  trigger?.addEventListener("click", (event) => {
    const firstTouchOpen = desktopNavigationQuery.matches
      && !hoverNavigationQuery.matches
      && !dropdown.classList.contains("is-open");
    if (!firstTouchOpen) return;
    event.preventDefault();
    closeDesktopNavDropdowns();
    setDesktopNavDropdown(dropdown, true);
  });
});

document.addEventListener("click", (event) => {
  if (!event.target.closest("[data-nav-dropdown]")) closeDesktopNavDropdowns();
});

const contactUrl = isContactPage ? "#quote-form" : new URL("/contact.html#quote-form", window.location.href).href;
const currentPageTopic = document.title.split("|")[0].trim() || "custom sportswear";
const contextualWhatsAppText = [
  `Hi GloryStarWear, I am interested in ${currentPageTopic}.`,
  `Page: ${window.location.origin}${window.location.pathname}`,
  "Please share MOQ, sample cost, lead time, and quote details.",
].join("\n");
const defaultWhatsAppText = encodeURIComponent(contextualWhatsAppText);

const getCtaLocation = (element) => {
  if (element.closest("[data-quote-form]")) return "form";
  if (element.closest("[data-mobile-quote-bar], .floating-contact")) return "sticky";
  if (element.closest(".site-header, [data-mobile-nav]")) return "header";
  if (element.closest(".product-hero, .hero")) return "hero";
  if (element.closest(".site-footer")) return "footer";
  return "content";
};

if (mobileNav && !mobileNav.querySelector(".mobile-nav-actions")) {
  const actions = document.createElement("div");
  actions.className = "mobile-nav-actions";
  actions.innerHTML = `
    <a class="button primary" href="${contactUrl}"><i data-lucide="send"></i>Get Quote</a>
    <a class="button whatsapp" href="https://wa.me/${whatsappNumber}?text=${defaultWhatsAppText}" target="_blank" rel="noreferrer"><i data-lucide="message-circle"></i>WhatsApp</a>
  `;
  mobileNav.prepend(actions);
}

if (!document.querySelector("[data-mobile-quote-bar]")) {
  const bar = document.createElement("nav");
  bar.className = "mobile-quote-bar";
  bar.setAttribute("data-mobile-quote-bar", "");
  bar.setAttribute("aria-label", "Quick product actions");
  bar.innerHTML = `
    <a href="${contactUrl}"><i data-lucide="send"></i><span>Get Quote</span></a>
    <a href="https://wa.me/${whatsappNumber}?text=${defaultWhatsAppText}" target="_blank" rel="noreferrer"><i data-lucide="message-circle"></i><span>WhatsApp</span></a>
  `;
  document.body.append(bar);
}

const mobileQuoteBar = document.querySelector("[data-mobile-quote-bar]");
if (mobileQuoteBar && quoteForms.length && "IntersectionObserver" in window) {
  const visibleQuoteForms = new Set();
  const mobileQuoteBarObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) visibleQuoteForms.add(entry.target);
      else visibleQuoteForms.delete(entry.target);
    });
    const shouldSuppress = visibleQuoteForms.size > 0;
    mobileQuoteBar.classList.toggle("is-suppressed", shouldSuppress);
    mobileQuoteBar.setAttribute("aria-hidden", String(shouldSuppress));
    mobileQuoteBar.toggleAttribute("inert", shouldSuppress);
  }, { threshold: 0.05 });
  quoteForms.forEach((form) => mobileQuoteBarObserver.observe(form));
}

document.querySelectorAll(".footer-links").forEach((footerLinks) => {
  if (!footerLinks.querySelector('a[href$="/privacy.html"], a[href="./privacy.html"]')) {
    const privacyLink = document.createElement("a");
    privacyLink.href = new URL("/privacy.html", window.location.href).href;
    privacyLink.textContent = "Privacy";
    footerLinks.append(privacyLink);
  }

  if (!footerLinks.querySelector("[data-manage-analytics-consent]")) {
    const analyticsChoiceButton = document.createElement("button");
    analyticsChoiceButton.className = "footer-choice-link";
    analyticsChoiceButton.type = "button";
    analyticsChoiceButton.setAttribute("data-manage-analytics-consent", "");
    analyticsChoiceButton.textContent = "Analytics Choices";
    footerLinks.append(analyticsChoiceButton);
  }
});

setupAnalyticsConsentControls();

document.querySelectorAll(`a[href^="https://wa.me/${whatsappNumber}"]`).forEach((link) => {
  const target = new URL(link.href);
  if (!target.searchParams.has("text")) {
    target.searchParams.set("text", contextualWhatsAppText);
    link.href = target.toString();
  }
});

const setMobileMenu = (isOpen) => {
  mobileNav?.classList.toggle("is-open", isOpen);
  document.body.classList.toggle("menu-open", isOpen);
  menuToggle?.setAttribute("aria-expanded", String(isOpen));
  mobileNav?.setAttribute("aria-hidden", String(!isOpen));
};

menuToggle?.addEventListener("click", () => {
  setMobileMenu(!mobileNav?.classList.contains("is-open"));
});

mobileNav?.addEventListener("click", (event) => {
  if (event.target.closest("a")) {
    setMobileMenu(false);
  }
});

document.addEventListener("click", (event) => {
  const link = event.target.closest("a[href]");
  if (!link) return;
  if (event.defaultPrevented) return;

  try {
    const target = new URL(link.href, window.location.href);
    const navigationArea = link.closest(".desktop-nav")
      ? "desktop"
      : link.closest("[data-mobile-nav]")
        ? "mobile"
        : "";
    if (navigationArea) {
      trackEvent("navigation_select", {
        navigation_area: navigationArea,
        navigation_group: link.closest(".nav-menu-group, .mobile-nav-group")?.querySelector("strong")?.textContent.trim().slice(0, 50) || "primary",
        link_path: target.pathname,
        link_text: link.textContent.trim().slice(0, 80),
      });
    }
    const ctaLocation = getCtaLocation(link);
    const contactMethod = target.protocol === "tel:"
      ? "phone"
      : target.protocol === "mailto:"
        ? "email"
        : target.hostname === "wa.me"
          ? "whatsapp"
          : target.pathname.endsWith("/contact.html") || target.hash === "#quote-form"
            ? "quote_page"
            : "";

    if (contactMethod) {
      trackEvent("contact_click", {
        contact_method: contactMethod,
        cta_location: ctaLocation,
        link_text: link.textContent.trim().slice(0, 80),
      });

      if (contactMethod === "whatsapp" || contactMethod === "email" || contactMethod === "phone") {
        trackEvent(`${contactMethod}_click`, {
          link_context: "site_link",
          cta_location: ctaLocation,
          link_text: link.textContent.trim().slice(0, 80),
        });
      }
    }

    if (link.dataset.resourceDownload) {
      trackEvent("resource_download", {
        resource_name: link.dataset.resourceDownload.slice(0, 80),
        file_name: target.pathname.split("/").pop()?.slice(0, 120) || "",
      });
    }

    if (!isContactPage && target.pathname.endsWith("/contact.html")) {
      if (!link.closest(".sku-card-actions, .product-detail-actions, .product-detail-shortlist")) {
        sessionStorage.removeItem(productDirectionStorageKey);
      }
      sessionStorage.setItem(
        inquirySourceKey,
        JSON.stringify({
          title: document.title,
          path: window.location.pathname,
          savedAt: Date.now(),
        }),
      );
    }
  } catch {
    // Browsing still works when storage is unavailable.
  }
});

window.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    closeDesktopNavDropdowns(true, true);
    setMobileMenu(false);
  }
});

const readInquirySource = () => {
  try {
    const source = JSON.parse(sessionStorage.getItem(inquirySourceKey));
    const isRecent = source?.savedAt && Date.now() - source.savedAt < 2 * 60 * 60 * 1000;
    if (source?.title && source?.path && isRecent) {
      return source;
    }
    if (source) {
      sessionStorage.removeItem(inquirySourceKey);
    }
  } catch {
    // Continue without source context when storage is unavailable or invalid.
  }

  return null;
};

const getInquirySource = () => {
  const source = isContactPage ? readInquirySource() : null;
  if (source) return `${source.title} (${source.path})`;

  return `${document.title} (${window.location.pathname})`;
};

const getShortPageTitle = (title) => title.split("|")[0].trim();

const inquiryPrefillOptions = {
  buyer: {
    startup_brand: "Startup brand",
    established_brand: "Established brand",
    dealer_distributor: "Dealer or distributor",
    club_school_team: "Club, school, or team",
  },
  development: {
    light_custom: "Light customization from an existing direction",
    oem: "OEM from our tech pack",
    odm: "ODM from references and requirements",
    reorder: "Repeat or reorder of an approved style",
  },
  product: {
    private_label: "Private label activewear program",
    teamwear: "Custom teamwear program",
    low_moq: "Low MOQ launch planning",
    supplier_capability: "Supplier capability review",
    fabric: "Fabric selection and performance testing",
    fishing: "Custom fishing apparel",
    rowing: "Custom rowing uniforms",
    pilates: "Pilates activewear",
    flag_football: "Flag football uniforms",
    baseball: "Baseball uniforms",
    softball: "Softball uniforms",
    rugby: "Rugby uniforms",
    field_hockey: "Field hockey uniforms",
    running_shorts: "Custom running shorts",
    badminton: "Badminton uniforms",
    gym_leggings: "Private label gym leggings",
    boxing: "Custom boxing apparel",
    handball: "Custom handball uniforms",
    padel: "Custom padel apparel",
    futsal: "Custom futsal uniforms",
    table_tennis: "Custom table tennis uniforms",
    bowling: "Custom bowling shirts",
    darts: "Custom darts shirts",
    ultimate: "Custom ultimate jerseys",
    weightlifting: "Custom weightlifting singlets",
    team_polo: "Custom team polo shirts",
    cycling_skinsuit: "Custom cycling skinsuits",
    triathlon_suit: "Custom triathlon suits",
    beach_volleyball: "Custom beach volleyball uniforms",
    motocross: "Custom motocross jerseys",
    referee_uniform: "Custom referee uniforms",
    yoga_leggings: "Yoga leggings",
    seamless_activewear: "Seamless activewear",
    soccer_uniforms: "Soccer uniforms",
  },
};

const productSuggestionsByBuyerType = {
  "Startup brand": "Low MOQ launch planning",
  "Established brand": "Private label activewear program",
  "Dealer or distributor": "Supplier capability review",
  "Club, school, or team": "Custom teamwear program",
};

const readStoredBuyerPath = () => {
  try {
    const stored = JSON.parse(sessionStorage.getItem(buyerPathStorageKey));
    const isRecent = stored?.savedAt && Date.now() - stored.savedAt < 2 * 60 * 60 * 1000;
    if (stored?.buyerPath && isRecent) return stored.buyerPath;
    if (stored) sessionStorage.removeItem(buyerPathStorageKey);
  } catch {
    // Continue without a stored buyer path when storage is unavailable.
  }
  return "";
};

const readStoredProductDirection = () => {
  try {
    const stored = JSON.parse(sessionStorage.getItem(productDirectionStorageKey));
    const isRecent = stored?.savedAt && Date.now() - stored.savedAt < 2 * 60 * 60 * 1000;
    const hasValidSource = typeof stored?.sourcePath === "string" && stored.sourcePath.startsWith("/products/");
    if (stored?.label && hasValidSource && isRecent) {
      return {
        label: String(stored.label).replace(/[\r\n\t]/g, " ").slice(0, 100),
        sourcePath: stored.sourcePath,
      };
    }
    if (stored) sessionStorage.removeItem(productDirectionStorageKey);
  } catch {
    // Continue without a stored product direction when storage is unavailable.
  }
  return null;
};

const readStoredProductShortlist = () => {
  try {
    const stored = JSON.parse(sessionStorage.getItem(productShortlistStorageKey));
    const isRecent = stored?.savedAt && Date.now() - stored.savedAt < 2 * 60 * 60 * 1000;
    const items = [];
    if (Array.isArray(stored?.items)) {
      stored.items.slice(0, 4).forEach((item) => {
        const slug = String(item?.slug || "").toLowerCase();
        const label = String(item?.label || "").replace(/[\r\n\t]/g, " ").trim().slice(0, 100);
        const path = String(item?.path || "");
        const validSlug = /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug);
        if (!validSlug || !label || path !== `/products/${slug}.html`) return;
        if (!items.some((candidate) => candidate.slug === slug)) items.push({ slug, label, path });
      });
    }
    if (items.length && isRecent) return items;
    if (stored) sessionStorage.removeItem(productShortlistStorageKey);
  } catch {
    // Continue without a product shortlist when storage is unavailable or invalid.
  }
  return [];
};

const saveStoredProductShortlist = (items) => {
  try {
    if (!items.length) {
      sessionStorage.removeItem(productShortlistStorageKey);
      return;
    }
    sessionStorage.setItem(productShortlistStorageKey, JSON.stringify({
      items: items.slice(0, 4),
      savedAt: Date.now(),
    }));
  } catch {
    // The visible shortlist still works when session storage is unavailable.
  }
};

const readStoredFabricShortlist = () => {
  try {
    const stored = JSON.parse(sessionStorage.getItem(fabricShortlistStorageKey));
    const isRecent = stored?.savedAt && Date.now() - stored.savedAt < 2 * 60 * 60 * 1000;
    const items = Array.isArray(stored?.items)
      ? stored.items
        .slice(0, 4)
        .map((item) => ({
          id: String(item?.id || "").replace(/[^A-Za-z0-9-]/g, "").slice(0, 16),
          name: String(item?.name || "").replace(/[\r\n\t]/g, " ").trim().slice(0, 100),
        }))
        .filter((item) => item.id && item.name)
      : [];
    if (items.length && isRecent) return items;
    if (stored) sessionStorage.removeItem(fabricShortlistStorageKey);
  } catch {
    // Continue without a stored fabric shortlist when storage is unavailable or invalid.
  }
  return [];
};

const readInquiryPrefill = () => {
  if (!isContactPage) return { values: {}, hasValues: false, source: "" };
  const parameters = new URLSearchParams(window.location.search);
  const storedBuyerPath = readStoredBuyerPath();
  const queryBuyerPath = parameters.get("buyer") || "";
  const values = Object.fromEntries(
    Object.entries(inquiryPrefillOptions)
      .map(([name, options]) => {
        const requestedValue = name === "buyer"
          ? queryBuyerPath || storedBuyerPath
          : parameters.get(name);
        return [name, options[requestedValue] || ""];
      })
      .filter(([, value]) => value),
  );
  const source = queryBuyerPath ? "buyer_quote_link" : storedBuyerPath ? "buyer_path" : "";
  return { values, hasValues: Object.keys(values).length > 0, source };
};

const inquiryPrefill = readInquiryPrefill();

const applyInquiryPrefill = (form) => {
  const fieldNames = { buyer: "buyerType", development: "developmentRoute", product: "product" };
  Object.entries(inquiryPrefill.values).forEach(([parameterName, value]) => {
    const field = form.elements.namedItem(fieldNames[parameterName]);
    if (!field || field.value || ![...field.options].some((option) => option.value === value)) return;
    field.value = value;
    field.dataset.queryPrefilled = value;
  });
};

quoteForms.forEach(applyInquiryPrefill);

if (inquiryPrefill.hasValues) {
  trackEvent("buyer_quote_prefill", {
    prefill_source: inquiryPrefill.source,
    buyer_type: inquiryPrefill.values.buyer || "",
    development_route: inquiryPrefill.values.development || "",
    product_interest: inquiryPrefill.values.product || "",
  });
}

const getProductInterestForPath = (path) => {
  const routes = [
    ["Tech pack review and development", /\/(?:resources\/custom-sportswear-tech-pack|blog\/verify-ai-generated-tech-pack)\.html$/],
    ["Artwork and decoration review", /\/(?:resources\/sportswear-logo-artwork-preparation-guide|blog\/(?:apparel-print-wash-test-logo-durability|sportswear-sublimation-color-matching-guide)|customization)\.html$/],
    ["Fabric selection and performance testing", /\/(?:fabrics|blog\/(?:activewear-odor-resistance-antibacterial-test|moisture-wicking-quick-dry-activewear-test))\.html$/],
    ["Packaging and label handoff", /\/(?:resources\/sportswear-packaging-label-handoff-checklist|blog\/(?:custom-apparel-packaging-moq-inventory-planning|us-clothing-label-requirements-private-label)|products\/private-label-sportswear-packaging)\.html$/],
    ["Quality and inspection planning", /\/(?:quality|resources\/sportswear-aql-inspection-checklist|blog\/(?:clothing-sample-to-bulk-quality-control|activewear-leggings-quality-testing|running-shorts-chafing-ride-up-test|sports-bra-fit-support-wear-test|activewear-inclusive-sizing-fit-test))\.html$/],
    ["Sampling and approval support", /\/(?:process|resources\/sportswear-sample-approval-checklist|blog\/clothing-sample-rounds-before-bulk-production)\.html$/],
    ["Cost and lead-time review", /\/(?:quote-checklist|resources\/custom-sportswear-cost-lead-time|blog\/apparel-incoterms-exw-fob-ddp-landed-cost)\.html$/],
    ["Private label activewear program", /\/private-label-activewear-manufacturer\.html$/],
    ["Custom teamwear program", /\/custom-teamwear-uniforms\.html$/],
    ["Low MOQ launch planning", /\/low-moq-sportswear-manufacturer\.html$/],
    ["Supplier capability review", /\/sportswear-manufacturer\.html$/],
    ["Supplier verification and documents", /\/resources\/sportswear-manufacturer-due-diligence-checklist\.html$/],
    ["Supplier verification and documents", /\/(about-factory|certificates|factory-video)\.html$/],
    ["Custom fishing apparel", /custom-fishing-apparel/],
    ["Custom rowing uniforms", /custom-rowing-uniforms/],
    ["Pilates activewear", /pilates-activewear/],
    ["Flag football uniforms", /flag-football-uniforms/],
    ["Baseball uniforms", /(?:^|\/)baseball-uniforms/],
    ["Softball uniforms", /softball-uniforms/],
    ["Rugby uniforms", /(?:^|\/)rugby-uniforms/],
    ["Field hockey uniforms", /field-hockey-uniforms/],
    ["Custom running shorts", /custom-running-shorts/],
    ["Badminton uniforms", /badminton-uniforms/],
    ["Private label gym leggings", /private-label-gym-leggings/],
    ["Custom boxing apparel", /custom-boxing-apparel/],
    ["Custom handball uniforms", /custom-handball-uniforms/],
    ["Custom padel apparel", /custom-padel-apparel/],
    ["Custom futsal uniforms", /custom-futsal-uniforms/],
    ["Custom table tennis uniforms", /custom-table-tennis-uniforms/],
    ["Custom bowling shirts", /custom-bowling-shirts/],
    ["Custom darts shirts", /custom-darts-shirts/],
    ["Custom ultimate jerseys", /custom-ultimate-jerseys/],
    ["Custom weightlifting singlets", /custom-weightlifting-singlets/],
    ["Custom team polo shirts", /custom-team-polo-shirts/],
    ["Custom cycling skinsuits", /custom-cycling-skinsuits/],
    ["Custom triathlon suits", /custom-triathlon-suits/],
    ["Custom beach volleyball uniforms", /custom-beach-volleyball-uniforms/],
    ["Custom motocross jerseys", /custom-motocross-jerseys/],
    ["Custom referee uniforms", /custom-referee-uniforms/],
    ["Yoga leggings", /\/products\/yoga-leggings\.html$/],
    ["Seamless activewear", /\/products\/seamless-activewear\.html$/],
    ["Soccer uniforms", /\/products\/soccer-uniforms\.html$/],
    ["Yoga wear", /yoga|sports-bras|seamless-activewear|plus-size-activewear/],
    ["Athleisure", /athleisure|hoodies-sweatshirts|joggers-tracksuits|club-hoodies/],
    ["Training wear", /training-wear|gym-tshirts|training-shorts|private-label-gym|compression-base|outdoor-training/],
    ["Basketball wear", /basketball/],
    ["Custom teamwear program", /american-football|cricket-uniforms|netball-uniforms|ice-hockey-jerseys/],
    ["Football kits", /football|soccer/],
    ["Running wear", /running|track-field|marathon|triathlon|trail-hiking/],
    ["Tennis and pickleball apparel", /tennis|pickleball|racket-sports/],
    ["Golf apparel", /golf/],
    ["Baseball and softball teamwear", /baseball|softball/],
    ["Swimwear and water sports", /swimwear|rash-guards|water-sports/],
    ["Combat sports apparel", /combat-sports|mma|wrestling/],
    ["Accessories", /accessories|sports-socks|sports-caps-bags/],
    ["Packaging and one-stop service", /packaging|one-stop-service/],
  ];
  const match = routes.find(([, pattern]) => pattern.test(path));
  if (match) return match[0];

  const isSpecificProductPage = /\/products\/[^/]+\.html$/.test(path) &&
    !/\/(index|new-products|lookbook|more-sports)\.html$/.test(path);
  return isSpecificProductPage ? "Other custom sportswear" : "";
};

const inquiryContext = document.querySelector("[data-inquiry-context]");
const storedInquirySource = isContactPage ? readInquirySource() : null;
const storedProductDirection = isContactPage ? readStoredProductDirection() : null;
let storedProductShortlist = readStoredProductShortlist();
const storedFabricShortlist = isContactPage ? readStoredFabricShortlist() : [];
let inquiryContextDismissed = false;

const renderInquiryContextSummary = () => {
  if (!inquiryContext) return;
  const contextTitle = inquiryContext.querySelector("[data-inquiry-context-title]");
  const contextLabel = inquiryContext.querySelector("span");
  const contextParts = [
    storedInquirySource ? getShortPageTitle(storedInquirySource.title) : "",
    inquiryPrefill.values.buyer || "",
    inquiryPrefill.values.product || "",
    storedProductDirection?.label || "",
    storedProductShortlist.length ? `${storedProductShortlist.length} product direction${storedProductShortlist.length === 1 ? "" : "s"} shortlisted` : "",
    storedFabricShortlist.length ? `${storedFabricShortlist.length} fabric direction${storedFabricShortlist.length === 1 ? "" : "s"} shortlisted` : "",
  ].filter(Boolean);

  if (!contextParts.length || inquiryContextDismissed) {
    inquiryContext.hidden = true;
    return;
  }
  if (contextTitle) contextTitle.textContent = contextParts.join(" · ");
  if (contextLabel) {
    contextLabel.textContent = inquiryPrefill.hasValues || storedProductDirection || storedProductShortlist.length || storedFabricShortlist.length
      ? "Brief tailored for"
      : "Continuing from";
  }
  inquiryContext.hidden = false;
};

if (inquiryContext) {
  const productSelect = document.querySelector('[data-quote-form] select[name="product"]');
  const suggestedProduct = storedInquirySource ? getProductInterestForPath(storedInquirySource.path) : "";
  renderInquiryContextSummary();

  if (productSelect && !productSelect.value && suggestedProduct) {
    productSelect.value = suggestedProduct;
    productSelect.dataset.sourcePrefilled = suggestedProduct;
  }

  inquiryContext.querySelector("[data-inquiry-context-clear]")?.addEventListener("click", () => {
    try {
      sessionStorage.removeItem(inquirySourceKey);
      sessionStorage.removeItem(buyerPathStorageKey);
      sessionStorage.removeItem(productDirectionStorageKey);
      sessionStorage.removeItem(productShortlistStorageKey);
      sessionStorage.removeItem(fabricShortlistStorageKey);
    } catch {
      // The visual context can still be dismissed when storage is unavailable.
    }
    storedProductShortlist = [];
    inquiryContextDismissed = true;
    const fieldNames = { buyer: "buyerType", development: "developmentRoute", product: "product" };
    Object.values(fieldNames).forEach((fieldName) => {
      const field = document.querySelector(`[data-quote-form] [name="${fieldName}"]`);
      if (field?.value === field?.dataset.queryPrefilled) {
        field.value = "";
        field.dispatchEvent(new Event("change", { bubbles: true }));
      }
      if (field) delete field.dataset.queryPrefilled;
    });
    if (inquiryPrefill.hasValues) {
      const cleanedUrl = new URL(window.location.href);
      Object.keys(fieldNames).forEach((name) => cleanedUrl.searchParams.delete(name));
      window.history.replaceState({}, "", `${cleanedUrl.pathname}${cleanedUrl.search}${cleanedUrl.hash}`);
    }
    inquiryContext.hidden = true;
    if (productSelect?.value === productSelect?.dataset.sourcePrefilled) {
      productSelect.value = "";
      productSelect.dispatchEvent(new Event("change", { bubbles: true }));
    }
    if (productSelect) {
      delete productSelect.dataset.sourcePrefilled;
    }
    renderQuoteProductShortlistPanels("Product shortlist cleared from this brief.");
  });
}

const quoteProductShortlistPanels = [...quoteForms].map((form, index) => {
  const panel = document.createElement("section");
  const titleId = `quote-product-shortlist-title-${index + 1}`;
  panel.className = "quote-product-shortlist";
  panel.dataset.quoteProductShortlist = "";
  panel.hidden = true;
  panel.setAttribute("aria-labelledby", titleId);
  panel.innerHTML = `
    <div class="quote-product-shortlist-heading">
      <div><span>Multi-product brief</span><strong id="${titleId}">Selected product directions</strong></div>
      <small data-quote-product-shortlist-count>0 of 4 selected</small>
    </div>
    <p>Review the exact products included in this inquiry. Every send method will carry the same list.</p>
    <div class="quote-product-shortlist-items" data-quote-product-shortlist-items></div>
    <div class="quote-product-shortlist-footer">
      <span data-quote-product-shortlist-status role="status" aria-live="polite">Saved for this inquiry in the current browser tab.</span>
      <div>
        <a href="/products/" data-quote-product-shortlist-continue>Continue choosing products <span aria-hidden="true">→</span></a>
        <button type="button" data-quote-product-shortlist-clear>Clear shortlist</button>
      </div>
    </div>
  `;
  const insertionPoint = form.querySelector("[data-inquiry-context]") || form.querySelector("[data-quote-progress]");
  insertionPoint?.insertAdjacentElement("afterend", panel);
  return {
    panel,
    count: panel.querySelector("[data-quote-product-shortlist-count]"),
    items: panel.querySelector("[data-quote-product-shortlist-items]"),
    status: panel.querySelector("[data-quote-product-shortlist-status]"),
    clearButton: panel.querySelector("[data-quote-product-shortlist-clear]"),
    continueLink: panel.querySelector("[data-quote-product-shortlist-continue]"),
  };
});

const renderQuoteProductShortlistPanels = (message = "") => {
  quoteProductShortlistPanels.forEach(({ panel, count, items, status }) => {
    panel.hidden = storedProductShortlist.length === 0;
    if (count) count.textContent = `${storedProductShortlist.length} of 4 selected`;
    if (status) status.textContent = message || "Saved for this inquiry in the current browser tab.";
    if (!items) return;
    items.replaceChildren();
    storedProductShortlist.forEach((item) => {
      const row = document.createElement("article");
      row.className = "quote-product-shortlist-item";
      const copy = document.createElement("div");
      const indexLabel = document.createElement("span");
      indexLabel.textContent = `Product ${storedProductShortlist.indexOf(item) + 1}`;
      const link = document.createElement("a");
      link.href = item.path;
      link.textContent = item.label;
      copy.append(indexLabel, link);
      const removeButton = document.createElement("button");
      removeButton.type = "button";
      removeButton.textContent = "Remove";
      removeButton.setAttribute("aria-label", `Remove ${item.label} from this quote brief`);
      removeButton.addEventListener("click", () => {
        storedProductShortlist = storedProductShortlist.filter((candidate) => candidate.slug !== item.slug);
        saveStoredProductShortlist(storedProductShortlist);
        renderQuoteProductShortlistPanels(`${item.label} removed from this quote brief.`);
        renderInquiryContextSummary();
        trackEvent("quote_product_shortlist_edit", {
          action: "remove",
          product_slug: item.slug,
          selected_count: storedProductShortlist.length,
        });
      });
      row.append(copy, removeButton);
      items.append(row);
    });
  });
};

quoteProductShortlistPanels.forEach(({ clearButton, continueLink }) => {
  clearButton?.addEventListener("click", () => {
    const previousCount = storedProductShortlist.length;
    storedProductShortlist = [];
    saveStoredProductShortlist(storedProductShortlist);
    renderQuoteProductShortlistPanels("Product shortlist cleared from this brief.");
    renderInquiryContextSummary();
    trackEvent("quote_product_shortlist_clear", { previous_count: previousCount });
  });
  continueLink?.addEventListener("click", () => {
    trackEvent("quote_product_shortlist_continue", { selected_count: storedProductShortlist.length });
  });
});

renderQuoteProductShortlistPanels();

const calculateQuoteReadiness = (form) => {
  const data = new FormData(form);
  const projectDetails = String(data.get("message") || "").trim();
  const referenceLinkField = form.querySelector("[data-reference-link]");
  const hasValidReferenceLink = Boolean(referenceLinkField?.value && referenceLinkField.checkValidity());
  const hasReferenceFiles = getReferenceFiles(form).length > 0;
  const items = [
    {
      key: "product",
      label: "Choose a product category",
      fieldName: "product",
      complete: Boolean(String(data.get("product") || "").trim()),
    },
    {
      key: "quantity",
      label: "Add estimated quantity",
      fieldName: "quantity",
      complete: Boolean(String(data.get("quantity") || "").trim()),
    },
    {
      key: "project_details",
      label: "Add more product detail",
      fieldName: "message",
      complete: projectDetails.length >= 60,
    },
    {
      key: "market",
      label: "Add delivery market",
      fieldName: "market",
      complete: Boolean(String(data.get("market") || "").trim()),
    },
    {
      key: "timeline",
      label: "Add a target date",
      fieldName: "timeline",
      complete: Boolean(String(data.get("timeline") || "").trim()),
    },
    {
      key: "development_route",
      label: "Choose a development route",
      fieldName: "developmentRoute",
      complete: Boolean(String(data.get("developmentRoute") || "").trim()),
    },
    {
      key: "references",
      label: "Add a view-only reference link",
      fieldName: hasReferenceFiles ? "referenceFiles" : "referenceLink",
      complete: hasReferenceFiles || hasValidReferenceLink,
    },
  ];
  const completedCount = items.filter((item) => item.complete).length;
  const totalCount = items.length;
  const missingItems = items.filter((item) => !item.complete);
  const coreInputsComplete = ["product", "quantity", "project_details"]
    .every((key) => items.find((item) => item.key === key)?.complete);
  const level = completedCount === totalCount
    ? { key: "well-scoped", label: "Complete project context" }
    : completedCount >= 5 && coreInputsComplete
      ? { key: "review-ready", label: "Strong project context" }
      : completedCount >= 3
        ? { key: "good-start", label: "Useful project context" }
        : { key: "starting", label: "Starting project context" };
  const summary = completedCount === totalCount
    ? "All seven optional planning inputs are prepared for an initial project review."
    : level.key === "review-ready"
      ? "Strong project context is ready. Adding the remaining optional inputs can reduce follow-up questions."
      : completedCount >= 5
        ? "Add the missing product, quantity, or project-detail input to make the scope easier to review."
        : "Optional commercial and technical context helps us identify the appropriate review, sample, or quotation route.";

  return { available: true, items, missingItems, completedCount, totalCount, coreInputsComplete, level, summary };
};

const getQuoteReadiness = (form) => {
  try {
    return calculateQuoteReadiness(form);
  } catch {
    return {
      available: false,
      items: [],
      missingItems: [],
      completedCount: 0,
      totalCount: 7,
      coreInputsComplete: false,
      level: { key: "unavailable", label: "Optional guidance unavailable" },
      summary: "You can still complete and send the required inquiry fields.",
    };
  }
};

const getInquiryLines = (form) => {
  const data = new FormData(form);
  const referenceFiles = [...(form.querySelector("[data-reference-files]")?.files || [])];
  const referenceFileNames = referenceFiles
    .map((file) => file.name.replace(/[\r\n\t]/g, " ").slice(0, 120))
    .join(", ");
  const attribution = readAttribution() || pageAttribution;
  const trafficAttribution = classifyAttribution(attribution);
  const campaign = Object.entries(attribution?.campaign || {})
    .map(([name, value]) => `${name}=${value}`)
    .join(" | ");
  const attributionLines = [
    `Source Channel: ${trafficAttribution.channel}`,
    `Source Platform: ${trafficAttribution.source}`,
    campaign ? `Campaign: ${campaign}` : "",
    attribution?.landingPage ? `Landing Page: ${attribution.landingPage}` : "",
    attribution?.referrer ? `Referrer: ${attribution.referrer}` : "",
  ].filter(Boolean);
  const productDirection = isContactPage ? readStoredProductDirection() : null;
  const productShortlist = readStoredProductShortlist()
    .map((item) => `${item.label} (${item.path})`)
    .join(" | ");
  const fabricShortlist = (isContactPage ? readStoredFabricShortlist() : [])
    .map((item) => `${item.id} — ${item.name}`)
    .join(" | ");

  return [
    `Name: ${data.get("name")}`,
    `Email: ${data.get("email")}`,
    `WhatsApp or Phone: ${data.get("phone") || "Not provided"}`,
    `Buyer Type: ${data.get("buyerType") || "Not provided"}`,
    `Development Route: ${data.get("developmentRoute") || "Not sure yet"}`,
    `Product Interest: ${data.get("product")}`,
    `Product Direction: ${productDirection?.label || "Not specified"}`,
    `Product Shortlist: ${productShortlist || "None"}`,
    `Fabric Shortlist: ${fabricShortlist || "None"}`,
    `Estimated Quantity: ${data.get("quantity") || "Not provided"}`,
    `Target Market: ${data.get("market") || "Not provided"}`,
    `Expected Timeline: ${data.get("timeline") || "Not provided"}`,
    `Preferred Contact: ${data.get("preferredContact") || "No preference"}`,
    `Call Request: ${data.get("callRequest") || "No call requested"}`,
    `Reference Files Selected: ${referenceFileNames || "None"}`,
    `Reference File Transfer: ${referenceFileNames ? "Attach selected local files through the chosen send method" : "No local files selected"}`,
    `Reference File Link: ${data.get("referenceLink") || "None"}`,
    `Source Page: ${getInquirySource()}`,
    ...attributionLines,
    "",
    "Project Details:",
    data.get("message"),
  ];
};

const getInquiryPayload = (form) => {
  const data = new FormData(form);
  const referenceFiles = [...(form.querySelector("[data-reference-files]")?.files || [])];
  const referenceFileNames = referenceFiles
    .map((file) => file.name.replace(/[\r\n\t]/g, " ").slice(0, 120))
    .join(", ");
  const productDirection = isContactPage ? readStoredProductDirection() : null;
  const productShortlist = readStoredProductShortlist()
    .map((item) => `${item.label} (${item.path})`)
    .join(" | ");
  const fabricShortlist = (isContactPage ? readStoredFabricShortlist() : [])
    .map((item) => `${item.id} — ${item.name}`)
    .join(" | ");
  const quoteReadiness = getQuoteReadiness(form);
  const projectMessage = [
    `Buyer Type: ${data.get("buyerType") || "Not provided"}`,
    `Development Route: ${data.get("developmentRoute") || "Not sure yet"}`,
    `Preferred Contact: ${data.get("preferredContact") || "No preference"}`,
    `Call Request: ${data.get("callRequest") || "No call requested"}`,
    `Product Direction: ${productDirection?.label || "Not specified"}`,
    `Product Shortlist: ${productShortlist || "None"}`,
    `Fabric Shortlist: ${fabricShortlist || "None"}`,
    `Reference Files Selected: ${referenceFileNames || "None"}`,
    `Reference File Transfer: ${referenceFileNames ? "Attach selected local files through the chosen send method" : "No local files selected"}`,
    `Reference File Link: ${data.get("referenceLink") || "None"}`,
    "",
    String(data.get("message") || ""),
  ].join("\n");
  const attribution = readAttribution() || pageAttribution;
  const trafficAttribution = classifyAttribution(attribution);
  let submissionId = quoteSubmissionIds.get(form) || "";
  if (!submissionId && typeof crypto.randomUUID === "function") {
    submissionId = crypto.randomUUID();
    quoteSubmissionIds.set(form, submissionId);
  }

  return {
    payloadVersion: 2,
    submissionId,
    turnstileToken: turnstileStates.get(form)?.token || "",
    name: data.get("name"),
    email: data.get("email"),
    phone: data.get("phone"),
    buyerType: data.get("buyerType"),
    developmentRoute: data.get("developmentRoute"),
    briefReadiness: {
      version: 1,
      completed: quoteReadiness.completedCount,
      total: quoteReadiness.totalCount,
      level: quoteReadiness.level.key,
    },
    product: data.get("product"),
    quantity: data.get("quantity"),
    market: data.get("market"),
    timeline: data.get("timeline"),
    projectDetails: data.get("message"),
    message: projectMessage,
    companyWebsite: data.get("companyWebsite"),
    consent: data.get("consent") === "on",
    sourcePage: getInquirySource(),
    landingPage: attribution?.landingPage || "",
    referrer: attribution?.referrer || "",
    trafficChannel: trafficAttribution.channel,
    trafficSource: trafficAttribution.source,
    campaign: attribution?.campaign || {},
  };
};

const setFormNote = (form, message, state) => {
  const note = form.querySelector("[data-form-note]");
  if (!note) return;
  note.textContent = message;
  note.dataset.state = state;
};

const copyText = async (value) => {
  if (navigator.clipboard && window.isSecureContext) {
    await navigator.clipboard.writeText(value);
    return true;
  }

  const textarea = document.createElement("textarea");
  textarea.value = value;
  textarea.setAttribute("readonly", "");
  textarea.style.position = "fixed";
  textarea.style.opacity = "0";
  document.body.append(textarea);
  textarea.select();

  try {
    return document.execCommand("copy");
  } finally {
    textarea.remove();
  }
};

const fetchWithTimeout = (url, options = {}, timeoutMilliseconds = 8000) => {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), timeoutMilliseconds);

  return fetch(url, { ...options, signal: controller.signal })
    .finally(() => window.clearTimeout(timeout));
};

const loadTurnstile = () => {
  if (window.turnstile) return Promise.resolve(window.turnstile);
  if (turnstileScriptPromise) return turnstileScriptPromise;

  turnstileScriptPromise = new Promise((resolve, reject) => {
    const callbackName = "glorystarwearTurnstileReady";
    const script = document.createElement("script");
    const timeout = window.setTimeout(() => reject(new Error("turnstile_timeout")), 10000);
    window[callbackName] = () => {
      window.clearTimeout(timeout);
      delete window[callbackName];
      if (window.turnstile) resolve(window.turnstile);
      else reject(new Error("turnstile_unavailable"));
    };
    script.src = `https://challenges.cloudflare.com/turnstile/v0/api.js?onload=${callbackName}&render=explicit`;
    script.async = true;
    script.defer = true;
    script.addEventListener("error", () => {
      window.clearTimeout(timeout);
      delete window[callbackName];
      reject(new Error("turnstile_load_failed"));
    }, { once: true });
    document.head.append(script);
  });

  return turnstileScriptPromise;
};

const setupTurnstile = async (form, siteKey) => {
  const container = form.querySelector("[data-turnstile-container]");
  const widget = form.querySelector("[data-turnstile-widget]");
  if (!container || !widget || !siteKey) throw new Error("turnstile_not_configured");

  const turnstile = await loadTurnstile();
  const state = { token: "", widgetId: "" };
  state.widgetId = turnstile.render(widget, {
    sitekey: siteKey,
    theme: "light",
    size: "flexible",
    callback: (token) => {
      state.token = token;
      setFormNote(form, "Human verification complete. You can submit the inquiry securely.", "success");
    },
    "expired-callback": () => {
      state.token = "";
      setFormNote(form, "Human verification expired. Please verify again before secure submission.", "error");
    },
    "error-callback": () => {
      state.token = "";
      setFormNote(form, "Human verification is unavailable. Please use WhatsApp or email.", "error");
    },
  });
  turnstileStates.set(form, state);
  container.hidden = false;
};

const resetTurnstile = (form) => {
  const state = turnstileStates.get(form);
  if (state) state.token = "";
  if (state?.widgetId && window.turnstile) window.turnstile.reset(state.widgetId);
};

const referenceFileRules = {
  maximumCount: 5,
  maximumTotalBytes: 20 * 1024 * 1024,
  allowedExtensions: new Set(["pdf", "csv", "xlsx", "xls", "doc", "docx", "png", "jpg", "jpeg", "webp"]),
};

const getReferenceFiles = (form) =>
  [...(form.querySelector("[data-reference-files]")?.files || [])];

const getReferenceFileExtension = (file) =>
  file.name.toLowerCase().split(".").pop()?.replace(/[^a-z0-9]/g, "") || "unknown";

const validateReferenceFiles = (files) => {
  if (files.length > referenceFileRules.maximumCount) {
    return { valid: false, reason: "too_many_files", message: "Choose no more than 5 reference files." };
  }
  if (files.some((file) => !referenceFileRules.allowedExtensions.has(getReferenceFileExtension(file)))) {
    return { valid: false, reason: "unsupported_type", message: "Use PDF, spreadsheet, Word, PNG, JPG, or WebP files only." };
  }
  const totalBytes = files.reduce((sum, file) => sum + file.size, 0);
  if (totalBytes > referenceFileRules.maximumTotalBytes) {
    return { valid: false, reason: "total_size", message: "Keep the combined file size at or below 20 MB." };
  }
  return { valid: true, totalBytes };
};

const canShareReferenceFiles = (files) => {
  if (!files.length || typeof navigator.share !== "function" || typeof navigator.canShare !== "function") return false;
  try {
    return navigator.canShare({ files });
  } catch {
    return false;
  }
};

quoteForms.forEach((form, formIndex) => {
  let hasStartedQuote = false;
  let highestProgressMilestone = 0;
  let highestReadinessMilestone = 0;
  let lastReadinessSignature = "";
  let serverSubmissionAvailable = false;
  let secureSubmissionStarted = false;
  const leadEndpoint = form.dataset.leadEndpoint || "";
  const serverSubmitButton = form.querySelector("[data-server-submit]");
  const quoteProgress = form.querySelector("[data-quote-progress]");
  const quoteProgressLabel = form.querySelector("[data-quote-progress-label]");
  const quoteProgressMeter = form.querySelector("[data-quote-progress-meter]");
  const requiredFields = [...form.querySelectorAll("input[required], select[required], textarea[required]")];
  const quoteReadiness = document.createElement("section");
  const quoteReadinessTitleId = `quote-readiness-title-${formIndex + 1}`;
  quoteReadiness.className = "quote-readiness";
  quoteReadiness.dataset.quoteReadiness = "";
  quoteReadiness.setAttribute("aria-labelledby", quoteReadinessTitleId);
  quoteReadiness.innerHTML = `
    <div class="quote-readiness-heading">
      <div><span>Optional planning guidance</span><strong id="${quoteReadinessTitleId}">Improve your project brief</strong></div>
      <small data-quote-readiness-status role="status" aria-live="polite" aria-atomic="true">Starting project context · 0 of 7</small>
    </div>
    <p data-quote-readiness-summary>Optional commercial and technical context helps us identify the appropriate review, sample, or quotation route.</p>
    <div class="quote-readiness-prompts" data-quote-readiness-prompts role="group" aria-label="Useful next inputs"></div>
    <small class="quote-readiness-boundary">These inputs are optional and do not block sending. MOQ, feasibility, sample scope, price, and timing are confirmed after review. Selected local files still need to be attached through the chosen send method; shared links must be viewable.</small>
  `;
  const quoteReadinessInsertionPoint = form.querySelector("[data-reference-link]")?.closest("label")
    || form.querySelector('[name="message"]')?.closest("label");
  quoteReadinessInsertionPoint?.insertAdjacentElement("afterend", quoteReadiness);
  const quoteReadinessStatus = quoteReadiness.querySelector("[data-quote-readiness-status]");
  const quoteReadinessSummary = quoteReadiness.querySelector("[data-quote-readiness-summary]");
  const quoteReadinessPrompts = quoteReadiness.querySelector("[data-quote-readiness-prompts]");
  const trackQuoteStart = () => {
    if (hasStartedQuote) return;
    hasStartedQuote = true;
    trackEvent("quote_start", { form_location: window.location.pathname });
  };

  const updateQuoteProgress = (shouldTrack = false) => {
    const completedFields = requiredFields.filter((field) => {
      if (field.type === "checkbox" || field.type === "radio") return field.checked;
      return Boolean(field.value.trim()) && field.checkValidity();
    }).length;
    const totalFields = requiredFields.length;
    const isComplete = totalFields > 0 && completedFields === totalFields;

    if (quoteProgressLabel) {
      quoteProgressLabel.textContent = isComplete
        ? `${completedFields} of ${totalFields} essentials ready — choose how to send`
        : `${completedFields} of ${totalFields} essentials ready`;
    }
    if (quoteProgressMeter) {
      quoteProgressMeter.max = totalFields || 1;
      quoteProgressMeter.value = completedFields;
    }
    if (quoteProgress) quoteProgress.dataset.complete = String(isComplete);

    if (!shouldTrack || !totalFields) return;
    const progressPercent = Math.round((completedFields / totalFields) * 100);
    const reachedMilestone = [100, 75, 50, 25]
      .find((milestone) => progressPercent >= milestone) || 0;
    if (reachedMilestone <= highestProgressMilestone) return;
    highestProgressMilestone = reachedMilestone;
    trackEvent("quote_progress", {
      form_location: window.location.pathname,
      progress_percent: reachedMilestone,
      completed_fields: completedFields,
      required_fields: totalFields,
    });
  };

  const renderQuoteReadiness = (shouldTrack = false) => {
    const readiness = getQuoteReadiness(form);
    if (!readiness.available) {
      quoteReadiness.hidden = true;
      return;
    }
    const readinessSignature = readiness.items.map((item) => Number(item.complete)).join("");
    if (readinessSignature !== lastReadinessSignature) {
      quoteReadiness.dataset.level = readiness.level.key;
      if (quoteReadinessStatus) {
        quoteReadinessStatus.textContent = `${readiness.level.label} · ${readiness.completedCount} of ${readiness.totalCount}`;
      }
      if (quoteReadinessSummary) quoteReadinessSummary.textContent = readiness.summary;
    }

    if (quoteReadinessPrompts && readinessSignature !== lastReadinessSignature) {
      quoteReadinessPrompts.replaceChildren();
      if (!readiness.missingItems.length) {
        const completeNote = document.createElement("span");
        completeNote.className = "quote-readiness-complete";
        completeNote.textContent = "All optional planning inputs are prepared for initial review.";
        quoteReadinessPrompts.append(completeNote);
      } else {
        const promptLabel = document.createElement("span");
        promptLabel.className = "quote-readiness-prompt-label";
        promptLabel.textContent = "Useful next inputs";
        quoteReadinessPrompts.append(promptLabel);
        readiness.missingItems.slice(0, 3).forEach((item) => {
          const prompt = document.createElement("button");
          prompt.type = "button";
          prompt.textContent = item.label;
          prompt.dataset.quoteReadinessTarget = item.fieldName;
          prompt.addEventListener("click", () => {
            const targetField = form.querySelector(`[name="${item.fieldName}"]`);
            if (!targetField) return;
            const reducedMotion = typeof window.matchMedia === "function"
              && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
            targetField.scrollIntoView({ behavior: reducedMotion ? "auto" : "smooth", block: "center" });
            targetField.focus({ preventScroll: true });
            trackEvent("quote_readiness_prompt_select", {
              prompt_key: item.key,
              completed_inputs: readiness.completedCount,
              form_location: window.location.pathname,
            });
          });
          quoteReadinessPrompts.append(prompt);
        });
        if (readiness.missingItems.length > 3) {
          const remainingNote = document.createElement("small");
          remainingNote.className = "quote-readiness-more";
          remainingNote.textContent = `+${readiness.missingItems.length - 3} more after these`;
          quoteReadinessPrompts.append(remainingNote);
        }
      }
      lastReadinessSignature = readinessSignature;
    }

    if (!shouldTrack || !readiness.totalCount) return;
    const readinessPercent = Math.round((readiness.completedCount / readiness.totalCount) * 100);
    const reachedMilestone = [100, 75, 50, 25]
      .find((milestone) => readinessPercent >= milestone) || 0;
    if (reachedMilestone <= highestReadinessMilestone) return;
    highestReadinessMilestone = reachedMilestone;
    trackEvent("quote_readiness_progress", {
      form_location: window.location.pathname,
      progress_percent: reachedMilestone,
      completed_inputs: readiness.completedCount,
      missing_inputs: readiness.missingItems.map((item) => item.key).join("|").slice(0, 180),
    });
  };

  const updateQuoteReadiness = (shouldTrack = false) => {
    try {
      renderQuoteReadiness(shouldTrack);
    } catch {
      quoteReadiness.hidden = true;
    }
  };

  const handleQuoteUpdate = (event) => {
    const updatedField = event.target;
    if (updatedField?.matches?.("input, select, textarea") && updatedField.checkValidity()) {
      updatedField.removeAttribute("aria-invalid");
    }
    trackQuoteStart();
    updateQuoteProgress(true);
    updateQuoteReadiness(true);
  };

  form.addEventListener("input", handleQuoteUpdate);
  form.addEventListener("change", handleQuoteUpdate);

  const buyerTypeSelect = form.querySelector('[name="buyerType"]');
  const productSelect = form.querySelector('[name="product"]');
  buyerTypeSelect?.addEventListener("change", () => {
    const suggestion = productSuggestionsByBuyerType[buyerTypeSelect.value] || "";
    const previousSuggestion = productSelect?.dataset.buyerSuggested || "";
    const canUpdateProduct = productSelect && (!productSelect.value || productSelect.value === previousSuggestion);
    if (canUpdateProduct) {
      productSelect.value = suggestion;
      if (suggestion) productSelect.dataset.buyerSuggested = suggestion;
      else delete productSelect.dataset.buyerSuggested;
    }
    updateQuoteProgress(true);
    if (buyerTypeSelect.value) {
      trackEvent("buyer_type_select", {
        buyer_type: buyerTypeSelect.value,
        product_suggested: Boolean(canUpdateProduct && suggestion),
      });
    }
  });
  updateQuoteProgress();
  updateQuoteReadiness();

  const validateQuoteForm = (sendMethod) => {
    if (form.checkValidity()) return true;
    const invalidFieldElements = [...form.querySelectorAll("input, select, textarea")]
      .filter((field) => !field.checkValidity());
    invalidFieldElements.forEach((field) => field.setAttribute("aria-invalid", "true"));
    const invalidFields = invalidFieldElements
      .map((field) => field.name)
      .filter(Boolean);
    setFormNote(
      form,
      `Complete or correct the ${invalidFields.length === 1 ? "field" : "fields"} highlighted above before sending.`,
      "error",
    );
    trackEvent("quote_validation_error", {
      send_method: sendMethod,
      missing_fields: invalidFields.join("|"),
      missing_count: invalidFields.length,
    });
    form.reportValidity();
    return false;
  };

  const referenceFileInput = form.querySelector("[data-reference-files]");
  const referenceFileStatus = form.querySelector("[data-reference-file-status]");
  const shareFilesButton = form.querySelector("[data-share-files]");
  const referenceLinkInput = form.querySelector("[data-reference-link]");

  referenceFileInput?.addEventListener("change", () => {
    const files = getReferenceFiles(form);
    const validation = validateReferenceFiles(files);

    if (!validation.valid) {
      referenceFileInput.value = "";
      if (referenceFileStatus) referenceFileStatus.textContent = `${validation.message} No file was attached.`;
      if (shareFilesButton) shareFilesButton.hidden = true;
      setFormNote(form, validation.message, "error");
      trackEvent("quote_reference_files_rejected", { rejection_reason: validation.reason });
      return;
    }

    if (!files.length) {
      if (referenceFileStatus) referenceFileStatus.textContent = "Choose up to 5 files, 20 MB total. The secure form records filenames only; supported devices can share the files through the system share menu.";
      if (shareFilesButton) shareFilesButton.hidden = true;
      return;
    }

    const totalMegabytes = (validation.totalBytes / (1024 * 1024)).toFixed(1);
    const shareAvailable = canShareReferenceFiles(files);
    if (referenceFileStatus) {
      referenceFileStatus.textContent = `${files.length} file${files.length === 1 ? "" : "s"} selected (${totalMegabytes} MB). ${shareAvailable ? "Use “Share Brief + Files” to pass them through your device." : "Attach them manually after WhatsApp or email opens; the secure form sends filenames only."}`;
    }
    if (shareFilesButton) shareFilesButton.hidden = !shareAvailable;
    trackEvent("quote_reference_files_selected", {
      file_count: files.length,
      file_types: [...new Set(files.map(getReferenceFileExtension))].join("|"),
      total_size_bucket: validation.totalBytes <= 5 * 1024 * 1024 ? "0_5mb" : validation.totalBytes <= 10 * 1024 * 1024 ? "5_10mb" : "10_20mb",
    });
  });

  referenceLinkInput?.addEventListener("change", () => {
    if (!referenceLinkInput.value || !referenceLinkInput.checkValidity()) return;
    trackEvent("quote_reference_link_added", { has_reference_link: true });
  });

  form.querySelector('[name="callRequest"]')?.addEventListener("change", (event) => {
    if (!event.currentTarget.value) return;
    trackEvent("call_request_select", { call_request_type: event.currentTarget.value });
  });

  const initializeSecureSubmission = () => {
    if (secureSubmissionStarted || !leadEndpoint || !serverSubmitButton) return;
    secureSubmissionStarted = true;
    fetchWithTimeout(leadEndpoint, {
      method: "GET",
      mode: "cors",
      cache: "no-store",
      headers: { Accept: "application/json" },
    }, 4000)
      .then((response) => response.ok ? response.json() : { configured: false })
      .then(async (status) => {
        if (!status.configured || !status.turnstileSiteKey) return;
        await setupTurnstile(form, status.turnstileSiteKey);
        serverSubmissionAvailable = true;
        serverSubmitButton.hidden = false;
        setFormNote(form, "Secure server submission is available. Complete the human verification, then submit.", "success");
      })
      .catch(() => {
        // WhatsApp, email, and copy remain available when the server check cannot complete.
      });
  };

  if (leadEndpoint && serverSubmitButton) {
    form.addEventListener("focusin", initializeSecureSubmission, { once: true });
    if ("IntersectionObserver" in window) {
      const secureSubmissionObserver = new IntersectionObserver((entries, observer) => {
        if (!entries.some((entry) => entry.isIntersecting)) return;
        observer.disconnect();
        initializeSecureSubmission();
      }, { rootMargin: "300px 0px" });
      secureSubmissionObserver.observe(form);
    } else {
      initializeSecureSubmission();
    }
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!validateQuoteForm("secure")) return;

    if (!serverSubmissionAvailable || !leadEndpoint || !serverSubmitButton) {
      form.querySelector("[data-whatsapp-inquiry]")?.click();
      return;
    }

    if (!turnstileStates.get(form)?.token) {
      setFormNote(form, "Complete the human verification before secure submission, or use WhatsApp or email.", "error");
      return;
    }

    const data = new FormData(form);
    serverSubmitButton.disabled = true;
    setFormNote(form, "Sending your inquiry securely...", "opening");

    try {
      const response = await fetchWithTimeout(leadEndpoint, {
        method: "POST",
        mode: "cors",
        cache: "no-store",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify(getInquiryPayload(form)),
      }, 18000);

      const result = await response.json().catch(() => ({}));
      if (!response.ok || !result.ok) {
        throw new Error(result.error || `HTTP ${response.status}`);
      }

      trackEvent("lead_submit_success", {
        form_location: window.location.pathname,
        product_interest: data.get("product") || "",
      });
      if (storeLeadReceipt()) {
        window.location.assign(new URL("/thank-you.html", window.location.href).href);
      } else {
        setFormNote(
          form,
          "Your inquiry was received, but this browser could not open the one-time confirmation page. Please keep this page for your records.",
          "success",
        );
      }
    } catch {
      setFormNote(
        form,
        "We could not confirm receipt, so this inquiry has not been marked as received. Please use WhatsApp or email instead.",
        "error",
      );
      trackEvent("lead_submit_error", {
        form_location: window.location.pathname,
        product_interest: data.get("product") || "",
      });
      serverSubmitButton.disabled = false;
      resetTurnstile(form);
    }
  });

  form.querySelector("[data-whatsapp-inquiry]")?.addEventListener("click", () => {
    if (!validateQuoteForm("whatsapp")) return;

    const files = getReferenceFiles(form);
    const text = encodeURIComponent(
      ["Hi GloryStarWear, I want to start a custom sportswear project.", "", ...getInquiryLines(form)].join(
        "\n",
      ),
    );
    setFormNote(
      form,
      files.length
        ? "Opening WhatsApp with the project brief. Attach the selected files manually in the chat."
        : "Opening WhatsApp with the project brief...",
      "opening",
    );
    trackEvent("whatsapp_click", {
      link_context: "quote_form",
      cta_location: "form",
      product_interest: new FormData(form).get("product") || "",
    });
    const whatsappLink = document.createElement("a");
    whatsappLink.href = `https://wa.me/${whatsappNumber}?text=${text}`;
    whatsappLink.target = "_blank";
    whatsappLink.rel = "noreferrer";
    whatsappLink.click();
  });

  form.querySelector("[data-email-inquiry]")?.addEventListener("click", () => {
    if (!validateQuoteForm("email")) return;

    const data = new FormData(form);
    const files = getReferenceFiles(form);
    const subject = encodeURIComponent(`GloryStarWear inquiry - ${data.get("product")}`);
    const body = encodeURIComponent(getInquiryLines(form).join("\n"));

    setFormNote(
      form,
      files.length
        ? "Opening your email app. Attach the selected files manually, then send the message. It is not counted as received until it reaches the mailbox."
        : "Opening your email app. This is not counted as received until you send the message and it reaches the mailbox.",
      "opening",
    );
    trackEvent("email_click", {
      link_context: "quote_form",
      cta_location: "form",
      product_interest: data.get("product") || "",
    });
    window.location.href = `mailto:kevin@glorystarwears.com?subject=${subject}&body=${body}`;
  });

  form.querySelector("[data-copy-inquiry]")?.addEventListener("click", async (event) => {
    if (!validateQuoteForm("copy")) return;

    const button = event.currentTarget;
    const data = new FormData(form);
    const text = [
      "GloryStarWear custom sportswear inquiry",
      "",
      ...getInquiryLines(form),
    ].join("\n");

    button.disabled = true;
    try {
      const copied = await copyText(text);
      if (!copied) throw new Error("Clipboard access was unavailable");

      setFormNote(
        form,
        "Project brief copied. Paste it into your preferred email or messaging app.",
        "success",
      );
      trackEvent("quote_copy_brief", { product_interest: data.get("product") || "" });
    } catch {
      setFormNote(form, "Copy failed. Please use Email Inquiry or WhatsApp instead.", "error");
    } finally {
      button.disabled = false;
    }
  });

  shareFilesButton?.addEventListener("click", async () => {
    if (!validateQuoteForm("share")) return;

    const files = getReferenceFiles(form);
    const validation = validateReferenceFiles(files);
    if (!validation.valid || !canShareReferenceFiles(files)) {
      setFormNote(form, "File sharing is unavailable on this device. Use WhatsApp or email and attach the files manually.", "error");
      return;
    }

    shareFilesButton.disabled = true;
    try {
      await navigator.share({
        title: "GloryStarWear project brief",
        text: ["GloryStarWear custom sportswear inquiry", "", ...getInquiryLines(form)].join("\n"),
        files,
      });
      setFormNote(form, "Your device share menu accepted the brief and files. Confirm delivery in the app you selected.", "success");
      trackEvent("quote_reference_files_shared", {
        file_count: files.length,
        file_types: [...new Set(files.map(getReferenceFileExtension))].join("|"),
      });
    } catch (error) {
      if (error?.name !== "AbortError") {
        setFormNote(form, "The device could not share these files. Use WhatsApp or email and attach them manually.", "error");
      }
    } finally {
      shareFilesButton.disabled = false;
    }
  });
});

if ("IntersectionObserver" in window) {
  const quoteFormObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting || entry.intersectionRatio < 0.25) return;
      trackEvent("quote_form_view", { form_location: window.location.pathname });
      observer.unobserve(entry.target);
    });
  }, { threshold: [0.25] });
  quoteForms.forEach((form) => quoteFormObserver.observe(form));
}

document.querySelectorAll("[data-buyer-path]").forEach((link) => {
  link.addEventListener("click", () => {
    const buyerPath = link.dataset.buyerPath || "unknown";
    try {
      sessionStorage.setItem(buyerPathStorageKey, JSON.stringify({ buyerPath, savedAt: Date.now() }));
    } catch {
      // The planning link still works when storage is unavailable.
    }
    trackEvent("buyer_path_select", { buyer_path: buyerPath });
  });
});

document.querySelectorAll("[data-buyer-quote]").forEach((link) => {
  link.addEventListener("click", () => {
    trackEvent("buyer_quote_select", { buyer_path: link.dataset.buyerQuote || "unknown" });
  });
});

const setupProductDetailExplorer = () => {
  const productPathMatch = window.location.pathname.match(/\/products\/([^/]+)\.html$/);
  const excludedProductPages = new Set(["index", "lookbook", "new-products", "more-sports"]);
  const productSlug = productPathMatch?.[1] || "";
  if (!productSlug || excludedProductPages.has(productSlug)) return;

  const hero = document.querySelector("main > .product-hero");
  const skuCards = [...document.querySelectorAll(".sku-card")];
  if (!hero || !skuCards.length) return;

  const productName = hero.querySelector("h1")?.textContent.trim() || "Product details";
  const productSummary = hero.querySelector(".product-hero-content > p:not(.eyebrow)")?.textContent.trim() ||
    "Review the product direction, customization inputs, and approval points before sampling.";

  skuCards.forEach((card, index) => {
    const directionLabel = card.querySelector("h3")?.textContent.trim() || `Product direction ${index + 1}`;
    const cardContent = card.querySelector("div");
    if (!cardContent || cardContent.querySelector(".sku-quote-link")) return;
    const actions = document.createElement("nav");
    actions.className = "sku-card-actions";
    actions.setAttribute("aria-label", `${directionLabel} actions`);
    const existingDetailLink = cardContent.querySelector(".detail-link");
    if (existingDetailLink) actions.append(existingDetailLink);
    const quoteLink = document.createElement("a");
    quoteLink.className = "detail-link sku-quote-link";
    quoteLink.href = "../contact.html#quote-form";
    quoteLink.textContent = "Ask about this direction";
    quoteLink.addEventListener("click", () => {
      try {
        sessionStorage.setItem(productDirectionStorageKey, JSON.stringify({
          label: directionLabel,
          sourcePath: window.location.pathname,
          savedAt: Date.now(),
        }));
      } catch {
        // The quote link still works when storage is unavailable.
      }
      trackEvent("product_direction_quote_select", {
        product_slug: productSlug,
        direction_label: directionLabel.slice(0, 80),
      });
    });
    actions.append(quoteLink);
    cardContent.append(actions);
  });

  const mediaItems = [];
  const seenImageSources = new Set();
  const addMediaItem = (picture, title, description) => {
    const image = picture?.querySelector("img");
    const imageSource = image?.getAttribute("src") || "";
    if (!picture || !imageSource || seenImageSources.has(imageSource)) return;
    if (!image.dataset.evidenceStatus) image.dataset.evidenceStatus = "illustrative";
    if (!image.dataset.mediaKind) image.dataset.mediaKind = "product-planning-reference";
    picture.dataset.evidenceStatus = image.dataset.evidenceStatus;
    if (image.alt && !image.alt.toLowerCase().startsWith("illustrative product-planning reference")) {
      image.alt = `Illustrative product-planning reference: ${image.alt}`;
    }
    seenImageSources.add(imageSource);
    mediaItems.push({ picture, title, description });
  };

  addMediaItem(hero.querySelector("picture"), "Collection overview", productSummary);
  skuCards.forEach((card, index) => {
    const title = card.querySelector("h3")?.textContent.trim() || `Product direction ${index + 1}`;
    const description = card.querySelector("li, p")?.textContent.trim() || "Review this direction against the approved specification and sample.";
    addMediaItem(card.querySelector("picture"), title, description);
  });
  const visibleMediaItems = mediaItems.slice(0, 6);
  if (!visibleMediaItems.length) return;
  const evidenceSlotLabels = /accessories|caps|bags|packaging|socks/.test(productSlug)
    ? ["Exterior", "Interior", "Base or reverse", "Closure and construction", "Logo or decoration"]
    : ["Front", "Back", "Fabric macro", "Stitch or seam macro", "Print or decoration macro"];
  const planningResource = /basketball|football|futsal|soccer|volleyball|baseball|softball|rugby|hockey|cricket|netball|lacrosse|teamwear|team-polo|referee|cheer|esports|wrestling|badminton|handball|table-tennis|bowling|darts|ultimate/.test(productSlug)
    ? {
        href: "../assets/downloads/teamwear-roster-packing-template.csv",
        name: "Teamwear Roster Template",
        analytics: "teamwear-roster-packing-template",
      }
    : /yoga|pilates|activewear|sports-bras|leggings|gym|training|athleisure|seamless|plus-size|compression/.test(productSlug)
      ? {
          href: "../assets/downloads/private-label-activewear-collection-planner.csv",
          name: "Collection Planner",
          analytics: "private-label-activewear-collection-planner",
        }
      : {
          href: "../assets/downloads/sportswear-collection-development-brief.csv",
          name: "Product Brief CSV",
          analytics: "sportswear-collection-development-brief",
        };

  const section = document.createElement("section");
  const headingId = `product-detail-explorer-${productSlug}`;
  const stageId = `product-detail-stage-${productSlug}`;
  section.className = "section product-detail-explorer";
  section.dataset.productDetailExplorer = "";
  section.setAttribute("aria-labelledby", headingId);
  section.innerHTML = `
    <div class="product-detail-explorer-layout">
      <div class="product-detail-gallery">
        <div class="product-detail-stage" id="${stageId}" role="tabpanel" tabindex="0">
          <div class="product-detail-stage-media" data-product-detail-stage-media></div>
          <div class="product-detail-stage-caption" role="status" aria-live="polite">
            <span>Selected planning reference</span>
            <strong data-product-detail-stage-title></strong>
            <p data-product-detail-stage-description></p>
          </div>
        </div>
        <div class="product-detail-thumbnails" role="tablist" aria-label="Choose an illustrative product-planning reference" data-product-detail-thumbnails></div>
        <div class="product-detail-evidence-checklist">
          <div class="product-detail-evidence-heading">
            <div><span>Real style-specific detail pack</span><strong>Five evidence views to request before approval</strong></div>
            <a href="./lookbook.html#illustrative-detail-board-heading">See the five-view submission standard</a>
          </div>
          <div class="product-detail-evidence-slots">
            ${evidenceSlotLabels.map((label, index) => `
              <div>
                <span>${String(index + 1).padStart(2, "0")}</span>
                <strong>${label}</strong>
                <small>Real style-specific image not yet provided in a controlled evidence record.</small>
              </div>
            `).join("")}
          </div>
        </div>
        <p class="product-detail-disclosure"><strong>Illustrative product-planning references:</strong> Unless a view is separately marked with a verified evidence record, treat every image in this explorer as illustrative—not a photograph of available stock, current production, a customer order, or an approved product specification. Confirm the actual sample, material, construction, color, decoration, and packaging for your project.</p>
      </div>
      <div class="product-detail-summary">
        <p class="eyebrow">Interactive product details</p>
        <h2 id="${headingId}"></h2>
        <p class="product-detail-intro"></p>
        <div class="product-detail-facts" aria-label="Product detail overview">
          <div><span>Visual references</span><strong>${visibleMediaItems.length}</strong></div>
          <div><span>Product directions</span><strong>${skuCards.length}</strong></div>
          <div><span>Bulk release</span><strong>Sample approval</strong></div>
        </div>
        <div class="product-detail-groups" data-product-detail-groups></div>
        <div class="product-detail-buyer-route">
          <strong>Who is buying this product?</strong>
          <nav aria-label="Choose a buyer route for this product">
            <a href="../contact.html?buyer=startup_brand#quote-form" data-product-buyer-route="startup_brand">Startup</a>
            <a href="../contact.html?buyer=established_brand#quote-form" data-product-buyer-route="established_brand">Established brand</a>
            <a href="../contact.html?buyer=dealer_distributor#quote-form" data-product-buyer-route="dealer_distributor">Distributor</a>
            <a href="../contact.html?buyer=club_school_team#quote-form" data-product-buyer-route="club_school_team">Club or school</a>
          </nav>
        </div>
        <div class="product-detail-actions">
          <a class="button primary" href="../contact.html#quote-form"><i data-lucide="send"></i>Request Details &amp; Quote</a>
          <a class="button secondary" href="../fabrics.html"><i data-lucide="swatch-book"></i>Compare Fabrics</a>
          <a class="button secondary" href="${planningResource.href}" download data-resource-download="${planningResource.analytics}"><i data-lucide="download"></i>${planningResource.name}</a>
          <button class="button secondary product-shortlist-toggle" type="button" aria-pressed="false" data-product-shortlist-toggle><i data-lucide="bookmark-plus"></i><span>Add to Shortlist</span></button>
        </div>
        <div class="product-detail-shortlist" data-product-shortlist-panel>
          <div class="product-shortlist-heading"><div><span>Multi-product brief</span><strong>Project shortlist</strong></div><small data-product-shortlist-count>0 of 4 saved</small></div>
          <p>Save up to four product directions, compare them while browsing, and carry the list into one structured inquiry.</p>
          <div class="product-shortlist-items" data-product-shortlist-items></div>
          <div class="product-shortlist-footer"><span data-product-shortlist-note role="status" aria-live="polite">Saved only in this browser tab for the current inquiry.</span><a href="../contact.html#quote-form" data-product-shortlist-quote hidden>Build a Multi-Product Brief <span aria-hidden="true">→</span></a></div>
        </div>
        <small class="product-detail-boundary">MOQ, sample cost, lead time, material availability, construction, decoration, testing, and reorder conditions are confirmed against the exact brief.</small>
      </div>
    </div>
  `;

  section.querySelector("h2").textContent = `${productName}: planning references, options, and specification points`;
  section.querySelector(".product-detail-intro").textContent = productSummary;
  hero.insertAdjacentElement("afterend", section);
  document.documentElement.classList.add("has-product-detail-explorer");

  const shortlistToggle = section.querySelector("[data-product-shortlist-toggle]");
  const shortlistToggleLabel = shortlistToggle?.querySelector("span");
  const shortlistCount = section.querySelector("[data-product-shortlist-count]");
  const shortlistItems = section.querySelector("[data-product-shortlist-items]");
  const shortlistNote = section.querySelector("[data-product-shortlist-note]");
  const shortlistQuote = section.querySelector("[data-product-shortlist-quote]");
  const currentShortlistItem = {
    slug: productSlug,
    label: productName.replace(/[\r\n\t]/g, " ").trim().slice(0, 100),
    path: window.location.pathname,
  };
  let productShortlist = readStoredProductShortlist();

  const renderProductShortlist = (message = "") => {
    const currentIsSelected = productShortlist.some((item) => item.slug === productSlug);
    const shortlistIsFull = productShortlist.length >= 4;
    if (shortlistToggle) {
      shortlistToggle.setAttribute("aria-pressed", String(currentIsSelected));
      shortlistToggle.classList.toggle("is-selected", currentIsSelected);
      shortlistToggle.disabled = shortlistIsFull && !currentIsSelected;
    }
    if (shortlistToggleLabel) {
      shortlistToggleLabel.textContent = currentIsSelected
        ? "Remove from Shortlist"
        : shortlistIsFull
          ? "Shortlist Full"
          : "Add to Shortlist";
    }
    if (shortlistCount) shortlistCount.textContent = `${productShortlist.length} of 4 saved`;
    if (shortlistQuote) shortlistQuote.hidden = productShortlist.length === 0;
    if (shortlistNote) {
      shortlistNote.textContent = message || (shortlistIsFull && !currentIsSelected
        ? "Four directions saved. Remove one before adding this product."
        : "Saved only in this browser tab for the current inquiry.");
    }
    if (!shortlistItems) return;
    shortlistItems.replaceChildren();
    if (!productShortlist.length) {
      const emptyState = document.createElement("span");
      emptyState.className = "product-shortlist-empty";
      emptyState.textContent = "No product directions saved yet.";
      shortlistItems.append(emptyState);
      return;
    }
    productShortlist.forEach((item) => {
      const row = document.createElement("div");
      row.className = "product-shortlist-item";
      const link = document.createElement("a");
      link.href = item.path;
      link.textContent = item.label;
      if (item.slug === productSlug) link.setAttribute("aria-current", "page");
      const removeButton = document.createElement("button");
      removeButton.type = "button";
      removeButton.textContent = "×";
      removeButton.setAttribute("aria-label", `Remove ${item.label} from the project shortlist`);
      removeButton.addEventListener("click", () => {
        productShortlist = productShortlist.filter((candidate) => candidate.slug !== item.slug);
        saveStoredProductShortlist(productShortlist);
        renderProductShortlist(`${item.label} removed from the project shortlist.`);
        trackEvent("product_shortlist_update", {
          action: "remove",
          product_slug: item.slug,
          selected_count: productShortlist.length,
        });
      });
      row.append(link, removeButton);
      shortlistItems.append(row);
    });
  };

  shortlistToggle?.addEventListener("click", () => {
    const currentIsSelected = productShortlist.some((item) => item.slug === productSlug);
    if (!currentIsSelected && productShortlist.length >= 4) {
      renderProductShortlist("Four directions are already saved. Remove one before adding this product.");
      return;
    }
    if (currentIsSelected) {
      productShortlist = productShortlist.filter((item) => item.slug !== productSlug);
    } else if (productShortlist.length < 4) {
      productShortlist.push(currentShortlistItem);
    }
    saveStoredProductShortlist(productShortlist);
    renderProductShortlist(`${currentShortlistItem.label} ${currentIsSelected ? "removed from" : "added to"} the project shortlist.`);
    trackEvent("product_shortlist_update", {
      action: currentIsSelected ? "remove" : "add",
      product_slug: productSlug,
      selected_count: productShortlist.length,
    });
  });

  shortlistQuote?.addEventListener("click", () => {
    trackEvent("product_shortlist_quote", {
      selected_count: productShortlist.length,
      product_slugs: productShortlist.map((item) => item.slug).join("|").slice(0, 240),
    });
  });

  renderProductShortlist();

  section.querySelectorAll("[data-product-buyer-route]").forEach((link) => {
    link.addEventListener("click", () => {
      trackEvent("product_buyer_route_select", {
        product_slug: productSlug,
        buyer_path: link.dataset.productBuyerRoute || "unknown",
      });
    });
  });

  const detailGroups = section.querySelector("[data-product-detail-groups]");
  const createDetailGroup = (title, items, isOpen = false) => {
    const details = document.createElement("details");
    details.className = "product-detail-group";
    details.open = isOpen;
    const summary = document.createElement("summary");
    summary.textContent = title;
    const list = document.createElement("ul");
    items.forEach(({ label, text: itemText }) => {
      const item = document.createElement("li");
      const itemLabel = document.createElement("strong");
      const itemDescription = document.createElement("span");
      itemLabel.textContent = label;
      itemDescription.textContent = itemText;
      item.append(itemLabel, itemDescription);
      list.append(item);
    });
    details.append(summary, list);
    details.addEventListener("toggle", () => {
      if (!details.open) return;
      trackEvent("product_detail_section_open", {
        product_slug: productSlug,
        detail_section: title.toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_|_$/g, ""),
      });
    });
    detailGroups.append(details);
  };

  const productOptions = skuCards.slice(0, 6).map((card, index) => ({
    label: card.querySelector("h3")?.textContent.trim() || `Product direction ${index + 1}`,
    text: [...card.querySelectorAll("li")]
      .slice(0, 3)
      .map((item) => item.textContent.trim())
      .join(" · ") || "Confirm the selected style, fit, size range, and intended use before sampling.",
  }));
  createDetailGroup("Product styles and options", productOptions, true);

  const systemCards = [...document.querySelectorAll(".product-system-grid article")];
  const systemDetails = systemCards.length
    ? systemCards.slice(0, 6).map((card) => ({
        label: [card.querySelector("span")?.textContent.trim(), card.querySelector("h3")?.textContent.trim()].filter(Boolean).join(" — "),
        text: card.querySelector("p")?.textContent.trim() || "Confirm this requirement in the approved specification.",
      }))
    : [
        { label: "Material", text: "Confirm composition, weight, handfeel, stretch, recovery, color reference, and availability." },
        { label: "Fit and construction", text: "Confirm measurements, tolerances, panel lines, seam type, reinforcement, and size grading." },
        { label: "Branding", text: "Confirm artwork, dimensions, placement anchors, decoration method, color, and durability checks." },
      ];
  createDetailGroup("Materials, construction, and branding", systemDetails);
  createDetailGroup("What to confirm before quotation", [
    { label: "Product definition", text: "Reference style or tech pack, front and back requirements, size range, fit direction, and intended use." },
    { label: "Order scope", text: "Quantity by style and color, target market, sample need, delivery country, and timing target." },
    { label: "Material and color", text: "Composition, weight, performance target, handfeel, color standard, and acceptable substitutions." },
    { label: "Decoration and packaging", text: "Logo files, dimensions, placement, labels, hangtags, polybags, barcodes, and carton sorting." },
    { label: "Approval control", text: "Sample ID, revision, measurement record, artwork approval, packaging approval, and written bulk release." },
  ]);

  const stage = section.querySelector(".product-detail-stage");
  const stageMedia = section.querySelector("[data-product-detail-stage-media]");
  const stageTitle = section.querySelector("[data-product-detail-stage-title]");
  const stageDescription = section.querySelector("[data-product-detail-stage-description]");
  const thumbnailList = section.querySelector("[data-product-detail-thumbnails]");
  const thumbnailButtons = [];
  let activeMediaIndex = 0;

  const preparePicture = (picture, sizes, loading) => {
    const clone = picture.cloneNode(true);
    clone.querySelectorAll("source").forEach((source) => source.setAttribute("sizes", sizes));
    const image = clone.querySelector("img");
    if (image) {
      image.setAttribute("sizes", sizes);
      image.setAttribute("loading", loading);
      image.setAttribute("decoding", "async");
      image.removeAttribute("fetchpriority");
    }
    return clone;
  };

  const showMediaItem = (index, userInitiated = false) => {
    const item = visibleMediaItems[index];
    if (!item) return;
    activeMediaIndex = index;
    stageMedia.replaceChildren(preparePicture(item.picture, "(max-width: 1040px) calc(100vw - 40px), 54vw", userInitiated ? "eager" : "lazy"));
    stageTitle.textContent = item.title;
    stageDescription.textContent = item.description;
    thumbnailButtons.forEach((button, buttonIndex) => {
      const isSelected = buttonIndex === index;
      button.setAttribute("aria-selected", String(isSelected));
      button.tabIndex = isSelected ? 0 : -1;
    });
    stage.setAttribute("aria-labelledby", thumbnailButtons[index]?.id || "");
    if (userInitiated) {
      trackEvent("product_detail_image_select", {
        product_slug: productSlug,
        image_position: index + 1,
        image_label: item.title.slice(0, 80),
      });
    }
  };

  visibleMediaItems.forEach((item, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.id = `product-detail-tab-${productSlug}-${index + 1}`;
    button.setAttribute("role", "tab");
    button.setAttribute("aria-controls", stageId);
    button.setAttribute("aria-label", `Show ${item.title}`);
    const position = document.createElement("span");
    position.className = "product-detail-thumbnail-position";
    position.textContent = String(index + 1).padStart(2, "0");
    const label = document.createElement("span");
    label.className = "product-detail-thumbnail-label";
    label.textContent = item.title;
    const status = document.createElement("small");
    status.textContent = "Illustrative reference";
    button.append(position, label, status);
    button.addEventListener("click", () => showMediaItem(index, true));
    thumbnailButtons.push(button);
    thumbnailList.append(button);
  });

  thumbnailList.addEventListener("keydown", (event) => {
    if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
    event.preventDefault();
    const activeIndex = Math.max(0, thumbnailButtons.findIndex((button) => button.getAttribute("aria-selected") === "true"));
    const nextIndex = event.key === "Home"
      ? 0
      : event.key === "End"
        ? thumbnailButtons.length - 1
        : event.key === "ArrowRight"
          ? (activeIndex + 1) % thumbnailButtons.length
          : (activeIndex - 1 + thumbnailButtons.length) % thumbnailButtons.length;
    showMediaItem(nextIndex, true);
    thumbnailButtons[nextIndex].focus();
  });

  section.querySelector(".product-detail-actions .primary")?.addEventListener("click", () => {
    const selectedReference = visibleMediaItems[activeMediaIndex]?.title || productName;
    try {
      sessionStorage.setItem(productDirectionStorageKey, JSON.stringify({
        label: selectedReference,
        sourcePath: window.location.pathname,
        savedAt: Date.now(),
      }));
    } catch {
      // The quote link still works when storage is unavailable.
    }
    trackEvent("product_detail_quote_select", {
      product_slug: productSlug,
      selected_reference: selectedReference.slice(0, 80),
    });
  });

  showMediaItem(0);
  trackEvent("product_detail_view", {
    product_slug: productSlug,
    visual_reference_count: visibleMediaItems.length,
    product_direction_count: skuCards.length,
  });
};

setupProductDetailExplorer();

const fabricLibrary = document.querySelector("[data-fabric-library]");
if (fabricLibrary) {
  const filterButtons = [...fabricLibrary.querySelectorAll("[data-fabric-filter]")];
  const fabricCards = [...fabricLibrary.querySelectorAll("[data-fabric-groups]")];
  const status = fabricLibrary.querySelector("[data-fabric-filter-status]");
  const searchInput = fabricLibrary.querySelector("[data-fabric-search]");
  const structureSelect = fabricLibrary.querySelector("[data-fabric-structure]");
  const decorationSelect = fabricLibrary.querySelector("[data-fabric-decoration]");
  const resetButton = fabricLibrary.querySelector("[data-fabric-reset]");
  const shortlistInputs = [...fabricLibrary.querySelectorAll("[data-fabric-shortlist]")];
  const shortlistItems = fabricLibrary.querySelector("[data-fabric-shortlist-items]");
  const shortlistLimit = fabricLibrary.querySelector("[data-fabric-shortlist-limit]");
  const shortlistCopy = fabricLibrary.querySelector("[data-fabric-shortlist-copy]");
  const shortlistQuote = fabricLibrary.querySelector("[data-fabric-shortlist-quote]");
  const shortlistNote = fabricLibrary.querySelector("[data-fabric-shortlist-note]");
  let activeGroup = "all";

  fabricCards.forEach((card) => {
    card.dataset.fabricText = [
      card.dataset.fabricSearch || "",
      card.textContent || "",
    ].join(" ").toLowerCase();
  });

  const applyFabricFilters = (shouldTrack = false) => {
    const searchTerm = searchInput?.value.trim().toLowerCase() || "";
    const structure = structureSelect?.value || "all";
    const decoration = decorationSelect?.value || "all";
    let visibleCount = 0;

    fabricCards.forEach((card) => {
      const groups = (card.dataset.fabricGroups || "").split(/\s+/);
      const structures = (card.dataset.fabricStructures || "").split(/\s+/);
      const decorations = (card.dataset.fabricDecorations || "").split(/\s+/);
      const matchesGroup = activeGroup === "all" || groups.includes(activeGroup);
      const matchesStructure = structure === "all" || structures.includes(structure);
      const matchesDecoration = decoration === "all" || decorations.includes(decoration);
      const matchesSearch = !searchTerm || card.dataset.fabricText.includes(searchTerm);
      const isVisible = matchesGroup && matchesStructure && matchesDecoration && matchesSearch;
      card.hidden = !isVisible;
      if (isVisible) visibleCount += 1;
    });

    if (status) {
      status.textContent = visibleCount === fabricCards.length
        ? `Showing all ${fabricCards.length} planning directions.`
        : `Showing ${visibleCount} of ${fabricCards.length} planning directions.`;
    }
    if (shouldTrack) {
      trackEvent("fabric_library_filter", {
        product_group: activeGroup,
        construction: structure,
        decoration,
        has_search: Boolean(searchTerm),
        result_count: visibleCount,
      });
    }
  };

  filterButtons.forEach((button) => {
    button.addEventListener("click", () => {
      activeGroup = button.dataset.fabricFilter || "all";
      filterButtons.forEach((item) => {
        const isActive = item === button;
        item.classList.toggle("is-active", isActive);
        item.setAttribute("aria-pressed", String(isActive));
      });
      applyFabricFilters(true);
    });
  });

  searchInput?.addEventListener("input", () => applyFabricFilters());
  searchInput?.addEventListener("change", () => applyFabricFilters(true));
  structureSelect?.addEventListener("change", () => applyFabricFilters(true));
  decorationSelect?.addEventListener("change", () => applyFabricFilters(true));
  resetButton?.addEventListener("click", () => {
    activeGroup = "all";
    if (searchInput) searchInput.value = "";
    if (structureSelect) structureSelect.value = "all";
    if (decorationSelect) decorationSelect.value = "all";
    filterButtons.forEach((button) => {
      const isActive = button.dataset.fabricFilter === "all";
      button.classList.toggle("is-active", isActive);
      button.setAttribute("aria-pressed", String(isActive));
    });
    applyFabricFilters(true);
    searchInput?.focus();
  });

  const getSelectedFabricDirections = () => shortlistInputs
    .filter((input) => input.checked)
    .map((input) => {
      const card = input.closest("[data-fabric-id]");
      return {
        id: card?.dataset.fabricId || input.value,
        name: card?.querySelector("h3")?.textContent.trim() || "Material direction",
      };
    });

  const saveFabricShortlist = (items) => {
    try {
      if (items.length) {
        sessionStorage.setItem(fabricShortlistStorageKey, JSON.stringify({ items, savedAt: Date.now() }));
      } else {
        sessionStorage.removeItem(fabricShortlistStorageKey);
      }
    } catch {
      // The visible shortlist still works when storage is unavailable.
    }
  };

  const updateFabricShortlist = (message = "") => {
    const selected = getSelectedFabricDirections();
    const reachedLimit = selected.length >= 4;
    shortlistInputs.forEach((input) => {
      input.disabled = reachedLimit && !input.checked;
    });
    if (shortlistItems) {
      shortlistItems.replaceChildren();
      if (!selected.length) {
        const emptyItem = document.createElement("li");
        emptyItem.textContent = "No material directions selected yet.";
        shortlistItems.append(emptyItem);
      } else {
        selected.forEach((item) => {
          const listItem = document.createElement("li");
          const itemLabel = document.createElement("span");
          itemLabel.textContent = `${item.id} — ${item.name}`;
          const removeButton = document.createElement("button");
          removeButton.type = "button";
          removeButton.className = "fabric-shortlist-remove";
          removeButton.dataset.fabricShortlistRemove = item.id;
          removeButton.textContent = "Remove";
          removeButton.setAttribute("aria-label", `Remove ${item.id} — ${item.name} from shortlist`);
          listItem.append(itemLabel, removeButton);
          shortlistItems.append(listItem);
        });
      }
    }
    if (shortlistLimit) shortlistLimit.textContent = `${selected.length} of 4 selected`;
    if (shortlistCopy) shortlistCopy.disabled = selected.length === 0;
    if (shortlistNote) {
      shortlistNote.textContent = message || (selected.length
        ? "Shortlist saved for this browser session and ready to carry into the quote form."
        : "Choose one to four directions to create a fabric brief.");
    }
    saveFabricShortlist(selected);
    return selected;
  };

  shortlistItems?.addEventListener("click", (event) => {
    if (!(event.target instanceof Element)) return;
    const removeButton = event.target.closest("[data-fabric-shortlist-remove]");
    if (!removeButton || !shortlistItems.contains(removeButton)) return;

    const removeButtons = [...shortlistItems.querySelectorAll("[data-fabric-shortlist-remove]")];
    const removeIndex = removeButtons.indexOf(removeButton);
    const fabricId = removeButton.dataset.fabricShortlistRemove || "";
    const input = shortlistInputs.find((candidate) => {
      const candidateId = candidate.closest("[data-fabric-id]")?.dataset.fabricId || candidate.value;
      return candidateId === fabricId;
    });
    if (!input) return;

    input.checked = false;
    const selected = updateFabricShortlist(`${fabricId} removed. You can now add another material direction.`);
    const nextRemoveButtons = [...shortlistItems.querySelectorAll("[data-fabric-shortlist-remove]")];
    const nextFocusTarget = nextRemoveButtons[removeIndex]
      || nextRemoveButtons[nextRemoveButtons.length - 1]
      || shortlistCopy
      || shortlistQuote;
    nextFocusTarget?.focus();
    trackEvent("fabric_shortlist_update", { selected_count: selected.length });
  });

  const restoredShortlistIds = new Set(readStoredFabricShortlist().map((item) => item.id));
  shortlistInputs.forEach((input) => {
    const cardId = input.closest("[data-fabric-id]")?.dataset.fabricId || input.value;
    input.checked = restoredShortlistIds.has(cardId);
    input.addEventListener("change", () => {
      const beforeUpdate = getSelectedFabricDirections();
      if (beforeUpdate.length > 4) {
        input.checked = false;
        updateFabricShortlist("Choose no more than four material directions for one comparison brief.");
        return;
      }
      const selected = updateFabricShortlist();
      trackEvent("fabric_shortlist_update", { selected_count: selected.length });
    });
  });

  shortlistCopy?.addEventListener("click", async () => {
    const selected = getSelectedFabricDirections();
    if (!selected.length) return;
    const text = [
      "GloryStarWear fabric planning shortlist",
      "",
      ...selected.map((item) => `${item.id} — ${item.name}`),
      "",
      "Please confirm the exact supplier code, composition, construction, finished GSM, stretch, finish, color, decoration compatibility, MOQ, testing, availability, and physical sample for this project.",
    ].join("\n");
    shortlistCopy.disabled = true;
    try {
      if (!(await copyText(text))) throw new Error("copy_unavailable");
      if (shortlistNote) shortlistNote.textContent = "Fabric shortlist copied. Add your product, quantity, market, and color requirements before sending.";
      trackEvent("fabric_shortlist_copy", { selected_count: selected.length });
    } catch {
      if (shortlistNote) shortlistNote.textContent = "Copying is unavailable in this browser. Use Request Coded Swatches to carry the shortlist into the quote form.";
    } finally {
      shortlistCopy.disabled = false;
    }
  });

  shortlistQuote?.addEventListener("click", () => {
    const selected = updateFabricShortlist();
    trackEvent("fabric_shortlist_quote", { selected_count: selected.length });
  });

  updateFabricShortlist();
  applyFabricFilters();
}

if (catalogGrid) {
  const catalogCards = [...catalogGrid.querySelectorAll(".product-card")];
  const searchInput = document.querySelector("[data-catalog-search]");
  const clearSearchButton = document.querySelector("[data-catalog-clear]");
  const resetButton = document.querySelector("[data-catalog-reset]");
  const resultStatus = document.querySelector("[data-catalog-results]");
  const emptyState = document.querySelector("[data-catalog-empty]");
  const filterButtons = [...document.querySelectorAll("[data-catalog-filter]")];
  const catalogGroups = {
    activewear: new Set([
      "yoga-wear", "yoga-leggings", "sports-bras", "seamless-activewear", "plus-size-activewear",
      "athleisure", "hoodies-sweatshirts", "joggers-tracksuits", "training-wear",
      "gym-tshirts-tank-tops", "training-shorts-joggers", "private-label-gym-clothing",
      "compression-base-layers", "pilates-activewear", "private-label-gym-leggings",
    ]),
    teamwear: new Set([
      "basketball-wear", "basketball-jerseys", "football-kits", "football-jerseys",
      "custom-sublimated-teamwear", "volleyball-teamwear", "volleyball-uniforms",
      "team-warm-up-jackets", "baseball-softball-teamwear", "rugby-hockey-teamwear",
      "youth-sportswear", "club-fan-merchandise", "club-hoodies-varsity-jackets", "soccer-uniforms",
      "esports-jerseys", "cheerleading-uniforms", "track-field-uniforms", "lacrosse-uniforms",
      "wrestling-singlets", "gymnastics-leotards", "cricket-uniforms", "american-football-uniforms",
      "netball-uniforms", "ice-hockey-jerseys",
      "flag-football-uniforms", "baseball-uniforms", "softball-uniforms",
      "rugby-uniforms", "field-hockey-uniforms", "custom-handball-uniforms",
      "custom-futsal-uniforms", "custom-bowling-shirts", "custom-darts-shirts",
      "custom-ultimate-jerseys", "custom-team-polo-shirts",
      "custom-beach-volleyball-uniforms", "custom-referee-uniforms",
    ]),
    specialty: new Set([
      "running-wear", "running-singlets-shirts", "tennis-pickleball-apparel", "cycling-wear",
      "cycling-jerseys-bib-shorts", "outdoor-training-outerwear", "golf-apparel",
      "golf-polo-shirts-skorts", "swimwear-water-sports", "rash-guards-board-shorts",
      "combat-sports-apparel", "mma-rash-guards-fight-shorts", "racket-sports-apparel",
      "dancewear-cheer", "trail-hiking-apparel", "winter-sports-apparel",
      "triathlon-endurance-apparel", "marathon-event-apparel",
      "custom-fishing-apparel", "custom-rowing-uniforms", "custom-running-shorts",
      "custom-boxing-apparel", "custom-padel-apparel", "badminton-uniforms",
      "custom-table-tennis-uniforms", "custom-weightlifting-singlets",
      "custom-cycling-skinsuits", "custom-triathlon-suits", "custom-motocross-jerseys",
    ]),
    accessories: new Set([
      "accessories", "custom-sports-socks", "custom-sports-caps-bags",
      "private-label-sportswear-packaging",
    ]),
  };
  let activeFilter = "all";

  const getCardCategory = (slug) => {
    const group = Object.entries(catalogGroups).find(([, slugs]) => slugs.has(slug));
    return group?.[0] || "discovery";
  };

  catalogCards.forEach((card) => {
    const cardLink = card.querySelector(".product-card-link");
    const href = cardLink?.getAttribute("href") || "";
    const slug = href.split("/").pop()?.replace(/\.html$/, "") || "";
    card.dataset.catalogCategory = getCardCategory(slug);
    card.dataset.catalogText = card.textContent.toLowerCase();
    const cardContent = card.querySelector("div");
    if (cardContent && !cardContent.querySelector(".product-card-detail-cue")) {
      const detailCue = document.createElement("span");
      detailCue.className = "product-card-detail-cue";
      detailCue.textContent = "Explore product direction";
      cardContent.append(detailCue);
    }
    cardLink?.addEventListener("click", () => {
      trackEvent("product_card_open", {
        product_slug: slug,
        catalog_category: card.dataset.catalogCategory,
      });
    });
  });

  const applyCatalogFilters = () => {
    const query = searchInput?.value.trim().toLowerCase() || "";
    let visibleCount = 0;

    catalogCards.forEach((card) => {
      const matchesFilter = activeFilter === "all" || card.dataset.catalogCategory === activeFilter;
      const matchesSearch = !query || card.dataset.catalogText.includes(query);
      const isVisible = matchesFilter && matchesSearch;
      card.hidden = !isVisible;
      if (isVisible) visibleCount += 1;
    });

    if (clearSearchButton) {
      clearSearchButton.hidden = !query;
    }
    if (resultStatus) {
      resultStatus.textContent = visibleCount === catalogCards.length
        ? `Showing all ${catalogCards.length} categories`
        : `Showing ${visibleCount} of ${catalogCards.length} categories`;
    }
    if (emptyState) {
      emptyState.hidden = visibleCount !== 0;
    }
  };

  const setCatalogFilter = (filter) => {
    activeFilter = filter;
    filterButtons.forEach((button) => {
      button.setAttribute("aria-pressed", String(button.dataset.catalogFilter === activeFilter));
    });
    applyCatalogFilters();
  };

  const resetCatalog = () => {
    if (searchInput) searchInput.value = "";
    setCatalogFilter("all");
    searchInput?.focus();
  };

  filterButtons.forEach((button) => {
    button.setAttribute("aria-controls", catalogGrid.id);
    button.addEventListener("click", () => {
      setCatalogFilter(button.dataset.catalogFilter);
      trackEvent("catalog_filter", { catalog_filter: button.dataset.catalogFilter });
    });
  });

  searchInput?.addEventListener("input", applyCatalogFilters);
  searchInput?.addEventListener("change", () => {
    const searchTerm = searchInput.value.trim();
    if (searchTerm) {
      trackEvent("catalog_search", { search_term: searchTerm.slice(0, 80) });
    }
  });
  searchInput?.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && searchInput.value.trim()) {
      trackEvent("catalog_search", { search_term: searchInput.value.trim().slice(0, 80) });
    }
    if (event.key === "Escape" && searchInput.value) {
      searchInput.value = "";
      applyCatalogFilters();
    }
  });
  clearSearchButton?.addEventListener("click", () => {
    searchInput.value = "";
    applyCatalogFilters();
    searchInput.focus();
  });
  resetButton?.addEventListener("click", resetCatalog);
  applyCatalogFilters();
}

const renderIcons = () => {
  window.lucide?.createIcons();
};

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", renderIcons, { once: true });
} else {
  renderIcons();
}
