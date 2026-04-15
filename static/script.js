function debounce(fn, delay) {
  let timer;
  return function (...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), delay);
  };
}

function showToast(msg, type = "info") {
  const toast = document.getElementById("toast");
  if (!toast) return;
  toast.textContent = msg;
  toast.className = `toast show ${type}`;
  clearTimeout(toast._timer);
  toast._timer = setTimeout(() => {
    toast.classList.remove("show");
  }, 3200);
}

function formatNum(n) {
  if (n >= 1000000) return `${(n / 1000000).toFixed(1)}m`;
  if (n >= 1000) return `${(n / 1000).toFixed(1)}k`;
  return `${n}`;
}

function animateCount(el, target, duration = 900, decimals = 0) {
  if (!el) return;
  const start = Number(el.dataset.value || 0);
  const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (prefersReduced) {
    el.textContent = Number(target).toFixed(decimals);
    el.dataset.value = target;
    return;
  }

  const startTime = performance.now();
  function tick(now) {
    const progress = Math.min((now - startTime) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const current = start + (target - start) * eased;
    el.textContent = Number(current).toFixed(decimals);
    if (progress < 1) {
      requestAnimationFrame(tick);
    } else {
      el.dataset.value = target;
    }
  }
  requestAnimationFrame(tick);
}

function highlightNav() {
  const path = window.location.pathname;
  document.querySelectorAll(".nav-link").forEach((link) => {
    const href = link.getAttribute("href");
    link.classList.toggle(
      "active",
      href === path || (path !== "/" && href !== "/" && path.startsWith(href))
    );
  });
}

function isPerformanceLite() {
  const lowMemory = typeof navigator.deviceMemory === "number" && navigator.deviceMemory <= 4;
  const lowCpu = typeof navigator.hardwareConcurrency === "number" && navigator.hardwareConcurrency <= 4;
  return window.innerWidth <= 1100 || lowMemory || lowCpu;
}

function setupPerformanceMode() {
  const apply = () => {
    document.body.classList.toggle("perf-lite", isPerformanceLite());
  };

  apply();
  window.addEventListener("resize", apply);
}

function setupViewportProgress() {
  const bar = document.getElementById("viewport-progress-bar");
  if (!bar) return;

  const update = () => {
    const max = document.documentElement.scrollHeight - window.innerHeight;
    const pct = max > 0 ? (window.scrollY / max) * 100 : 0;
    bar.style.width = `${Math.min(Math.max(pct, 0), 100)}%`;
  };

  update();
  window.addEventListener("scroll", update, { passive: true });
  window.addEventListener("resize", update);
}

function setupRevealAnimations() {
  const targets = document.querySelectorAll("[data-reveal]");
  if (!targets.length) return;

  const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (prefersReduced || !("IntersectionObserver" in window)) {
    targets.forEach((el) => {
      el.style.opacity = "1";
      el.style.transform = "none";
    });
    return;
  }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      const el = entry.target;
      const delay = Number(el.dataset.revealDelay || 0);
      setTimeout(() => {
        el.style.opacity = "1";
        el.style.transform = "translateY(0)";
      }, delay);
      observer.unobserve(el);
    });
  }, { threshold: 0.14 });

  targets.forEach((el) => {
    el.style.transition = "opacity 0.7s ease, transform 0.7s ease";
    observer.observe(el);
  });
}

function setupTilt() {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches || document.body.classList.contains("perf-lite")) return;
  document.querySelectorAll("[data-tilt]").forEach((el) => {
    el.addEventListener("mousemove", (event) => {
      if (window.innerWidth < 900) return;
      const rect = el.getBoundingClientRect();
      const x = (event.clientX - rect.left) / rect.width - 0.5;
      const y = (event.clientY - rect.top) / rect.height - 0.5;
      el.style.transform =
        `perspective(1200px) rotateX(${(-y * 6).toFixed(2)}deg) rotateY(${(x * 8).toFixed(2)}deg) translateY(-3px)`;
    });
    el.addEventListener("mouseleave", () => {
      el.style.transform = "";
    });
  });
}

function setupMagneticButtons() {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches || document.body.classList.contains("perf-lite")) return;

  document.querySelectorAll("[data-magnetic]").forEach((el) => {
    el.addEventListener("mousemove", (event) => {
      if (window.innerWidth < 900) return;
      const rect = el.getBoundingClientRect();
      const x = (event.clientX - rect.left) / rect.width - 0.5;
      const y = (event.clientY - rect.top) / rect.height - 0.5;
      el.style.transform = `translate3d(${(x * 12).toFixed(1)}px, ${(y * 10).toFixed(1)}px, 0)`;
    });

    el.addEventListener("mouseleave", () => {
      el.style.transform = "";
    });
  });
}

