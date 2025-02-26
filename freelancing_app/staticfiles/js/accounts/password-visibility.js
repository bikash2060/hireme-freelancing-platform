document.addEventListener("DOMContentLoaded", function () {
    const toggleIcons = document.querySelectorAll(".fa-eye");
  
    toggleIcons.forEach((icon) => {
      icon.addEventListener("click", function () {
        const passwordField = this.previousElementSibling;
        const type = passwordField.type === "password" ? "text" : "password";
        passwordField.type = type;
        this.className = type === "password" ? "fa fa-eye" : "fa fa-eye-slash";
      });
    });
  });
  