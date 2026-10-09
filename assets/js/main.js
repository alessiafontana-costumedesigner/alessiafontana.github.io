document.documentElement.classList.add("js");

// Fade elements in as they scroll into view.
(() => {
  const els = document.querySelectorAll(".reveal");
  if (!("IntersectionObserver" in window)) {
    els.forEach((el) => el.classList.add("in"));
    return;
  }
  const io = new IntersectionObserver((entries) => {
    for (const e of entries) {
      if (e.isIntersecting) {
        e.target.classList.add("in");
        io.unobserve(e.target);
      }
    }
  }, { rootMargin: "0px 0px -8% 0px" });
  els.forEach((el) => io.observe(el));
})();

// Respect reduced-motion: don't autoplay looping clips.
if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
  document.querySelectorAll("video[autoplay]").forEach((v) => {
    v.pause();
    v.controls = true;
  });
}

// Lightbox: each .gallery is its own sequence.
(() => {
  const galleries = document.querySelectorAll(".gallery");
  if (!galleries.length) return;

  const dlg = document.createElement("dialog");
  dlg.className = "lightbox";
  dlg.setAttribute("aria-label", "Image viewer");
  dlg.innerHTML = `
    <img alt="">
    <button class="lb-btn lb-close" type="button">Close</button>
    <button class="lb-btn lb-prev" type="button" aria-label="Previous image">&larr;</button>
    <button class="lb-btn lb-next" type="button" aria-label="Next image">&rarr;</button>
    <span class="lb-count" aria-live="polite"></span>`;
  document.body.appendChild(dlg);

  const img = dlg.querySelector("img");
  const count = dlg.querySelector(".lb-count");
  let items = [];
  let index = 0;

  function show(i) {
    index = (i + items.length) % items.length;
    const btn = items[index];
    const thumb = btn.querySelector("img");
    img.src = btn.dataset.full;
    img.alt = thumb.alt;
    count.textContent = `${index + 1} / ${items.length}`;
    // Preload neighbours.
    [index + 1, index - 1].forEach((n) => {
      const b = items[(n + items.length) % items.length];
      new Image().src = b.dataset.full;
    });
  }

  galleries.forEach((g) => {
    const buttons = [...g.querySelectorAll("button[data-full]")];
    buttons.forEach((b, i) => {
      b.addEventListener("click", () => {
        items = buttons;
        show(i);
        dlg.showModal();
      });
    });
  });

  dlg.querySelector(".lb-close").addEventListener("click", () => dlg.close());
  dlg.querySelector(".lb-prev").addEventListener("click", () => show(index - 1));
  dlg.querySelector(".lb-next").addEventListener("click", () => show(index + 1));
  dlg.addEventListener("click", (e) => { if (e.target === dlg) dlg.close(); });
  dlg.addEventListener("close", () => img.removeAttribute("src"));
  dlg.addEventListener("keydown", (e) => {
    if (e.key === "ArrowRight") show(index + 1);
    if (e.key === "ArrowLeft") show(index - 1);
  });

  let startX = null;
  dlg.addEventListener("touchstart", (e) => { startX = e.touches[0].clientX; }, { passive: true });
  dlg.addEventListener("touchend", (e) => {
    if (startX === null) return;
    const dx = e.changedTouches[0].clientX - startX;
    if (Math.abs(dx) > 50) show(index + (dx < 0 ? 1 : -1));
    startX = null;
  });
})();
