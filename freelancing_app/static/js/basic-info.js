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

document.addEventListener("DOMContentLoaded", function() {
    const editLink = document.querySelector('.edit-link');
    const overlay = document.getElementById('overlay');
    const editProfileForm = document.getElementById('edit-profile-form');
    const cancelBtn = document.getElementById('cancel-edit');
    
    // Show overlay and form when edit button is clicked
    editLink.addEventListener('click', function(event) {
        event.preventDefault();
        overlay.style.display = 'block'; // Show overlay
        editProfileForm.style.display = 'block'; // Show form
        document.body.classList.add('no-scroll'); // Disable scrolling
    });


    // If there are any messages, ensure the form remains visible
    const messageContainer = document.querySelector('.alert-container');
    if (messageContainer) {
        overlay.style.display = 'block'; // Show overlay
        editProfileForm.style.display = 'block'; // Show form
        document.body.classList.add('no-scroll'); // Disable scrolling
    }
});


