const header = document.querySelector("[data-header]");
const menuToggle = document.querySelector("[data-menu-toggle]");
const mobileNav = document.querySelector("[data-mobile-nav]");
const quoteForms = document.querySelectorAll("[data-quote-form]");
const catalogGrid = document.querySelector("[data-catalog-grid]");
const whatsappNumber = "8618020755949";
const isContactPage = window.location.pathname.endsWith("/contact.html");
const inquirySourceKey = "glorystarwear-inquiry-source";
const attributionStorageKey = "glorystarwear-attribution";
const campaignParameterNames = [
  "utm_source",
  "utm_medium",
  "utm_campaign",
  "utm_term",
  "utm_content",
  "gclid",
  "msclkid",
];

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

window.dataLayer = window.dataLayer || [];
const trackEvent = (eventName, details = {}) => {
  window.dataLayer.push({
    event: eventName,
    page_path: window.location.pathname,
    ...details,
  });
};

if (isNewAttributionSession) {
  trackEvent("session_landing", {
    campaign_source: pageAttribution.campaign.utm_source || "",
    campaign_medium: pageAttribution.campaign.utm_medium || "",
    campaign_name: pageAttribution.campaign.utm_campaign || "",
  });
}

document.documentElement.classList.add("has-enhanced-contact");
if (catalogGrid) {
  document.documentElement.classList.add("has-enhanced-catalog");
}

const syncHeader = () => {
  header?.classList.toggle("is-scrolled", window.scrollY > 24);
};

window.addEventListener("scroll", syncHeader, { passive: true });
syncHeader();

menuToggle?.setAttribute("aria-expanded", "false");
if (mobileNav && !mobileNav.id) {
  mobileNav.id = "mobile-navigation";
}
if (mobileNav?.id) {
  menuToggle?.setAttribute("aria-controls", mobileNav.id);
}
mobileNav?.setAttribute("aria-hidden", "true");

