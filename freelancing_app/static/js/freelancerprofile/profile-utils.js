document.addEventListener('DOMContentLoaded', function () {
    const bioText = document.getElementById('bio');
    const readMoreLink = document.getElementById('read-more');

    if (!bioText || bioText.textContent.trim() === "" || bioText.textContent.trim() === "None") {
        readMoreLink.style.display = 'none';
        return;
    }

    const lineHeight = parseFloat(getComputedStyle(bioText).lineHeight);
    const maxLines = 4;
    const maxHeight = lineHeight * maxLines;

    if (bioText.scrollHeight > maxHeight) {
        readMoreLink.style.display = 'inline';
        bioText.style.maxHeight = maxHeight + "px";
        bioText.style.overflow = "hidden";

        readMoreLink.addEventListener('click', function () {
            if (bioText.style.maxHeight === "none") {
                bioText.style.maxHeight = maxHeight + "px";
                readMoreLink.textContent = 'Read More';
            } else {
                bioText.style.maxHeight = "none";
                readMoreLink.textContent = 'Read Less';
            }
        });
    }
});

function toggleVisibility(fieldId, button) {
    const field = document.getElementById(fieldId);
    
    if (field.dataset.hidden === "true") {
        field.textContent = field.dataset.original;
        field.dataset.hidden = "false";
        button.textContent = "Hide";
    } else {
        field.dataset.original = field.textContent;
        if (fieldId === "email") {
            const [username, domain] = field.textContent.split("@");
            field.textContent = username.slice(0, 4) + "***@" + domain;
        } else {
            field.textContent = "**********";
        }
        field.dataset.hidden = "true";
        button.textContent = "Reveal";
    }
}

document.addEventListener("DOMContentLoaded", function () {
    toggleVisibility("email", document.querySelector("[onclick=\"toggleVisibility('email', this)\"]"));
    toggleVisibility("phone", document.querySelector("[onclick=\"toggleVisibility('phone', this)\"]"));
});