/* ============================================================
   NAVIGATION — scroll solidify + mobile toggle + dropdown
   ============================================================ */
const nav = document.getElementById('main-nav');
const hamburger = document.getElementById('nav-hamburger');
const mobileNav = document.getElementById('mobile-nav');

if (nav) {
  nav.classList.add('nav--solid');
  nav.classList.remove('nav--transparent');
}

if (hamburger && mobileNav) {
  hamburger.addEventListener('click', () => {
    const isOpen = mobileNav.classList.toggle('is-open');
    hamburger.classList.toggle('is-open', isOpen);
    document.body.style.overflow = isOpen ? 'hidden' : '';
  });
}

// Close mobile nav on link click
document.querySelectorAll('.nav__mobile-link, .nav__mobile-sublink').forEach(link => {
  link.addEventListener('click', () => {
    mobileNav.classList.remove('is-open');
    hamburger.classList.remove('is-open');
    document.body.style.overflow = '';
  });
});

// Mobile event types toggle
const mobileEventsToggle = document.getElementById('mobile-events-toggle');
const mobileEventsSub = document.getElementById('mobile-events-sub');

if (mobileEventsToggle && mobileEventsSub) {
  mobileEventsToggle.addEventListener('click', (e) => {
    e.preventDefault();
    const isOpen = mobileEventsSub.style.display === 'flex';
    mobileEventsSub.style.display = isOpen ? 'none' : 'flex';
  });
}

/* ============================================================
   VIDEO MODAL
   ============================================================ */
const modalBackdrop = document.getElementById('video-modal');
const modalVideoWrap = document.getElementById('modal-video-wrap');
const modalClose = document.getElementById('modal-close');

function openModal(src, type = 'video') {
  if (!modalBackdrop) return;

  modalVideoWrap.innerHTML = '';

  if (type === 'youtube') {
    const iframe = document.createElement('iframe');
    iframe.src = src + '?autoplay=1&rel=0';
    iframe.allow = 'autoplay; encrypted-media; fullscreen';
    iframe.allowFullscreen = true;
    modalVideoWrap.appendChild(iframe);
  } else {
    const video = document.createElement('video');
    video.src = src;
    video.controls = true;
    video.autoplay = true;
    video.playsInline = true;
    video.style.width = '100%';
    video.style.height = '100%';
    video.style.objectFit = 'contain';
    modalVideoWrap.appendChild(video);
  }

  modalBackdrop.classList.add('is-open');
  document.body.style.overflow = 'hidden';
}

function closeModal() {
  if (!modalBackdrop) return;
  modalBackdrop.classList.remove('is-open');
  document.body.style.overflow = '';
  // Stop video playback
  setTimeout(() => { modalVideoWrap.innerHTML = ''; }, 300);
}

// Clip thumbnails
document.querySelectorAll('[data-video-src]').forEach(el => {
  el.addEventListener('click', () => {
    const src = el.dataset.videoSrc;
    const type = el.dataset.videoType || 'video';
    openModal(src, type);
  });
});

if (modalClose) modalClose.addEventListener('click', closeModal);

if (modalBackdrop) {
  modalBackdrop.addEventListener('click', (e) => {
    if (e.target === modalBackdrop) closeModal();
  });
}

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') closeModal();
});

/* ============================================================
   SCROLL ANIMATIONS — fade in on scroll
   ============================================================ */
const observerOptions = {
  threshold: 0.12,
  rootMargin: '0px 0px -40px 0px'
};

const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('is-visible');
      observer.unobserve(entry.target);
    }
  });
}, observerOptions);

document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));

/* ============================================================
   FORM — basic client-side UX
   ============================================================ */
const consultForm = document.getElementById('consult-form');

if (consultForm) {
  consultForm.addEventListener('submit', (e) => {
    const btn = consultForm.querySelector('[type="submit"]');
    if (btn) {
      btn.disabled = true;
      btn.textContent = 'Sending…';
    }
  });
}

/* ============================================================
   REELS CAROUSEL
   ============================================================ */
