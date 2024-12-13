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
        messageBox.style.display = 'none';
        notificationBox.style.display = 'none';
        languageBox.style.display = 'none';
        userBox.style.display = 'none';
    };

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
        if (!messageBox.contains(event.target) && !messengerIcon.contains(event.target)) {
            messageBox.style.display = "none";
        }
    });

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
            if (!notificationIcon.contains(e.target) && !notificationBox.contains(e.target)) {
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
            if (!languageIcon.contains(e.target) && !languageBox.contains(e.target)) {
                languageBox.style.display = 'none';
            }
        });
    }

    profileIcon.addEventListener('click', () => {
        if (userBox.style.display === 'block') {
            userBox.style.display = 'none';  
        } else {
            hideAllBoxes();
            userBox.style.display = 'block';  
        }
    });

    document.addEventListener('click', (event) => {
        if (!event.target.closest('.profile-main')) {
            userBox.style.display = 'none';
        }
    });
});
