/* Elementor labels modal widgets as documents; aria-modal requires a dialog. */
(function () {
  function repair(node) {
    if (node.nodeType !== 1) return;
    if (node.matches('[aria-modal="true"][role="document"]')) {
      node.setAttribute('role', 'dialog');
      node.setAttribute('aria-label', 'Kuantum Sayısal Akademi duyurusu');
    }
    node.querySelectorAll('[aria-modal="true"][role="document"]').forEach(repair);
  }
  repair(document.body);
  new MutationObserver(function (changes) {
    changes.forEach(function (change) {
      if (change.type === 'attributes') repair(change.target);
      change.addedNodes.forEach(repair);
    });
  }).observe(document.body, {subtree:true, childList:true, attributes:true, attributeFilter:['aria-modal','role']});
}());
