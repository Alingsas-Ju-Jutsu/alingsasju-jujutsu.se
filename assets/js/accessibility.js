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

const navigation = document.querySelector(".site-nav");
const navToggle = document.querySelector(".nav-toggle");
const mobileNavigation = window.matchMedia("(max-width: 900px)");

const setNavigationExpanded = (expanded) => {
  navigation.classList.toggle("is-collapsed", !expanded);
  navToggle.setAttribute("aria-expanded", String(expanded));
};

if (navigation && navToggle) {
  navToggle.hidden = false;
  setNavigationExpanded(!mobileNavigation.matches);
  navToggle.addEventListener("click", () => {
    setNavigationExpanded(navToggle.getAttribute("aria-expanded") !== "true");
  });
  mobileNavigation.addEventListener("change", () => {
    if (navigation.contains(document.activeElement) && mobileNavigation.matches) {
      navToggle.focus();
    }
    setNavigationExpanded(!mobileNavigation.matches);
  });
}

navigation?.addEventListener("keydown", (event) => {
  if (event.key !== "Escape") return;
  const openMenu = event.target.closest("details[open]");
  if (openMenu) {
    openMenu.open = false;
    openMenu.querySelector("summary").focus();
    event.preventDefault();
    event.stopPropagation();
  } else if (navToggle && mobileNavigation.matches) {
    setNavigationExpanded(false);
    navToggle.focus();
    event.preventDefault();
  }
});
