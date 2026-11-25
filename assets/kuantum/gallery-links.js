/* Elementor shares each slide using the absolute image URL of this deployment. */
document.querySelectorAll('a[data-kuantum-lightbox-id]').forEach(function (link) {
  var slide = {
    id: Number(link.dataset.kuantumLightboxId),
    url: link.href,
    slideshow: link.dataset.elementorLightboxSlideshow
  };
  link.dataset.eActionHash = '#elementor-action' + encodeURIComponent(':action=lightbox&settings=' + btoa(JSON.stringify(slide)));
});
