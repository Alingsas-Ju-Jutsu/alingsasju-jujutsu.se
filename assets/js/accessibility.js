const hero = document.querySelector(".hero");
const motionToggle = document.querySelector(".hero__motion-toggle");

if (hero && motionToggle) {
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const setPaused = (paused) => {
    hero.classList.toggle("hero--animated", !paused);
    motionToggle.setAttribute("aria-pressed", String(paused));
    motionToggle.textContent = paused ? "Starta bildspelet" : "Pausa bildspelet";
  };

  setPaused(reducedMotion.matches);
  motionToggle.hidden = false;
  motionToggle.addEventListener("click", () => {
    setPaused(motionToggle.getAttribute("aria-pressed") !== "true");
  });
  reducedMotion.addEventListener("change", (event) => setPaused(event.matches));
}

document.querySelector(".site-nav")?.addEventListener("keydown", (event) => {
  if (event.key !== "Escape") return;
  const openMenu = event.target.closest("details[open]");
  if (openMenu) {
    openMenu.open = false;
    openMenu.querySelector("summary").focus();
    event.preventDefault();
    event.stopPropagation();
  }
});
