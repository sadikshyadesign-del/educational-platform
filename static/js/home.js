(() => {
  const menuButton = document.querySelector("#hp-burger");
  const header = document.querySelector("#hp-header");
  const navigation = document.querySelector("#hp-navigation");

  if (menuButton && header && navigation) {
    const closeMenu = () => {
      header.classList.remove("hp-nav-open");
      menuButton.setAttribute("aria-expanded", "false");
      menuButton.setAttribute("aria-label", "Open navigation menu");
    };

    menuButton.addEventListener("click", () => {
      const isOpen = menuButton.getAttribute("aria-expanded") !== "true";
      header.classList.toggle("hp-nav-open", isOpen);
      menuButton.setAttribute("aria-expanded", String(isOpen));
      menuButton.setAttribute("aria-label", isOpen ? "Close navigation menu" : "Open navigation menu");
    });

    navigation.addEventListener("click", (event) => {
      if (event.target.closest("a")) closeMenu();
    });
    navigation.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        closeMenu();
        menuButton.focus();
      }
    });
    window.addEventListener(
      "resize",
      () => {
        if (window.matchMedia("(min-width: 861px)").matches) closeMenu();
      },
      { passive: true },
    );
  }

  const search = document.querySelector("#resource-search");
  const filterTabs = Array.from(document.querySelectorAll("[data-resource-filter]"));
  const cards = Array.from(document.querySelectorAll("[data-resource-card]"));
  const count = document.querySelector("#resource-count");
  const emptyState = document.querySelector("#resource-empty");

  if (search && filterTabs.length && count && emptyState) {
    let activeCategory = "all";

    const updateResources = () => {
      const query = search.value.trim().toLocaleLowerCase();
      let visibleCount = 0;

      for (const card of cards) {
        const categoryMatches =
          activeCategory === "all" || card.dataset.category === activeCategory;
        const textMatches =
          !query ||
          `${card.dataset.title} ${card.dataset.description}`.toLocaleLowerCase().includes(query);
        const isVisible = categoryMatches && textMatches;
        card.hidden = !isVisible;
        if (isVisible) visibleCount += 1;
      }

      count.textContent = `${visibleCount} items`;
      emptyState.hidden = visibleCount !== 0;
    };

    const selectTab = (selectedTab) => {
      activeCategory = selectedTab.dataset.resourceFilter;
      for (const tab of filterTabs) {
        const isSelected = tab === selectedTab;
        tab.setAttribute("aria-selected", String(isSelected));
        tab.tabIndex = isSelected ? 0 : -1;
      }
      updateResources();
    };

    for (const tab of filterTabs) {
      tab.addEventListener("click", () => selectTab(tab));
    }

    const tablist = filterTabs[0].closest('[role="tablist"]');
    tablist?.addEventListener("keydown", (event) => {
      const currentIndex = filterTabs.indexOf(document.activeElement);
      if (currentIndex < 0) return;

      let nextIndex;
      if (event.key === "ArrowRight") {
        nextIndex = (currentIndex + 1) % filterTabs.length;
      } else if (event.key === "ArrowLeft") {
        nextIndex = (currentIndex - 1 + filterTabs.length) % filterTabs.length;
      } else if (event.key === "Home") {
        nextIndex = 0;
      } else if (event.key === "End") {
        nextIndex = filterTabs.length - 1;
      } else {
        return;
      }

      event.preventDefault();
      filterTabs[nextIndex].focus();
      selectTab(filterTabs[nextIndex]);
    });

    search.addEventListener("input", updateResources);
    updateResources();
  }

  const hero = document.querySelector("#home-hero");
  const trail = hero?.querySelector(".home-image-trail");
  const canTrail =
    window.matchMedia("(hover: hover) and (pointer: fine)").matches &&
    !window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (!hero || !trail || !canTrail) return;

  const assetPath = trail.dataset.trailPath;
  const images = ["equation.svg", "geometry.svg", "notes.svg", "book.svg", "chalkboard.svg"];
  const activeNodes = [];
  let lastSpawnedAt = 0;
  let lastPointer = null;

  const handlePointerMove = (event) => {
    if (event.pointerType !== "mouse") return;

    const bounds = hero.getBoundingClientRect();
    const point = { x: event.clientX - bounds.left, y: event.clientY - bounds.top };
    if (lastPointer) {
      const distance = Math.hypot(point.x - lastPointer.x, point.y - lastPointer.y);
      if (distance < 70) return;
    }

    const now = performance.now();
    if (now - lastSpawnedAt < 90) return;

    lastPointer = point;
    lastSpawnedAt = now;
    spawnImage(point);
  };

  const spawnImage = (point) => {
    const image = document.createElement("img");
    const rotation = Math.random() * 14 - 7;
    const drift = Math.random() * 40 - 20;
    const source = images[Math.floor(Math.random() * images.length)];
    image.className = "home-trail-image";
    image.src = `${assetPath}${source}`;
    image.alt = "";
    image.draggable = false;
    image.width = 160;
    image.height = 200;
    trail.append(image);
    activeNodes.push(image);

    while (activeNodes.length > 10) {
      activeNodes.shift().remove();
    }

    const animation = image.animate(
      [
        {
          opacity: 0,
          transform: `translate(${point.x}px, ${point.y}px) translate(-50%, -50%) scale(0.7) rotate(${rotation - 4}deg)`,
          offset: 0,
        },
        {
          opacity: 0.92,
          transform: `translate(${point.x}px, ${point.y}px) translate(-50%, -50%) scale(1.03) rotate(${rotation}deg)`,
          offset: 0.25,
        },
        {
          opacity: 0,
          transform: `translate(${point.x + drift}px, ${point.y - 24}px) translate(-50%, -50%) scale(0.96) rotate(${rotation + 3}deg)`,
          offset: 1,
        },
      ],
      {
        duration: 1100,
        easing: "cubic-bezier(0.22, 1, 0.36, 1)",
        fill: "forwards",
      },
    );
    animation.onfinish = () => {
      image.remove();
      const index = activeNodes.indexOf(image);
      if (index !== -1) activeNodes.splice(index, 1);
    };
  };

  hero.addEventListener("pointermove", handlePointerMove);
  window.addEventListener(
    "pagehide",
    () => {
      hero.removeEventListener("pointermove", handlePointerMove);
      for (const image of activeNodes) {
        image.getAnimations().forEach((animation) => animation.cancel());
        image.remove();
      }
      activeNodes.length = 0;
    },
    { once: true },
  );
})();