const contactUrl = isContactPage ? "#quote-form" : new URL("/contact.html", window.location.href).href;
const defaultWhatsAppText = encodeURIComponent(
  "Hi GloryStarWear, I want to start a custom sportswear project.",
);

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
  const bar = document.createElement("div");
  bar.className = "mobile-quote-bar";
  bar.setAttribute("data-mobile-quote-bar", "");
  bar.innerHTML = `
    <a href="${contactUrl}"><i data-lucide="send"></i><span>Get Quote</span></a>
    <a href="https://wa.me/${whatsappNumber}?text=${defaultWhatsAppText}" target="_blank" rel="noreferrer"><i data-lucide="message-circle"></i><span>WhatsApp</span></a>
  `;
  document.body.append(bar);
}

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

  try {
    const target = new URL(link.href, window.location.href);
    const contactMethod = target.protocol === "mailto:"
      ? "email"
      : target.hostname === "wa.me"
        ? "whatsapp"
        : target.pathname.endsWith("/contact.html") || target.hash === "#quote-form"
          ? "quote_page"
          : "";

    if (contactMethod) {
      trackEvent("contact_click", {
        contact_method: contactMethod,
        link_text: link.textContent.trim().slice(0, 80),
      });
    }

    if (link.dataset.resourceDownload) {
      trackEvent("resource_download", {
        resource_name: link.dataset.resourceDownload.slice(0, 80),
        file_name: target.pathname.split("/").pop()?.slice(0, 120) || "",
      });
    }

    if (!isContactPage && target.pathname.endsWith("/contact.html")) {
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

const getProductInterestForPath = (path) => {
  const routes = [
    ["Yoga wear", /yoga|sports-bras|seamless-activewear|plus-size-activewear/],
    ["Athleisure", /athleisure|hoodies-sweatshirts|joggers-tracksuits|club-hoodies/],
    ["Training wear", /training-wear|gym-tshirts|training-shorts|private-label-gym|compression-base|outdoor-training/],
    ["Basketball wear", /basketball/],
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

if (inquiryContext && storedInquirySource) {
  const contextTitle = inquiryContext.querySelector("[data-inquiry-context-title]");
  const productSelect = document.querySelector('[data-quote-form] select[name="product"]');
  const suggestedProduct = getProductInterestForPath(storedInquirySource.path);

  if (contextTitle) {
    contextTitle.textContent = getShortPageTitle(storedInquirySource.title);
  }
  inquiryContext.hidden = false;

  if (productSelect && !productSelect.value && suggestedProduct) {
    productSelect.value = suggestedProduct;
    productSelect.dataset.sourcePrefilled = suggestedProduct;
  }

  inquiryContext.querySelector("[data-inquiry-context-clear]")?.addEventListener("click", () => {
    try {
      sessionStorage.removeItem(inquirySourceKey);
    } catch {
      // The visual context can still be dismissed when storage is unavailable.
    }
    inquiryContext.hidden = true;
    if (productSelect?.value === productSelect?.dataset.sourcePrefilled) {
      productSelect.value = "";
    }
    if (productSelect) {
      delete productSelect.dataset.sourcePrefilled;
    }
  });
}

const getInquiryLines = (form) => {
  const data = new FormData(form);
  const attribution = readAttribution() || pageAttribution;
  const campaign = Object.entries(attribution?.campaign || {})
    .map(([name, value]) => `${name}=${value}`)
    .join(" | ");
  const attributionLines = [
    campaign ? `Campaign: ${campaign}` : "",
    attribution?.landingPage ? `Landing Page: ${attribution.landingPage}` : "",
    attribution?.referrer ? `Referrer: ${attribution.referrer}` : "",
  ].filter(Boolean);

  return [
    `Name: ${data.get("name")}`,
    `Email: ${data.get("email")}`,
    `WhatsApp or Phone: ${data.get("phone") || "Not provided"}`,
    `Product Interest: ${data.get("product")}`,
    `Estimated Quantity: ${data.get("quantity") || "Not provided"}`,
    `Target Market: ${data.get("market") || "Not provided"}`,
    `Expected Timeline: ${data.get("timeline") || "Not provided"}`,
    `Source Page: ${getInquirySource()}`,
    ...attributionLines,
    "",
    "Project Details:",
    data.get("message"),
  ];
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

quoteForms.forEach((form) => {
  let hasStartedQuote = false;
  const trackQuoteStart = () => {
    if (hasStartedQuote) return;
    hasStartedQuote = true;
    trackEvent("quote_start", { form_location: window.location.pathname });
  };

  form.addEventListener("input", trackQuoteStart);
  form.addEventListener("focusin", trackQuoteStart);

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const data = new FormData(form);
    const subject = encodeURIComponent(`GloryStarWear inquiry - ${data.get("product")}`);
    const body = encodeURIComponent(getInquiryLines(form).join("\n"));

    setFormNote(form, "Opening your email app with the project brief...", "opening");
    trackEvent("quote_submit_email", { product_interest: data.get("product") || "" });
    window.location.href = `mailto:kevin@glorystarwears.com?subject=${subject}&body=${body}`;
  });

  form.querySelector("[data-whatsapp-inquiry]")?.addEventListener("click", () => {
    if (!form.reportValidity()) return;

    const text = encodeURIComponent(
      ["Hi GloryStarWear, I want to start a custom sportswear project.", "", ...getInquiryLines(form)].join(
        "\n",
      ),
    );
    setFormNote(form, "Opening WhatsApp with the project brief...", "opening");
    trackEvent("quote_submit_whatsapp", {
      product_interest: new FormData(form).get("product") || "",
    });
    const whatsappLink = document.createElement("a");
    whatsappLink.href = `https://wa.me/${whatsappNumber}?text=${text}`;
    whatsappLink.target = "_blank";
    whatsappLink.rel = "noreferrer";
    whatsappLink.click();
  });

  form.querySelector("[data-copy-inquiry]")?.addEventListener("click", async (event) => {
    if (!form.reportValidity()) return;

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
});

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
      "compression-base-layers",
    ]),
    teamwear: new Set([
      "basketball-wear", "basketball-jerseys", "football-kits", "football-jerseys",
      "custom-sublimated-teamwear", "volleyball-teamwear", "volleyball-uniforms",
      "team-warm-up-jackets", "baseball-softball-teamwear", "rugby-hockey-teamwear",
      "youth-sportswear", "club-fan-merchandise", "club-hoodies-varsity-jackets", "soccer-uniforms",
      "esports-jerseys", "cheerleading-uniforms", "track-field-uniforms", "lacrosse-uniforms",
      "wrestling-singlets", "gymnastics-leotards",
    ]),
    specialty: new Set([
      "running-wear", "running-singlets-shirts", "tennis-pickleball-apparel", "cycling-wear",
      "cycling-jerseys-bib-shorts", "outdoor-training-outerwear", "golf-apparel",
      "golf-polo-shirts-skorts", "swimwear-water-sports", "rash-guards-board-shorts",
      "combat-sports-apparel", "mma-rash-guards-fight-shorts", "racket-sports-apparel",
      "dancewear-cheer", "trail-hiking-apparel", "winter-sports-apparel",
      "triathlon-endurance-apparel", "marathon-event-apparel",
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
    const href = card.querySelector(".product-card-link")?.getAttribute("href") || "";
    const slug = href.split("/").pop()?.replace(/\.html$/, "") || "";
    card.dataset.catalogCategory = getCardCategory(slug);
    card.dataset.catalogText = card.textContent.toLowerCase();
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

document.querySelector("[data-expand-products]")?.addEventListener("click", (event) => {
  const section = event.currentTarget.closest("[data-product-section]");
  const isCollapsed = section?.classList.toggle("is-collapsed");
  event.currentTarget.setAttribute("aria-expanded", String(!isCollapsed));
  event.currentTarget.innerHTML = isCollapsed
    ? '<i data-lucide="grid-3x3"></i>Show all product categories'
    : '<i data-lucide="chevrons-up"></i>Show fewer products';
  renderIcons();
});

const renderIcons = () => {
  window.lucide?.createIcons();
};

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", renderIcons, { once: true });
} else {
  renderIcons();
}
