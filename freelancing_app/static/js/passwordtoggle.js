// Wait until the DOM is fully loaded
document.addEventListener("DOMContentLoaded", function () {
    // Get all password toggle icons
    const toggleIcons = document.querySelectorAll(".fa-eye");
  
    // Loop through each icon and add a click event listener
    toggleIcons.forEach((icon) => {
      icon.addEventListener("click", function () {
        // Find the related password input field
        const passwordField = this.previousElementSibling;
  
        // Toggle the type attribute (password <-> text)
        const type = passwordField.type === "password" ? "text" : "password";
        passwordField.type = type;
  
        // Toggle the icon class (fa-eye <-> fa-eye-slash)
        this.className = type === "password" ? "fa fa-eye" : "fa fa-eye-slash";
      });
    });
  });

