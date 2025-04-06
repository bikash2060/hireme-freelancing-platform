document.addEventListener('DOMContentLoaded', function() {
  const loadingScreen = document.getElementById('loading-screen');
  let loaderTimeout;
  let isLoaderActive = false;

  function showLoader() {
    if (isLoaderActive) return;    
    loaderTimeout = setTimeout(() => {
      loadingScreen.classList.add('active');
      isLoaderActive = true;
    }, 100); // Only show if operation takes >100ms
  }

  function hideLoader() {
    clearTimeout(loaderTimeout);
    if (isLoaderActive) {
      loadingScreen.classList.remove('active');
      isLoaderActive = false;
    }
  }

  // Initial page load
  showLoader();
  window.addEventListener('load', hideLoader);

  // Form submissions
  const forms = document.querySelectorAll('form');
  forms.forEach(form => {
    form.addEventListener('submit', function(e) {
      showLoader();
      // Let form submit normally
    });
  });

  // Language select
  const languageSelect = document.querySelector('.language-box select');
  if (languageSelect) {
    languageSelect.addEventListener('change', function() {
      showLoader();
      this.form.submit();
    });
  }

  // Resend link
  const resendLink = document.querySelector('.resend-text a');
  if (resendLink) {
    resendLink.addEventListener('click', function(event) {
      event.preventDefault();
      showLoader();
      setTimeout(() => {
        window.location.href = this.href;
      }, 100); // Small delay to ensure loader shows
    });
  }

  // Before unload
  window.addEventListener('beforeunload', function() {
    showLoader();
  });

  // Handle pages loaded from cache (back/forward navigation)
  window.addEventListener('pageshow', function(event) {
    if (event.persisted) {
      hideLoader();
    }
  });
});