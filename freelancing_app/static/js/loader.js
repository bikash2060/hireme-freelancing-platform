document.addEventListener('DOMContentLoaded', function () {
  const loadingScreen = document.getElementById('loading-screen');

  // Show loader for form submissions
  const form = document.querySelector('form');
  if (form) {
    form.addEventListener('submit', function () {
      loadingScreen.style.display = 'flex';
    });
  }

  // Show loader for "Click to resend" link
  const resendLink = document.querySelector('.resend-text a');
  if (resendLink) {
    resendLink.addEventListener('click', function (event) {
      loadingScreen.style.display = 'flex';
    });
  }
});
