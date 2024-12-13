document.addEventListener("DOMContentLoaded", () => {
    const messengerIcon = document.getElementById("messenger-icon");
    const messageBox = document.getElementById("message-box");
    const notificationIcon = document.querySelector('.notification-icon');
    const notificationBox = document.querySelector('.notification-box');
    const languageIcon = document.querySelector('.fa-globe');
    const languageBox = document.querySelector('.language-box');
    const profileIcon = document.querySelector('.profile-main .icon');
    const userBox = document.querySelector('.profile-main .user-box');

    const hideAllBoxes = () => {
        if (messageBox) messageBox.style.display = 'none';
        if (notificationBox) notificationBox.style.display = 'none';
        if (languageBox) languageBox.style.display = 'none';
        if (userBox) userBox.style.display = 'none';
    };

    if (messengerIcon && messageBox) {
        messengerIcon.addEventListener("click", function (event) {
            event.stopPropagation();
            if (messageBox.style.display === "block") {
                messageBox.style.display = "none";  
            } else {
                hideAllBoxes();
                messageBox.style.display = "block";  
            }
        });

        document.addEventListener("click", function (event) {
            if (messageBox && !messageBox.contains(event.target) && !messengerIcon.contains(event.target)) {
                messageBox.style.display = "none";
            }
        });
    }

    if (notificationIcon && notificationBox) {
        notificationIcon.addEventListener('click', (e) => {
            e.preventDefault();
            if (notificationBox.style.display === 'block') {
                notificationBox.style.display = 'none';  
            } else {
                hideAllBoxes();
                notificationBox.style.display = 'block';  
            }
        });

        document.addEventListener('click', (e) => {
            if (notificationBox && !notificationIcon.contains(e.target) && !notificationBox.contains(e.target)) {
                notificationBox.style.display = 'none';
            }
        });
    }

    if (languageIcon && languageBox) {
        languageIcon.addEventListener('click', (e) => {
            e.preventDefault();
            if (languageBox.style.display === 'block') {
                languageBox.style.display = 'none';  
            } else {
                hideAllBoxes();
                languageBox.style.display = 'block';  
            }
        });

        document.addEventListener('click', (e) => {
            if (languageBox && !languageIcon.contains(e.target) && !languageBox.contains(e.target)) {
                languageBox.style.display = 'none';
            }
        });
    }

    if (profileIcon && userBox) {
        profileIcon.addEventListener('click', () => {
            if (userBox.style.display === 'block') {
                userBox.style.display = 'none';  
            } else {
                hideAllBoxes();
                userBox.style.display = 'block';  
            }
        });

        document.addEventListener('click', (event) => {
            if (userBox && !event.target.closest('.profile-main')) {
                userBox.style.display = 'none';
            }
        });
    }
});
