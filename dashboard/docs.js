(() => {
  const dialog = document.querySelector(".image-lightbox");
  const dialogImage = dialog?.querySelector(".image-lightbox-image");
  const dialogCaption = dialog?.querySelector(".image-lightbox-caption");
  const closeButton = dialog?.querySelector(".image-lightbox-close");

  if (!dialog || !dialogImage || !dialogCaption || !closeButton || typeof dialog.showModal !== "function") {
    return;
  }

  let opener = null;

  const openImage = (image) => {
    opener = image;
    dialogImage.src = image.currentSrc || image.src;
    dialogImage.alt = image.alt || "";

    const sourceCaption = image.closest("figure")?.querySelector("figcaption");
    dialogCaption.replaceChildren();
    if (sourceCaption) {
      dialogCaption.append(...Array.from(sourceCaption.childNodes, (node) => node.cloneNode(true)));
    }

    document.body.classList.add("lightbox-open");
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
    document.body.classList.remove("lightbox-open");
    dialogImage.removeAttribute("src");
    dialogImage.alt = "";
    dialogCaption.replaceChildren();
    opener?.focus();
    opener = null;
  });
})();
