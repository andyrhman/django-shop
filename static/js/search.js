document.addEventListener('DOMContentLoaded', () => {
  const searchModal   = document.getElementById('searchModal');
  const input         = searchModal.querySelector('input[type="search"]');
  const searchTrigger = searchModal.querySelector('.input-group-text');

  function doNavSearch() {
    const term = input.value.trim();
    const base = '/products/';
    const url  = term
      ? `${base}?search=${encodeURIComponent(term)}`
      : base;

    const bsModal = bootstrap.Modal.getInstance(searchModal);
    bsModal.hide();
    window.location.href = url;
  }

  input.addEventListener('keydown', e => {
    if (e.key === 'Enter') {
      e.preventDefault();
      doNavSearch();
    }
  });

  searchTrigger.addEventListener('click', e => {
    e.preventDefault();
    doNavSearch();
  });
});
