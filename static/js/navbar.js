const btn = document.getElementById('menu-btn');
const menu = document.getElementById('mobile-menu');

  // Toggle menu on button click
  btn.addEventListener('click', (e) => {
    e.stopPropagation(); // prevent document click from firing immediately
    if (menu.classList.contains('-translate-x-full')) {
      menu.classList.remove('-translate-x-full');
      menu.classList.add('translate-x-0');
    } else {
      menu.classList.add('-translate-x-full');
      menu.classList.remove('translate-x-0');
    }
  });

  // Close menu when clicking outside
  document.addEventListener('click', (e) => {
    if (!menu.contains(e.target) && !btn.contains(e.target)) {
      menu.classList.add('-translate-x-full');
      menu.classList.remove('translate-x-0');
    }
  });

  // Optional: stop clicks inside the menu from closing it
  menu.addEventListener('click', (e) => {
    e.stopPropagation();
  });
  