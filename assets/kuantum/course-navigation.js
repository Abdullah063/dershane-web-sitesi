/* Category shortcuts open the common course list, matching the requested flow.
   Stop the legacy AJAX handler; let the browser follow the real link. */
document.addEventListener('click', function(event) {
  var link=event.target.closest && event.target.closest('a[data-kuantum-course-category]');
  if (link) event.stopImmediatePropagation();
}, true);
