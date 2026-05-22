// === NAVBAR SCROLL ===
const navbar = document.querySelector('.navbar');
window.addEventListener('scroll', () => {
    navbar.classList.toggle('scrolled', window.scrollY > 20);
});

// === TABS CÓMO FUNCIONA ===
const tabBtns = document.querySelectorAll('.tab-btn');
const pasosTrabjador = document.getElementById('pasos-trabajador');
const pasosEmpleador = document.getElementById('pasos-empleador');

tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        tabBtns.forEach(b => b.classList.remove('tab-activo'));
        btn.classList.add('tab-activo');

        if (btn.dataset.tab === 'trabajador') {
            pasosTrabjador.style.display = '';
            pasosTrabjador.classList.remove('pasos-oculto');
            pasosEmpleador.style.display = 'none';
            pasosEmpleador.classList.add('pasos-oculto');
        } else {
            pasosEmpleador.style.display = '';
            pasosEmpleador.classList.remove('pasos-oculto');
            pasosTrabjador.style.display = 'none';
            pasosTrabjador.classList.add('pasos-oculto');
        }
    });
});

// === HAMBURGER MENU (mobile) ===
const hamburger = document.getElementById('hamburger');
const navLinks = document.querySelector('.nav-links');
const navAcciones = document.querySelector('.nav-acciones');

hamburger.addEventListener('click', () => {
    const isOpen = navLinks.style.display === 'flex';
    navLinks.style.display = isOpen ? 'none' : 'flex';
    navLinks.style.flexDirection = 'column';
    navLinks.style.position = 'absolute';
    navLinks.style.top = '6.4rem';
    navLinks.style.left = '0';
    navLinks.style.right = '0';
    navLinks.style.background = '#fff';
    navLinks.style.padding = '2rem';
    navLinks.style.borderBottom = '1px solid #E0E0E0';
    navLinks.style.zIndex = '999';

    if (!isOpen) {
        navLinks.style.display = 'flex';
    }
});

// === SMOOTH SCROLL ===
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            e.preventDefault();
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});

// === ANIMACIÓN AL ENTRAR EN VIEWPORT ===
const observar = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, { threshold: 0.1 });

document.querySelectorAll('.oficio-card, .paso-card, .mock-card').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    observar.observe(el);
});