(function () {
  var stage = document.getElementById('reels-stage');
  if (!stage) return;

  var overflow  = document.getElementById('reels-overflow');
  var track     = document.getElementById('reels-track');
  var prevBtn   = document.getElementById('reels-prev');
  var nextBtn   = document.getElementById('reels-next');
  var dotsWrap  = document.getElementById('reels-indicators');
  var cards     = Array.from(track.querySelectorAll('.reel-card'));
  var total     = cards.length;
  var current   = 0;
  var GAP       = 16;
  var lastSwipeTime = 0;

  // Build dots
  cards.forEach(function (_, i) {
    var dot = document.createElement('button');
    dot.className = 'reels-dot';
    dot.setAttribute('aria-label', 'Go to clip ' + (i + 1));
    dot.addEventListener('click', function () { goTo(i); });
    dotsWrap.appendChild(dot);
  });

  function cw() { return cards[0].offsetWidth; }

  function translateFor(index) {
    var containerW = overflow.offsetWidth;
    var offset = (containerW - cw()) / 2;
    return offset - index * (cw() + GAP);
  }

  function goTo(index, animate) {
    if (index < 0 || index >= total) return;
    if (animate === undefined) animate = true;

    var prevVideo = cards[current].querySelector('video');
    if (prevVideo && !prevVideo.paused) {
      prevVideo.pause();
      prevVideo.currentTime = 0;
    }
    var prevUi = cards[current].querySelector('.reel-card__ui');
    if (prevUi) prevUi.classList.remove('is-playing');

    current = index;

    if (!animate) {
      track.style.transition = 'none';
      track.style.transform = 'translateX(' + translateFor(current) + 'px)';
      track.offsetHeight;
      track.style.transition = '';
    } else {
      track.style.transform = 'translateX(' + translateFor(current) + 'px)';
    }

    cards.forEach(function (c, i) { c.classList.toggle('is-active', i === current); });
    dotsWrap.querySelectorAll('.reels-dot').forEach(function (d, i) {
      d.classList.toggle('is-active', i === current);
    });

    prevBtn.disabled = current === 0;
    nextBtn.disabled = current === total - 1;
  }

  prevBtn.addEventListener('click', function () { goTo(current - 1); });
  nextBtn.addEventListener('click', function () { goTo(current + 1); });

  // Click to play / pause
  cards.forEach(function (card, i) {
    var video = card.querySelector('video');
    var ui    = card.querySelector('.reel-card__ui');
    var frame = card.querySelector('.reel-card__frame');

    frame.addEventListener('click', function () {
      if (Date.now() - lastSwipeTime < 300) return;
      if (current !== i) { goTo(i); return; }
      if (video.paused) {
        video.play().catch(function () {});
        ui.classList.add('is-playing');
      } else {
        video.pause();
        ui.classList.remove('is-playing');
      }
    });

    video.addEventListener('ended', function () {
      ui.classList.remove('is-playing');
    });
  });

  // Touch swipe
  var touchStartX = 0, touchStartY = 0, swipeDetected = false;

  overflow.addEventListener('touchstart', function (e) {
    touchStartX  = e.touches[0].clientX;
    touchStartY  = e.touches[0].clientY;
    swipeDetected = false;
  }, { passive: true });

  overflow.addEventListener('touchmove', function (e) {
    var dx = Math.abs(e.touches[0].clientX - touchStartX);
    var dy = Math.abs(e.touches[0].clientY - touchStartY);
    if (dx > dy && dx > 12) swipeDetected = true;
  }, { passive: true });

  overflow.addEventListener('touchend', function (e) {
    if (!swipeDetected) return;
    var dx = e.changedTouches[0].clientX - touchStartX;
    if (Math.abs(dx) > 40) {
      goTo(dx < 0 ? current + 1 : current - 1);
      lastSwipeTime = Date.now();
    }
    e.preventDefault();
  });

  // Keyboard — only when clips section is in view
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') return;
    var clips = document.getElementById('clips');
    if (!clips) return;
    var r = clips.getBoundingClientRect();
    if (r.top < window.innerHeight && r.bottom > 0) {
      if (e.key === 'ArrowLeft')  goTo(current - 1);
      if (e.key === 'ArrowRight') goTo(current + 1);
      e.preventDefault();
    }
  });

  // Recalculate on resize
  var resizeTimer;
  window.addEventListener('resize', function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function () { goTo(current, false); }, 100);
  });

  requestAnimationFrame(function () { goTo(Math.floor(total / 2), false); });
})();

/* ============================================================
   ACTIVE NAV LINK — highlight current page
   ============================================================ */
const currentPath = window.location.pathname;
document.querySelectorAll('.nav__link, .nav__dropdown-item').forEach(link => {
  const href = link.getAttribute('href');
  if (href && currentPath.endsWith(href)) {
    link.classList.add('nav__link--active');
  }
});
