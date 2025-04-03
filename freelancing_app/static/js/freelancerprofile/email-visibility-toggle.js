document.addEventListener("DOMContentLoaded", function() {
    const emailField = document.getElementById("email");
    const toggleButton = document.querySelector(".visibility-toggle");
    
    function toggleEmailVisibility() {
        if (emailField.dataset.hidden === "true") {
            emailField.textContent = emailField.dataset.original;
            emailField.dataset.hidden = "false";
            toggleButton.textContent = "Hide";
        } else {
            emailField.dataset.original = emailField.textContent;
            const [username, domain] = emailField.textContent.split("@");
            emailField.textContent = username.slice(0, 4) + "***@" + domain;
            emailField.dataset.hidden = "true";
            toggleButton.textContent = "Reveal";
        }
    }
    
    emailField.dataset.original = emailField.textContent;
    const [username, domain] = emailField.textContent.split("@");
    emailField.textContent = username.slice(0, 4) + "***@" + domain;
    emailField.dataset.hidden = "true";
    
    toggleButton.addEventListener("click", toggleEmailVisibility);
});