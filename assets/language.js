/* Navigation between pre-rendered language editions. No translation service. */
(() => {
  const picker = document.querySelector('[data-language-switcher]');
  if (!picker) return;
  const trigger = picker.querySelector('summary');
  const links = [...picker.querySelectorAll('[data-site-language]')];
  const currentUrl = new URL(location.href);
  links.forEach((link) => {
    const target = new URL(link.getAttribute('href'), location.href);
    target.search = currentUrl.search;
    target.searchParams.delete('lang');
    target.hash = currentUrl.hash;
    link.href = target.href;
  });
  const closeMobile = () => {
    const toggle = document.querySelector('[data-menu-toggle]');
    if (toggle?.getAttribute('aria-expanded') === 'true') toggle.click();
  };
  trigger.addEventListener('click', closeMobile);
  picker.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') { picker.open = false; trigger.focus(); event.stopPropagation(); }
    if (!['ArrowDown', 'ArrowUp', 'Home', 'End'].includes(event.key)) return;
    event.preventDefault();
    closeMobile();
    picker.open = true;
    const index = links.indexOf(document.activeElement);
    const next = event.key === 'Home' ? 0 : event.key === 'End' ? links.length - 1
      : (index + (event.key === 'ArrowDown' ? 1 : -1) + links.length) % links.length;
    links[next].focus();
  });
  document.addEventListener('click', (event) => { if (!picker.contains(event.target)) picker.open = false; });
  document.addEventListener('focusin', (event) => { if (!picker.contains(event.target)) picker.open = false; });
})();
