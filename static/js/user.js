function getCookie(name) {
    const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    return match ? match[2] : null;
}

$(function renderUserMenu() {
    const $container = $('#user-menu');

    $.ajax({
        url: '/api/user/',
        method: 'GET',
        dataType: 'json',
        xhrFields: { withCredentials: true },   // send JWT cookie
        headers: { 'Content-Type': 'application/json' }
    })
        .done(function (user) {
            // logged in
            $container.html(`
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
      `);

            // bind logout click
            $container.find('#logout-btn').on('click', function (e) {
                e.preventDefault();
                $.ajax({
                    url: '/api/user/logout',
                    method: 'POST',
                    xhrFields: { withCredentials: true },
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Content-Type': 'application/json'
                    }
                }).always(function () {
                    location.reload();
                });
            });
        })
        .fail(function () {
            // not logged in
            $container.html(`
        <a href="/login" class="btn btn-outline-primary me-2">Login</a>
        <a href="/register" class="btn btn-primary">Register</a>
      `);
        });
});