const header = document.querySelector("[data-header]");
const menuToggle = document.querySelector("[data-menu-toggle]");
const mobileNav = document.querySelector("[data-mobile-nav]");
const form = document.querySelector("[data-quote-form]");

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

const setMobileMenu = (isOpen) => {
  mobileNav?.classList.toggle("is-open", isOpen);
  menuToggle?.setAttribute("aria-expanded", String(isOpen));
  mobileNav?.setAttribute("aria-hidden", String(!isOpen));
};

menuToggle?.addEventListener("click", () => {
  setMobileMenu(!mobileNav?.classList.contains("is-open"));
});

mobileNav?.addEventListener("click", (event) => {
  if (event.target.matches("a")) {
    setMobileMenu(false);
  }
});

window.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    setMobileMenu(false);
  }
});

form?.addEventListener("submit", (event) => {
  event.preventDefault();
  const data = new FormData(form);
  const subject = encodeURIComponent(`GloryStarWear inquiry - ${data.get("product")}`);
  const body = encodeURIComponent(
    [
      `Name: ${data.get("name")}`,
      `Email: ${data.get("email")}`,
      `WhatsApp or Phone: ${data.get("phone") || "Not provided"}`,
      `Product Interest: ${data.get("product")}`,
      `Estimated Quantity: ${data.get("quantity") || "Not provided"}`,
      `Target Market: ${data.get("market") || "Not provided"}`,
      `Expected Timeline: ${data.get("timeline") || "Not provided"}`,
      "",
      "Project Details:",
      data.get("message"),
    ].join("\n"),
  );

  window.location.href = `mailto:kevin@glorystarwears.com?subject=${subject}&body=${body}`;
});

const renderIcons = () => {
  window.lucide?.createIcons();
};

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", renderIcons, { once: true });
} else {
  renderIcons();
}
