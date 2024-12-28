function formatEmail() {
    const emailElement = document.getElementById('email');
    const email = emailElement.textContent.trim(); 

    const [username, domain] = email.split('@');

    const formattedUsername = username.slice(0, 4) + '***';

    const formattedEmail = formattedUsername + '@' + domain;

    emailElement.textContent = formattedEmail;
}

window.onload = formatEmail;

document.addEventListener('DOMContentLoaded', function () {
    const bioText = document.getElementById('bio');
    const readMoreLink = document.getElementById('read-more');

    if (!bioText || bioText.textContent.trim() === "") {
        readMoreLink.style.display = 'none';
    } else {
        readMoreLink.addEventListener('click', function () {
            if (bioText.style.maxHeight === 'none') {
                bioText.style.maxHeight = '6.4em';  
                readMoreLink.textContent = 'Read More';  
            } else {
                bioText.style.maxHeight = 'none';  
                readMoreLink.textContent = 'Read Less';  
            }
        });
    }
});


