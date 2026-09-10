/*!
* Start Bootstrap - Shop Homepage v5.0.6 (https://startbootstrap.com/template/shop-homepage)
* Copyright 2013-2023 Start Bootstrap
* Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-shop-homepage/blob/master/LICENSE)
*/
// This file is intentionally blank
// Use this file to add JavaScript to your project

// Small fallback interactions so the standalone demo remains usable even if Bootstrap JS is unavailable.
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.collage-dropdown > .dropdown-toggle').forEach(toggle => {
    toggle.addEventListener('click', (event) => {
      event.preventDefault();
      const menu = toggle.parentElement.querySelector('.dropdown-menu');
      if (!menu) return;
      document.querySelectorAll('.collage-dropdown-menu.show').forEach(other => { if (other !== menu) other.classList.remove('show'); });
      menu.classList.toggle('show');
    });
  });

  document.addEventListener('click', (event) => {
    if (!event.target.closest('.collage-dropdown')) {
      document.querySelectorAll('.collage-dropdown-menu.show').forEach(menu => menu.classList.remove('show'));
    }
  });

  const canvas = document.getElementById('offcanvasNavbar');
  document.querySelectorAll('[data-bs-target="#offcanvasNavbar"]').forEach(button => {
    button.addEventListener('click', () => {
      if (!canvas) return;
      canvas.classList.add('show');
      canvas.style.visibility = 'visible';
      canvas.setAttribute('aria-modal', 'true');
      canvas.removeAttribute('aria-hidden');
    });
  });
  document.querySelectorAll('[data-bs-dismiss="offcanvas"]').forEach(button => {
    button.addEventListener('click', () => {
      if (!canvas) return;
      canvas.classList.remove('show');
      canvas.style.visibility = 'hidden';
      canvas.removeAttribute('aria-modal');
      canvas.setAttribute('aria-hidden', 'true');
    });
  });
});
