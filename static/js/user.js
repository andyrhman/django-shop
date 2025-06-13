// user.js

function getCookie(name) {
  const match = document.cookie.match(
    new RegExp('(^| )' + name + '=([^;]+)')
  );
  return match ? match[2] : null;
}

document.addEventListener('DOMContentLoaded', () => {
  const userMenuContainer = document.getElementById('user-menu');
  const cartCountBadge    = document.getElementById('cart-count');

  // Render user menu (as before)…
  fetch('/api/user/', {
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' }
  })
    .then(res => {
      if (!res.ok) throw new Error('Not logged in');
      return res.json();
    })
    .then(user => {
      userMenuContainer.innerHTML = `
        <div class="nav-item dropdown">
          <a href="#" class="nav-link dropdown-toggle d-flex align-items-center" data-bs-toggle="dropdown">
            <i class="fas fa-user fa-2x me-2"></i>
            <span>${user.fullName}</span>
          </a>
          <ul class="dropdown-menu dropdown-menu-end">
            <li><a class="dropdown-item" href="/profile/">Profile</a></li>
            <li><a class="dropdown-item" href="#" id="logout-btn">Logout</a></li>
          </ul>
        </div>
      `;
      document.getElementById('logout-btn').addEventListener('click', e => {
        e.preventDefault();
        fetch('/api/user/logout', {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
          }
        }).finally(() => window.location.reload());
      });
    })
    .catch(() => {
      userMenuContainer.innerHTML = `
        <a href="/login" class="btn btn-outline-primary me-2">Login</a>
        <a href="/register" class="btn btn-primary">Register</a>
      `;
    });

  // Fetch totalItems and update badge
  if (cartCountBadge) {
    fetch('/api/cart-total', {
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' }
    })
      .then(res => {
        if (!res.ok) throw new Error('Failed to load cart total');
        return res.json();
      })
      .then(data => {
        cartCountBadge.textContent = data.totalItems;
      })
      .catch(err => {
        console.error('Cart-total error:', err);
        // Optionally hide or style the badge on error:
        // cartCountBadge.style.display = 'none';
      });
  }
});
