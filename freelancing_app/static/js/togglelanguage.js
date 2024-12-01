function toggleLanguage(button) {
    // Toggle the "on" class
    button.classList.toggle("on");

    // Change the icon and text
    const icon = button.querySelector("i");
    const text = button.querySelector(".language-text");

    if (button.classList.contains("on")) {
        // When "on", show "Nepali" with "fa-toggle-on"
        icon.classList.replace("fa-toggle-off", "fa-toggle-on");
        text.textContent = "Nepali";
    } else {
        // When "off", show "English" with "fa-toggle-off"
        icon.classList.replace("fa-toggle-on", "fa-toggle-off");
        text.textContent = "English";
    }
}
