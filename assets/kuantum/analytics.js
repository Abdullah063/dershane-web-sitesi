(function () {
  const siteDomain = 'kuantumsayisalakademi.com';
  if (![siteDomain, 'www.' + siteDomain].includes(location.hostname)) return;

  const id = document.currentScript.dataset.measurementId;
  const storageKey = 'kuantum.analytics.consent';
  const panel = document.getElementById('analytics-consent');
  const preferences = document.getElementById('analytics-preferences');
  let started = false;

  function readChoice() {
    try { return localStorage.getItem(storageKey); }
    catch { return null; }
  }

  function gtag() { window.dataLayer.push(arguments); }

  function startAnalytics() {
    if (started) return;
    started = true;
    window.dataLayer = window.dataLayer || [];
    gtag('consent', 'default', {
      analytics_storage: 'granted',
      ad_storage: 'denied',
      ad_user_data: 'denied',
      ad_personalization: 'denied'
    });
    gtag('js', new Date());
    gtag('config', id, {allow_google_signals: false, allow_ad_personalization_signals: false});
    const tag = document.createElement('script');
    tag.async = true;
    tag.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(id);
    document.head.appendChild(tag);
  }

  function applyChoice(choice) {
    panel.hidden = choice === 'granted' || choice === 'denied';
    if (choice === 'granted') {
      startAnalytics();
    } else if (started) {
      window['ga-disable-' + id] = true;
      for (const name of ['_ga', '_ga_' + id.slice(2)]) {
        const expired = name + '=; Max-Age=0; Path=/';
        document.cookie = expired;
        document.cookie = expired + '; Domain=' + siteDomain;
      }
      // Unload the running tag, including its enhanced measurement listeners.
      location.reload();
    }
  }

  preferences.hidden = false;
  preferences.addEventListener('click', function () {
    panel.hidden = false;
    panel.querySelector('button').focus();
  });
  panel.querySelectorAll('button[data-choice]').forEach(function (button) {
    button.addEventListener('click', function () {
      const choice = button.dataset.choice;
      try { localStorage.setItem(storageKey, choice); }
      catch { /* The visitor's choice still applies to this page. */ }
      applyChoice(choice);
    });
  });
  window.addEventListener('storage', function (event) {
    if (event.key === storageKey || event.key === null) applyChoice(readChoice());
  });
  window.addEventListener('pageshow', function (event) {
    if (event.persisted) applyChoice(readChoice());
  });
  applyChoice(readChoice());
})();
