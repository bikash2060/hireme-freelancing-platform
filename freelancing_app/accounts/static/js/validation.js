document.getElementById('togglePassword').addEventListener('click', function() {
  const passwordField = document.getElementById('password');
  const type = passwordField.type === 'password' ? 'text' : 'password';
  passwordField.type = type;
  this.classList.toggle('fa-eye-slash');
});

document.getElementById('toggleConfirmPassword').addEventListener('click', function() {
  const confirmPasswordField = document.getElementById('confirmpassword');
  const type = confirmPasswordField.type === 'password' ? 'text' : 'password';
  confirmPasswordField.type = type;
  this.classList.toggle('fa-eye-slash');
});

