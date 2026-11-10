document.querySelectorAll('.kuantum-hero').forEach(function (hero) {
  var slides = Array.from(hero.querySelectorAll('.kuantum-hero-slide'));
  var dots = Array.from(hero.querySelectorAll('.kuantum-hero-dots button'));
  var current = 0;
  var timer;
  function show(index) {
    current = (index + slides.length) % slides.length;
    slides.forEach(function (slide, i) { slide.hidden = i !== current; });
    dots.forEach(function (dot, i) { dot.setAttribute('aria-pressed', String(i === current)); });
  }
  function stop() { clearInterval(timer); }
  function start() {
    stop();
    if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      timer = setInterval(function () { show(current + 1); }, 5000);
    }
  }
  hero.querySelector('.kuantum-hero-prev').addEventListener('click', function () { stop(); show(current - 1); });
  hero.querySelector('.kuantum-hero-next').addEventListener('click', function () { stop(); show(current + 1); });
  dots.forEach(function (dot, i) { dot.addEventListener('click', function () { stop(); show(i); }); });
  hero.addEventListener('mouseenter', stop);
  hero.addEventListener('mouseleave', start);
  hero.addEventListener('focusin', stop);
  hero.addEventListener('focusout', function (event) { if (!hero.contains(event.relatedTarget)) start(); });
  start();
});
