document.addEventListener("DOMContentLoaded", () => {
    const messengerIcon = document.getElementById("messenger-icon");
    const messageBox = document.getElementById("message-box");
    const notificationIcon = document.querySelector('.notification-icon');
    const notificationBox = document.querySelector('.notification-box');
    const languageIcon = document.querySelector('.fa-globe');
    const languageBox = document.querySelector('.language-box');
    const profileTrigger = document.querySelector('.profile-trigger');
    const profileMain = document.querySelector('.profile-main');
    const profileDropdown = document.querySelector('.profile-dropdown');

    let currentOpenDropdown = null;

    const hideAllDropdowns = () => {
        if (messageBox) messageBox.style.display = 'none';
        if (notificationBox) notificationBox.style.display = 'none';
        if (languageBox) languageBox.style.display = 'none';
        if (profileDropdown) profileDropdown.style.display = 'none';
        if (profileMain) profileMain.classList.remove('active');
        currentOpenDropdown = null;
    };

    const setupIconToggle = (icon, dropdown) => {
        if (!icon || !dropdown) return;

        icon.addEventListener('click', (e) => {
            e.stopPropagation();
            
            if (currentOpenDropdown === dropdown) {
                hideAllDropdowns();
                return;
            }

            hideAllDropdowns();
            
            if (dropdown === profileDropdown) {
                profileMain.classList.add('active');
                profileDropdown.style.display = 'block';
            } else {
                dropdown.style.display = 'block';
            }
            
            currentOpenDropdown = dropdown;
        });
    };

    setupIconToggle(messengerIcon, messageBox);
    setupIconToggle(notificationIcon, notificationBox);
    setupIconToggle(languageIcon, languageBox);
    setupIconToggle(profileTrigger, profileDropdown);

    document.addEventListener('click', (e) => {
        if (!e.target.closest('.notification-icon') && !e.target.closest('.notification-box')) {
            notificationBox.style.display = 'none';
        }
        if (!e.target.closest('#messenger-icon') && !e.target.closest('#message-box')) {
            messageBox.style.display = 'none';
        }
        if (!e.target.closest('.fa-globe') && !e.target.closest('.language-box')) {
            languageBox.style.display = 'none';
        }
        if (!e.target.closest('.profile-trigger') && !e.target.closest('.profile-dropdown')) {
            profileDropdown.style.display = 'none';
            profileMain.classList.remove('active');
        }
        
        if (messageBox.style.display === 'block') {
            currentOpenDropdown = messageBox;
        } else if (notificationBox.style.display === 'block') {
            currentOpenDropdown = notificationBox;
        } else if (languageBox.style.display === 'block') {
            currentOpenDropdown = languageBox;
        } else if (profileDropdown.style.display === 'block') {
            currentOpenDropdown = profileDropdown;
        } else {
            currentOpenDropdown = null;
        }
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            hideAllDropdowns();
        }
    });

    const darkModeToggle = document.querySelector('.toggle-switch input');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('change', (e) => {
            document.body.classList.toggle('dark-mode', e.target.checked);
            localStorage.setItem('darkMode', e.target.checked);
        });

        if (localStorage.getItem('darkMode') === 'true') {
            document.body.classList.add('dark-mode');
            darkModeToggle.checked = true;
        }
    }
});