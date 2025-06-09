document.addEventListener('DOMContentLoaded', () => {
  const searchModal   = document.getElementById('searchModal');
  const modalInput    = searchModal.querySelector('input[type="search"]');
  const modalTrigger  = searchModal.querySelector('.input-group-text');

  function doNavSearch() {
    const term = modalInput.value.trim();
    const base = '/products/';
    const url  = term
      ? `${base}?search=${encodeURIComponent(term)}`
      : base;

    const bsModal = bootstrap.Modal.getInstance(searchModal);
    bsModal.hide();
    window.location.href = url;
  }

  modalInput.addEventListener('keydown', e => {
    if (e.key === 'Enter') {
      e.preventDefault();
      doNavSearch();
    }
  });
  modalTrigger.addEventListener('click', e => {
    e.preventDefault();
    doNavSearch();
  });

  const heroSection = document.querySelector('.hero-header');
  if (heroSection) {
    const heroInput  = heroSection.querySelector('input[type="search"]');
    const heroButton = heroSection.querySelector('button[type="submit"]');

    function doHeroSearch() {
      const term = heroInput.value.trim();
      const base = '/products/';
      const url  = term
        ? `${base}?search=${encodeURIComponent(term)}`
        : base;
      window.location.href = url;
    }

    heroInput.addEventListener('keydown', e => {
      if (e.key === 'Enter') {
        e.preventDefault();
        doHeroSearch();
      }
    });
    heroButton.addEventListener('click', e => {
      e.preventDefault();
      doHeroSearch();
    });
  }
});
