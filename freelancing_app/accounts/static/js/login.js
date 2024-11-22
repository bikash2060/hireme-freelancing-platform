document.getElementById('togglePassword').addEventListener('click', function() {
  const passwordField = document.getElementById('password');
  const type = passwordField.type === 'password' ? 'text' : 'password';
  passwordField.type = type;
  this.classList.toggle('fa-eye-slash');
});

// Function to display a message
document.getElementById('closeMessage').addEventListener('click', function() {
  // Hide the message box
  document.getElementById('messageBox').style.display = 'none';
});