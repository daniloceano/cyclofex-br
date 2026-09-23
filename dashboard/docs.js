(() => {
  const dialog = document.querySelector(".image-lightbox");
  const dialogImage = dialog?.querySelector(".image-lightbox-image");
  const dialogCaption = dialog?.querySelector(".image-lightbox-caption");
  const closeButton = dialog?.querySelector(".image-lightbox-close");

  if (!dialog || !dialogImage || !dialogCaption || !closeButton || typeof dialog.showModal !== "function") {
    return;
  }

  let opener = null;
  let scrollPosition = { left: 0, top: 0 };

  const lockPagePosition = () => {
    scrollPosition = { left: window.scrollX, top: window.scrollY };
    document.body.style.left = `-${scrollPosition.left}px`;
    document.body.style.top = `-${scrollPosition.top}px`;
    document.body.classList.add("lightbox-open");
  };

  const restorePagePosition = () => {
    const previousScrollBehavior = document.documentElement.style.scrollBehavior;
    document.documentElement.style.scrollBehavior = "auto";
    document.body.classList.remove("lightbox-open");
    document.body.style.removeProperty("left");
    document.body.style.removeProperty("top");
    window.scrollTo(scrollPosition.left, scrollPosition.top);
    opener?.focus({ preventScroll: true });
    requestAnimationFrame(() => {
      window.scrollTo(scrollPosition.left, scrollPosition.top);
      document.documentElement.style.scrollBehavior = previousScrollBehavior;
    });
  };

  const openImage = (image) => {
    opener = image;
    lockPagePosition();
    dialogImage.src = image.currentSrc || image.src;
    dialogImage.alt = image.alt || "";

    const sourceCaption = image.closest("figure")?.querySelector("figcaption");
    dialogCaption.replaceChildren();
    if (sourceCaption) {
      dialogCaption.append(...Array.from(sourceCaption.childNodes, (node) => node.cloneNode(true)));
    }

    dialog.showModal();
    closeButton.focus();
  };

  document.querySelectorAll(".document img").forEach((image) => {
    image.classList.add("zoomable");
    image.tabIndex = 0;
    image.setAttribute("role", "button");
    image.setAttribute("aria-haspopup", "dialog");
    image.setAttribute("aria-label", `Ampliar imagem: ${image.alt || "figura"}`);

    image.addEventListener("click", () => openImage(image));
    image.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        openImage(image);
      }
    });
  });

  closeButton.addEventListener("click", () => dialog.close());

  dialog.addEventListener("click", (event) => {
    const bounds = dialog.getBoundingClientRect();
    const outside = event.clientX < bounds.left
      || event.clientX > bounds.right
      || event.clientY < bounds.top
      || event.clientY > bounds.bottom;

    if (outside) {
      dialog.close();
    }
  });

  dialog.addEventListener("close", () => {
    dialogImage.removeAttribute("src");
    dialogImage.alt = "";
    dialogCaption.replaceChildren();
    restorePagePosition();
    opener = null;
  });
})();
