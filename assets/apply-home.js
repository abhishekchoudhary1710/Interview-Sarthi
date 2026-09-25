/* Navigation and screenshot enhancement; all page content works without JavaScript. */
(() => {
  const toggle = document.querySelector('.menu-toggle');
  const menu = document.querySelector('#main-nav');
  if (toggle && menu) {
    document.documentElement.classList.add('js');
    const closeMenu = () => { menu.classList.remove('open'); toggle.setAttribute('aria-expanded', 'false'); };
    toggle.addEventListener('click', () => {
      const open = menu.classList.toggle('open');
      toggle.setAttribute('aria-expanded', String(open));
    });
    menu.addEventListener('click', event => { if (event.target.closest('a')) closeMenu(); });
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && menu.classList.contains('open')) { closeMenu(); toggle.focus(); }
    });
  }
  const preview = document.querySelector('.screenshot-link');
  const dialog = document.querySelector('#screenshot-dialog');
  if (preview && dialog && typeof dialog.showModal === 'function') {
    preview.addEventListener('click', event => {
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      dialog.showModal();
    });
    dialog.querySelector('button').addEventListener('click', () => dialog.close());
    dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });
  }
})();
