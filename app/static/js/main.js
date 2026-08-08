document.addEventListener("DOMContentLoaded", function () {
  /* ---------- Mobile nav toggle ---------- */
  var navToggle = document.getElementById("navToggle");
  var navMenu = document.getElementById("navMenu");
  if (navToggle && navMenu) {
    navToggle.addEventListener("click", function () {
      var isOpen = navMenu.classList.toggle("is-open");
      navToggle.setAttribute("aria-expanded", isOpen);
    });
    navMenu.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        navMenu.classList.remove("is-open");
        navToggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  /* ---------- Scroll fade-in ---------- */
  var fadeEls = document.querySelectorAll(".fade-in-up");
  if ("IntersectionObserver" in window && fadeEls.length) {
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12 }
    );
    fadeEls.forEach(function (el) { observer.observe(el); });
  } else {
    fadeEls.forEach(function (el) { el.classList.add("is-visible"); });
  }

  /* ---------- Gallery filter ---------- */
  var filterBtns = document.querySelectorAll(".gallery-filter-btn");
  var galleryItems = document.querySelectorAll(".gallery-item");
  if (filterBtns.length) {
    filterBtns.forEach(function (btn) {
      btn.addEventListener("click", function () {
        filterBtns.forEach(function (b) { b.classList.remove("is-active"); });
        btn.classList.add("is-active");
        var category = btn.getAttribute("data-category");
        var showAll = btn.getAttribute("data-all") === "true";
        galleryItems.forEach(function (item) {
          var match = showAll || item.getAttribute("data-category") === category;
          item.style.display = match ? "" : "none";
        });
      });
    });
  }

  /* ---------- Lightbox ---------- */
  var lightbox = document.getElementById("lightbox");
  if (lightbox) {
    var lightboxImg = document.getElementById("lightboxImg");
    var lightboxCaption = document.getElementById("lightboxCaption");
    var visibleItems = [];
    var currentIndex = 0;

    function getVisibleItems() {
      return Array.prototype.filter.call(galleryItems, function (item) {
        return item.style.display !== "none";
      });
    }

    function openLightboxAt(index) {
      visibleItems = getVisibleItems();
      if (!visibleItems.length) return;
      currentIndex = (index + visibleItems.length) % visibleItems.length;
      var item = visibleItems[currentIndex];
      lightboxImg.src = item.getAttribute("data-full") || item.querySelector("img").src;
      lightboxCaption.textContent = item.getAttribute("data-title") || "";
      lightbox.classList.add("is-open");
    }

    galleryItems.forEach(function (item, idx) {
      item.addEventListener("click", function () {
        visibleItems = getVisibleItems();
        var visIdx = visibleItems.indexOf(item);
        openLightboxAt(visIdx >= 0 ? visIdx : 0);
      });
    });

    var closeBtn = document.getElementById("lightboxClose");
    var prevBtn = document.getElementById("lightboxPrev");
    var nextBtn = document.getElementById("lightboxNext");
    if (closeBtn) closeBtn.addEventListener("click", function () { lightbox.classList.remove("is-open"); });
    if (prevBtn) prevBtn.addEventListener("click", function () { openLightboxAt(currentIndex - 1); });
    if (nextBtn) nextBtn.addEventListener("click", function () { openLightboxAt(currentIndex + 1); });
    lightbox.addEventListener("click", function (e) {
      if (e.target === lightbox) lightbox.classList.remove("is-open");
    });
    document.addEventListener("keydown", function (e) {
      if (!lightbox.classList.contains("is-open")) return;
      if (e.key === "Escape") lightbox.classList.remove("is-open");
      if (e.key === "ArrowLeft") openLightboxAt(currentIndex - 1);
      if (e.key === "ArrowRight") openLightboxAt(currentIndex + 1);
    });
  }

  /* ---------- Bootstrap client-side validation styling ---------- */
  var forms = document.querySelectorAll(".needs-validation");
  forms.forEach(function (form) {
    form.addEventListener("submit", function (event) {
      if (!form.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
      }
      form.classList.add("was-validated");
    });
  });
});