function setupHeroScene() {
  const visual = document.querySelector("[data-hero-visual]");
  if (!visual || window.matchMedia("(prefers-reduced-motion: reduce)").matches || document.body.classList.contains("perf-lite")) return;

  visual.addEventListener("mousemove", (event) => {
    if (window.innerWidth < 900) return;
    const rect = visual.getBoundingClientRect();
    const x = (event.clientX - rect.left) / rect.width - 0.5;
    const y = (event.clientY - rect.top) / rect.height - 0.5;
    visual.style.transform =
      `perspective(1400px) rotateX(${(-y * 8).toFixed(2)}deg) rotateY(${(x * 10).toFixed(2)}deg)`;
  });
  visual.addEventListener("mouseleave", () => {
    visual.style.transform = "";
  });
}

function setupSignalScenes() {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches || document.body.classList.contains("perf-lite")) return;

  document.querySelectorAll("[data-signal-scene]").forEach((scene) => {
    const labels = scene.querySelectorAll(".signal-scene__label");

    scene.addEventListener("mousemove", (event) => {
      if (window.innerWidth < 900) return;
      const rect = scene.getBoundingClientRect();
      const x = (event.clientX - rect.left) / rect.width - 0.5;
      const y = (event.clientY - rect.top) / rect.height - 0.5;

      scene.style.setProperty("--signal-rotate-x", `${(-y * 7).toFixed(2)}deg`);
      scene.style.setProperty("--signal-rotate-y", `${(x * 9).toFixed(2)}deg`);
      scene.style.setProperty("--signal-shift-x", `${(x * 4).toFixed(1)}px`);
      scene.style.setProperty("--signal-shift-y", `${(y * -4).toFixed(1)}px`);

      labels.forEach((label, index) => {
        const dx = x * (index === 1 ? -14 : 14);
        const dy = y * (index === 2 ? 16 : -12);
        label.style.transform = `translate3d(${dx.toFixed(1)}px, ${dy.toFixed(1)}px, 0)`;
      });
    });

    scene.addEventListener("mouseleave", () => {
      scene.style.setProperty("--signal-rotate-x", "0deg");
      scene.style.setProperty("--signal-rotate-y", "0deg");
      scene.style.setProperty("--signal-shift-x", "0px");
      scene.style.setProperty("--signal-shift-y", "0px");
      labels.forEach((label) => {
        label.style.transform = "";
      });
    });
  });
}

function setupStoryModelCursor() {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches || document.body.classList.contains("perf-lite")) return;

  document.querySelectorAll("[data-story-pin]").forEach((section) => {
    const stage = section.querySelector(".story-stage__layers");
    const core = section.querySelector(".story-model__core");
    const rings = section.querySelectorAll(".story-model__ring");
    const badges = section.querySelectorAll(".stage-badge");
    const shadow = section.querySelector(".story-model__shadow");
    if (!stage || !core || !rings.length) return;

    const useGsap = Boolean(window.gsap);
    let resetTimer = null;

    const moveWithGsap = (target, vars) => {
      if (!target) return;
      if (useGsap) {
        gsap.to(target, { ...vars, duration: 0.45, ease: "power3.out", overwrite: true });
      } else {
        const translate = vars.x || vars.y ? ` translate3d(${vars.x || 0}px, ${vars.y || 0}px, 0)` : "";
        target.style.transform = `rotateX(${vars.rotateX || 0}deg) rotateY(${vars.rotateY || 0}deg) rotateZ(${vars.rotateZ || 0}deg)${translate}`;
      }
    };

    stage.addEventListener("mousemove", (event) => {
      if (window.innerWidth < 900) return;
      clearTimeout(resetTimer);
      const rect = stage.getBoundingClientRect();
      const x = (event.clientX - rect.left) / rect.width - 0.5;
      const y = (event.clientY - rect.top) / rect.height - 0.5;

      moveWithGsap(core, {
        rotateY: x * 30,
        rotateX: -y * 24,
        x: x * 18,
        y: y * 14
      });

      rings.forEach((ring, index) => {
        moveWithGsap(ring, {
          rotateY: x * (index === 0 ? 34 : index === 1 ? -28 : 20),
          rotateX: -y * (index === 0 ? 18 : index === 1 ? 26 : -16),
          rotateZ: x * (index === 0 ? 24 : index === 1 ? -18 : 12),
          x: x * (index === 0 ? 10 : index === 1 ? -8 : 6),
          y: y * (index === 0 ? 8 : index === 1 ? -10 : 6)
        });
      });

      badges.forEach((badge, index) => {
        moveWithGsap(badge, {
          rotateY: x * (index === 1 ? -10 : 10),
          rotateX: -y * 6,
          x: x * (index === 0 ? 18 : index === 1 ? -18 : 12),
          y: y * (index === 0 ? 12 : index === 1 ? -10 : 16)
        });
      });

      moveWithGsap(shadow, {
        x: x * 26,
        y: y * 10
      });
    });

    stage.addEventListener("mouseleave", () => {
      resetTimer = setTimeout(() => {
        moveWithGsap(core, { rotateY: 0, rotateX: 0, x: 0, y: 0 });
        rings.forEach((ring) => moveWithGsap(ring, { rotateY: 0, rotateX: 0, rotateZ: 0, x: 0, y: 0 }));
        badges.forEach((badge) => moveWithGsap(badge, { rotateY: 0, rotateX: 0, x: 0, y: 0 }));
        moveWithGsap(shadow, { x: 0, y: 0 });
      }, 20);
    });
  });
}

