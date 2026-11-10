/* Static export: never submit visitor data to a legacy WordPress endpoint. */
document.querySelectorAll('form[data-static-form]').forEach(function (form) {
  var message = document.createElement('p');
  message.setAttribute('role', 'status');
  message.textContent = 'Online form şu anda kullanılamıyor. Başvuru ve bilgi için iletişim sayfasındaki kanalları kullanabilirsiniz.';
  form.prepend(message);
  form.querySelectorAll('button[type="submit"], input[type="submit"]').forEach(function (button) {
    button.disabled = true;
  });
  form.addEventListener('submit', function (event) {
    event.preventDefault();
  });
});
