document.addEventListener("DOMContentLoaded", function() {
    const emailField = document.getElementById("email");
    const toggleButton = document.querySelector(".visibility-toggle");
    const emailContainer = document.querySelector(".email-value");
    const emailInfoItem = emailContainer.closest(".info-item");
    
    function toggleEmailVisibility() {
        if (emailField.dataset.hidden === "true") {
            emailField.textContent = emailField.dataset.original;
            emailField.dataset.hidden = "false";
            toggleButton.textContent = "Hide";
            emailContainer.classList.add("revealed");
            emailInfoItem.classList.add("expanded");
        } else {
            emailField.dataset.original = emailField.textContent;
            const [username, domain] = emailField.textContent.split("@");
            emailField.textContent = username.slice(0, 4) + "***@" + domain;
            emailField.dataset.hidden = "true";
            toggleButton.textContent = "Reveal";
            emailContainer.classList.remove("revealed");
            emailInfoItem.classList.remove("expanded");
        }
    }
    
    emailField.dataset.original = emailField.textContent;
    const [username, domain] = emailField.textContent.split("@");
    emailField.textContent = username.slice(0, 4) + "***@" + domain;
    emailField.dataset.hidden = "true";
    
    toggleButton.addEventListener("click", toggleEmailVisibility);
});