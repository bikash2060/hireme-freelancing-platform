document.addEventListener('DOMContentLoaded', function () {
  const loadingScreen = document.getElementById('loading-screen');

  loadingScreen.style.display = 'flex';

  window.addEventListener('load', function () {
    loadingScreen.style.display = 'none'; 
  });

  const forms = document.querySelectorAll('form');
  forms.forEach(form => {
    form.addEventListener('submit', function () {
      loadingScreen.style.display = 'flex';
    });
  });

  const languageSelect = document.querySelector('.language-box select');
  if (languageSelect) {
    languageSelect.addEventListener('change', function () {
      loadingScreen.style.display = 'flex';
      this.form.submit();
    });
  }

  const resendLink = document.querySelector('.resend-text a');
  if (resendLink) {
    resendLink.addEventListener('click', function (event) {
      event.preventDefault();
      loadingScreen.style.display = 'flex';
      setTimeout(() => {
        window.location.href = this.href;
      }, 500);
    });
  }

  window.addEventListener('beforeunload', function () {
    loadingScreen.style.display = 'flex';
  });
});
