(function () {
  "use strict";

  const root = document.querySelector("[data-supplier-catalog]");
  if (!root) return;

  const elements = {
    total: document.querySelector("[data-catalog-total]"),
    categoryTotal: document.querySelector("[data-catalog-category-total]"),
    heading: document.querySelector("[data-catalog-heading]"),
    categories: document.querySelector("[data-catalog-categories]"),
    search: document.querySelector("[data-catalog-search]"),
    clear: document.querySelector("[data-catalog-clear]"),
    sort: document.querySelector("[data-catalog-sort]"),
    results: document.querySelector("[data-catalog-results]"),
    reset: document.querySelector("[data-catalog-reset]"),
    grid: document.querySelector("[data-supplier-catalog-grid]"),
    empty: document.querySelector("[data-catalog-empty]"),
    emptyReset: document.querySelector("[data-catalog-empty-reset]"),
    loadMore: document.querySelector("[data-catalog-load-more]"),
    sidebarToggle: document.querySelector("[data-catalog-sidebar-toggle]"),
    sidebar: document.querySelector(".supplier-catalog-sidebar"),
    modal: document.querySelector("[data-catalog-modal]"),
    modalTitle: document.querySelector("[data-catalog-modal-title]"),
    modalCategory: document.querySelector("[data-catalog-modal-category]"),
    modalId: document.querySelector("[data-catalog-modal-id]"),
    modalCount: document.querySelector("[data-catalog-modal-count]"),
    modalNote: document.querySelector("[data-catalog-modal-note]"),
    modalQuote: document.querySelector("[data-catalog-modal-quote]"),
    modalSource: document.querySelector("[data-catalog-modal-source]"),
    stage: document.querySelector("[data-catalog-stage-image]"),
    thumbnails: document.querySelector("[data-catalog-thumbnails]"),
    previous: document.querySelector("[data-catalog-prev]"),
    next: document.querySelector("[data-catalog-next]")
  };

  const state = {
    products: [],
    categories: [],
    activeCategory: "",
    activeSubcategory: "",
    query: "",
    sort: "latest",
    visibleLimit: 48,
    modalProduct: null,
    modalImages: [],
    modalIndex: 0,
    lastFocused: null
  };

  const formatNumber = (value) => new Intl.NumberFormat("en-US").format(value);
  const catalogAssetVersion = "20260922-catalog-avif-v1";
  const localCatalogAssetPrefix = "../assets/catalog/";
  const localCompressedCatalogAssetBase = "../assets/catalog/catalog-clean/20260922-v1";
  const remoteCatalogAssetBase = "https://assets.glorystarwears.com/catalog-clean/20260922-v1";
  const useLocalCatalogAssets = ["localhost", "127.0.0.1"].includes(window.location.hostname);
  const versionedCatalogAsset = (source) => {
    if (!source || !source.startsWith(localCatalogAssetPrefix)) return source || "";
    const match = source.slice(localCatalogAssetPrefix.length).match(/^(watermark-clean-v[23])\/([^/]+)\/(.+)$/);
    if (match) {
      const filename = match[3].replace(/\.(?:jpe?g)$/i, ".avif");
      const assetBase = useLocalCatalogAssets ? localCompressedCatalogAssetBase : remoteCatalogAssetBase;
      source = `${assetBase}/${match[1]}/${match[2]}/${filename}`;
    }
    const separator = source.includes("?") ? "&" : "?";
    return `${source}${separator}v=${catalogAssetVersion}`;
  };

  const trackCatalogEvent = (name, properties) => {
    if (typeof trackEvent === "function") trackEvent(name, properties);
  };

  const refreshIcons = () => {
    if (window.lucide && typeof window.lucide.createIcons === "function") {
      window.lucide.createIcons();
    }
  };

  const setImageSource = (image, source, fallback) => {
    image.src = versionedCatalogAsset(source || fallback);
    image.dataset.fallback = versionedCatalogAsset(fallback);
    image.addEventListener("error", () => {
      if (image.dataset.fallback && image.src !== image.dataset.fallback) {
        image.src = image.dataset.fallback;
      } else {
        image.classList.add("is-image-missing");
      }
    }, { once: false });
  };

  const createImage = (source, fallback, alt, className, loading) => {
    const image = document.createElement("img");
    image.className = className || "";
    image.alt = alt || "";
    image.loading = loading || "lazy";
    image.decoding = "async";
    setImageSource(image, source, fallback);
    return image;
  };

  const productImages = (product) => {
    const images = [];
    const seenRemoteDirectories = new Set();
    const remoteDirectory = (source) => {
      if (!source || !/^https?:\/\//i.test(source)) return "";
      return source.slice(0, source.lastIndexOf("/"));
    };
    const add = (source, fallback, width, height) => {
      if (!source) return;
      const directory = remoteDirectory(source) || remoteDirectory(fallback);
      if (images.some((item) => item.source === source) || (directory && seenRemoteDirectories.has(directory))) return;
      if (directory) seenRemoteDirectories.add(directory);
      images.push({ source, fallback: fallback || "", width, height });
    };

    add(product.cover, product.coverRemote);
    (product.gallery || []).forEach((image) => {
      // A cleaned hosted variant, when present, is always preferred. The
      // original supplier URL is retained only as a migration fallback until
      // the all-or-nothing catalog switch is made.
      add(image.clean || image.src, image.src, image.width, image.height);
    });
    if (!images.length) add(product.coverRemote, "");
    return images;
  };

  const getFilteredProducts = () => {
    const query = state.query.trim().toLowerCase();
    const filtered = state.products.filter((product) => {
      const categoryMatches = !state.activeCategory || product.category === state.activeCategory;
      if (!categoryMatches) return false;
      const subcategoryMatches = !state.activeSubcategory || (product.subcategories || []).includes(state.activeSubcategory);
      if (!subcategoryMatches) return false;
      if (!query) return true;
      return [product.id, product.title, product.category].some((value) => String(value || "").toLowerCase().includes(query));
    });

    return filtered.sort((a, b) => {
      if (state.sort === "photos") return (b.photoCount || 0) - (a.photoCount || 0) || a.id.localeCompare(b.id);
      if (state.sort === "title") return a.id.localeCompare(b.id, undefined, { numeric: true, sensitivity: "base" });
      if (state.sort === "catalog") return a.sourceIndex - b.sourceIndex;
      return String(b.publishedDate || "").localeCompare(String(a.publishedDate || "")) || a.sourceIndex - b.sourceIndex;
    });
  };

  const updateCategoryState = () => {
    elements.categories.querySelectorAll("[data-catalog-category]").forEach((button) => {
      const selected = !state.activeSubcategory && button.dataset.catalogCategory === state.activeCategory;
      button.setAttribute("aria-pressed", String(selected));
      button.classList.toggle("is-active", selected);
    });
    elements.categories.querySelectorAll("[data-catalog-subcategory]").forEach((button) => {
      const selected = button.dataset.catalogSubcategory === state.activeSubcategory;
      button.setAttribute("aria-pressed", String(selected));
      button.classList.toggle("is-active", selected);
    });
  };

  const renderCategories = () => {
    const fragment = document.createDocumentFragment();
    const allButton = document.createElement("button");
    allButton.type = "button";
    allButton.className = "supplier-category-button";
    allButton.dataset.catalogCategory = "";
    allButton.setAttribute("aria-pressed", "true");
    const allLabel = document.createElement("span");
    allLabel.textContent = "All products";
    const allCount = document.createElement("strong");
    allCount.textContent = formatNumber(state.products.length);
    allButton.append(allLabel, allCount);
    fragment.appendChild(allButton);

    state.categories.forEach((category) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "supplier-category-button";
      button.dataset.catalogCategory = category.name;
      button.setAttribute("aria-pressed", "false");
      const label = document.createElement("span");
      label.textContent = category.name;
      const count = document.createElement("strong");
      count.textContent = formatNumber(category.count);
      button.append(label, count);
      fragment.appendChild(button);
      if (category.children?.length) {
        const childList = document.createElement("div");
        childList.className = "supplier-category-child-list";
        category.children.forEach((child) => {
          const childButton = document.createElement("button");
          childButton.type = "button";
          childButton.className = "supplier-category-button supplier-category-child-button";
          childButton.dataset.catalogSubcategory = child.name;
          childButton.setAttribute("aria-pressed", "false");
          const childLabel = document.createElement("span");
          childLabel.textContent = child.name;
          const childCount = document.createElement("strong");
          childCount.textContent = formatNumber(child.count);
          childButton.append(childLabel, childCount);
          childList.appendChild(childButton);
        });
        fragment.appendChild(childList);
      }
    });

    elements.categories.replaceChildren(fragment);
  };

  const renderCard = (product) => {
    const article = document.createElement("article");
    article.className = "supplier-product-card";

    const button = document.createElement("button");
    button.type = "button";
    button.className = "supplier-product-card-open";
    button.dataset.catalogProductId = product.id;
    button.setAttribute("aria-label", `Open ${product.title}, ${product.id}`);

    const media = document.createElement("div");
    media.className = "supplier-product-card-media";
    const image = createImage(product.cover, product.coverRemote, `${product.title} product reference`, "supplier-product-card-image", "lazy");
    media.appendChild(image);
    const code = document.createElement("span");
    code.className = "supplier-product-card-code";
    code.textContent = product.id;
    media.appendChild(code);
    const photoCount = document.createElement("span");
    photoCount.className = "supplier-product-card-photo-count";
    photoCount.textContent = `${product.photoCount || 0} photos`;
    media.appendChild(photoCount);

    const body = document.createElement("div");
    body.className = "supplier-product-card-body";
    const category = document.createElement("p");
    category.className = "supplier-product-card-category";
    category.textContent = [product.category, ...(product.subcategories || [])].join(" · ");
    const title = document.createElement("h3");
    title.textContent = product.title;
    const description = document.createElement("p");
    description.className = "supplier-product-card-description";
    description.textContent = `Reference album · ${product.photoCount || 0} detail images`;
    const action = document.createElement("span");
    action.className = "supplier-product-card-action";
    action.innerHTML = "View product details <span aria-hidden=\"true\">↗</span>";
    body.append(category, title, description, action);

    button.append(media, body);
    article.appendChild(button);
    return article;
  };

  const renderProducts = () => {
    const filtered = getFilteredProducts();
    const visible = filtered.slice(0, state.visibleLimit);
    const fragment = document.createDocumentFragment();
    visible.forEach((product) => fragment.appendChild(renderCard(product)));
    elements.grid.replaceChildren(fragment);

    const total = filtered.length;
    const shown = visible.length;
    if (!total) {
      elements.results.textContent = "No matching products";
      elements.empty.hidden = false;
    } else {
      elements.results.textContent = `Showing 1–${formatNumber(shown)} of ${formatNumber(total)} products`;
      elements.empty.hidden = true;
    }
    elements.loadMore.hidden = shown >= total || total === 0;
    elements.loadMore.textContent = `Load more products (${formatNumber(Math.min(48, total - shown))})`;
    elements.reset.hidden = !state.activeCategory && !state.activeSubcategory && !state.query;
    elements.clear.hidden = !state.query;
    elements.heading.textContent = state.activeSubcategory || state.activeCategory || "All products";
    updateCategoryState();
    refreshIcons();
  };

  const resetFilters = (track = true) => {
    state.activeCategory = "";
    state.activeSubcategory = "";
    state.query = "";
    state.sort = "latest";
    state.visibleLimit = 48;
    elements.search.value = "";
    elements.sort.value = "latest";
    renderProducts();
    if (track) trackCatalogEvent("catalog_filter_reset", {});
  };

  const showModalImage = (index) => {
    if (!state.modalImages.length) return;
    state.modalIndex = (index + state.modalImages.length) % state.modalImages.length;
    const image = state.modalImages[state.modalIndex];
    const stageLabel = `${state.modalProduct.title} detail image ${state.modalIndex + 1}`;
    elements.stage.style.backgroundImage = `url("${versionedCatalogAsset(image.source || image.fallback).replaceAll('"', "%22")}")`;
    elements.stage.setAttribute("aria-label", stageLabel);
    elements.thumbnails.querySelectorAll("[data-catalog-image-index]").forEach((thumbnail) => {
      const selected = Number(thumbnail.dataset.catalogImageIndex) === state.modalIndex;
      thumbnail.setAttribute("aria-selected", String(selected));
      thumbnail.classList.toggle("is-active", selected);
    });
    elements.previous.disabled = state.modalImages.length < 2;
    elements.next.disabled = state.modalImages.length < 2;
  };

  const openProduct = (product) => {
    state.modalProduct = product;
    state.modalImages = productImages(product);
    state.modalIndex = 0;
    state.lastFocused = document.activeElement;
    elements.modalTitle.textContent = product.title;
    elements.modalCategory.textContent = [product.category, ...(product.subcategories || [])].join(" · ");
    elements.modalId.textContent = `Reference ${product.id}`;
    elements.modalCount.textContent = `${product.photoCount || state.modalImages.length} detail images`;
    elements.modalNote.textContent = `${product.publishedDate ? `Catalog date ${product.publishedDate} · ` : ""}Reference images are for product discussion and sampling direction.`;
    elements.modalQuote.href = `../contact.html?product=${encodeURIComponent(product.title)}&reference=${encodeURIComponent(product.id)}#quote-form`;
    elements.modalSource.href = product.sourceUrl || product.categoryUrl || "#";

    const thumbnails = document.createDocumentFragment();
    state.modalImages.forEach((image, index) => {
      const thumbnail = document.createElement("button");
      thumbnail.type = "button";
      thumbnail.className = "supplier-product-thumbnail";
      thumbnail.dataset.catalogImageIndex = String(index);
      thumbnail.setAttribute("role", "tab");
      thumbnail.setAttribute("aria-label", `Show detail image ${index + 1}`);
      thumbnail.setAttribute("aria-selected", String(index === 0));
      thumbnail.appendChild(createImage(image.source, image.fallback, "", "", "lazy"));
      thumbnails.appendChild(thumbnail);
    });
    elements.thumbnails.replaceChildren(thumbnails);
    elements.modal.hidden = false;
    requestAnimationFrame(() => elements.modal.classList.add("is-open"));
    document.body.classList.add("supplier-modal-open");
    showModalImage(0);
    elements.modal.querySelector("[data-catalog-close]")?.focus();
    trackCatalogEvent("catalog_product_open", { product_id: product.id, category: product.category, photo_count: product.photoCount || 0 });
    refreshIcons();
  };

  const closeModal = () => {
    if (elements.modal.hidden) return;
    elements.modal.classList.remove("is-open");
    document.body.classList.remove("supplier-modal-open");
    window.setTimeout(() => {
      if (!elements.modal.classList.contains("is-open")) elements.modal.hidden = true;
    }, 160);
    state.modalProduct = null;
    if (state.lastFocused && typeof state.lastFocused.focus === "function") state.lastFocused.focus();
  };

  const handleKeydown = (event) => {
    if (elements.modal.hidden) return;
    if (event.key === "Escape") closeModal();
    if (event.key === "ArrowLeft") showModalImage(state.modalIndex - 1);
    if (event.key === "ArrowRight") showModalImage(state.modalIndex + 1);
  };

  const bindEvents = () => {
    elements.categories.addEventListener("click", (event) => {
      const categoryButton = event.target.closest("[data-catalog-category]");
      const subcategoryButton = event.target.closest("[data-catalog-subcategory]");
      if (!categoryButton && !subcategoryButton) return;
      if (subcategoryButton) {
        state.activeCategory = "Stock Item";
        state.activeSubcategory = subcategoryButton.dataset.catalogSubcategory || "";
      } else {
        state.activeCategory = categoryButton.dataset.catalogCategory || "";
        state.activeSubcategory = "";
      }
      state.visibleLimit = 48;
      renderProducts();
      trackCatalogEvent("catalog_category_select", { category: state.activeSubcategory || state.activeCategory || "all" });
      if (window.matchMedia("(max-width: 880px)").matches) {
        elements.sidebar.classList.remove("is-open");
        elements.sidebarToggle.setAttribute("aria-expanded", "false");
      }
    });

    elements.search.addEventListener("input", () => {
      state.query = elements.search.value;
      state.visibleLimit = 48;
      renderProducts();
    });
    elements.search.addEventListener("change", () => {
      if (state.query.trim()) trackCatalogEvent("catalog_search", { query_length: state.query.trim().length });
    });
    elements.clear.addEventListener("click", () => {
      state.query = "";
      state.visibleLimit = 48;
      elements.search.value = "";
      renderProducts();
      elements.search.focus();
    });
    elements.sort.addEventListener("change", () => {
      state.sort = elements.sort.value;
      state.visibleLimit = 48;
      renderProducts();
      trackCatalogEvent("catalog_sort", { sort: state.sort });
    });
    elements.reset.addEventListener("click", () => resetFilters());
    elements.emptyReset.addEventListener("click", () => resetFilters());
    elements.loadMore.addEventListener("click", () => {
      state.visibleLimit += 48;
      renderProducts();
    });
    elements.grid.addEventListener("click", (event) => {
      const button = event.target.closest("[data-catalog-product-id]");
      if (!button) return;
      const product = state.products.find((item) => item.id === button.dataset.catalogProductId);
      if (product) openProduct(product);
    });
    elements.thumbnails.addEventListener("click", (event) => {
      const button = event.target.closest("[data-catalog-image-index]");
      if (button) showModalImage(Number(button.dataset.catalogImageIndex));
    });
    elements.previous.addEventListener("click", () => showModalImage(state.modalIndex - 1));
    elements.next.addEventListener("click", () => showModalImage(state.modalIndex + 1));
    document.querySelectorAll("[data-catalog-close]").forEach((button) => button.addEventListener("click", closeModal));
    document.addEventListener("keydown", handleKeydown);
    elements.sidebarToggle.addEventListener("click", () => {
      const open = elements.sidebar.classList.toggle("is-open");
      elements.sidebarToggle.setAttribute("aria-expanded", String(open));
    });
  };

  const loadCatalog = async () => {
    try {
      const response = await fetch(`../assets/catalog/catalog-data.json?v=${catalogAssetVersion}`, { credentials: "same-origin" });
      if (!response.ok) throw new Error(`Catalog request failed: ${response.status}`);
      const data = await response.json();
      state.products = (data.products || []).map((product, index) => ({ ...product, sourceIndex: index }));
      state.categories = data.categories || [];
      elements.total.textContent = formatNumber(data.productsCount || state.products.length);
      elements.categoryTotal.textContent = `${formatNumber(state.categories.length)} categories`;
      renderCategories();
      renderProducts();
    } catch (error) {
      console.error("Unable to load supplier catalog", error);
      elements.results.textContent = "Catalog unavailable right now";
      elements.empty.hidden = false;
      elements.empty.querySelector("strong").textContent = "Catalog unavailable right now";
      elements.empty.querySelector("p").textContent = "Please refresh the page or send us a product inquiry directly.";
      elements.loadMore.hidden = true;
    }
  };

  bindEvents();
  loadCatalog();
}());
