document.addEventListener("DOMContentLoaded", function () {
  // Handle all toggle password icons
  const toggleIcons = document.querySelectorAll(".toggle_icon, .toggle-icon");

  toggleIcons.forEach((icon) => {
    icon.addEventListener("click", function (e) {
      e.preventDefault();
      const passwordField = this.parentElement.querySelector('input');
      
      // Toggle password visibility
      if (passwordField.type === "password") {
        passwordField.type = "text";
        this.classList.remove("fa-eye");
        this.classList.add("fa-eye-slash");
      } else {
        passwordField.type = "password";
        this.classList.remove("fa-eye-slash");
        this.classList.add("fa-eye");
      }
    });
  });
});
  