function setupParallax() {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches || document.body.classList.contains("perf-lite")) return;
  const layers = document.querySelectorAll("[data-depth]");
  if (!layers.length) return;

  let ticking = false;
  const update = () => {
    layers.forEach((layer) => {
      const depth = Number(layer.dataset.depth || 0.08);
      const rect = layer.parentElement?.getBoundingClientRect() || layer.getBoundingClientRect();
      const offset = (window.innerHeight * 0.5 - rect.top) * depth;
      layer.style.transform = `translate3d(0, ${offset.toFixed(1)}px, 0)`;
    });
    ticking = false;
  };

  update();
  window.addEventListener("scroll", () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(update);
  }, { passive: true });
  window.addEventListener("resize", update);
}

function setupGsapScenes() {
  if (!window.gsap || !window.ScrollTrigger || window.matchMedia("(prefers-reduced-motion: reduce)").matches || document.body.classList.contains("perf-lite")) return;
  gsap.registerPlugin(ScrollTrigger);

  document.querySelectorAll("[data-story-pin]").forEach((section) => {
    const layer = section.querySelector(".story-stage__layers");
    const model = section.querySelector(".story-model__core");
    const rings = section.querySelectorAll(".story-model__ring");
    const badges = section.querySelectorAll(".stage-badge");
    if (!layer) return;
    gsap.to(layer, {
      rotateX: 4,
      rotateY: -8,
      scale: 1.02,
      scrollTrigger: {
        trigger: section,
        start: "top center",
        end: "bottom top",
        scrub: 1
      }
    });

    if (model) {
      gsap.timeline({
        scrollTrigger: {
          trigger: section,
          start: "top 78%",
          end: "bottom top",
          scrub: 1.2
        }
      })
        .to(model, {
          rotateY: 180,
          rotateX: -18,
          z: 70,
          ease: "none"
        }, 0)
        .to(rings, {
          rotateZ: (index) => index % 2 === 0 ? 180 : -180,
          rotateX: (index) => index === 0 ? 82 : index === 1 ? 24 : -12,
          ease: "none",
          stagger: 0.02
        }, 0)
        .to(badges, {
          y: (index) => index === 1 ? -18 : index === 2 ? 14 : -8,
          z: 40,
          ease: "none",
          stagger: 0.03
        }, 0);
    }
  });

  document.querySelectorAll("[data-scroll-card]").forEach((card, index) => {
    gsap.fromTo(card,
      { y: 36, opacity: 0, rotateX: 10 },
      {
        y: 0,
        opacity: 1,
        rotateX: 0,
        duration: 0.8,
        delay: index * 0.06,
        ease: "power3.out",
        scrollTrigger: {
          trigger: card,
          start: "top 82%"
        }
      }
    );
  });
}

document.addEventListener("DOMContentLoaded", () => {
  setupPerformanceMode();
  highlightNav();
  setupViewportProgress();
  setupRevealAnimations();
  setupTilt();
  setupMagneticButtons();
  setupHeroScene();
  setupSignalScenes();
  setupStoryModelCursor();
  setupParallax();
  setupGsapScenes();
});
