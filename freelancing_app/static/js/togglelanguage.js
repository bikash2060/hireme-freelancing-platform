document.addEventListener('DOMContentLoaded', () => {
    const notificationIcon = document.querySelector('.notification-icon');
    const notificationBox = document.querySelector('.notification-box');
    const languageIcon = document.querySelector('.fa-globe');
    const languageBox = document.querySelector('.language-box');
    const markReadButton = document.querySelector('.mark-read');

    // Toggle notification box visibility
    notificationIcon.addEventListener('click', (e) => {
        e.preventDefault();
        notificationBox.style.display =
            notificationBox.style.display === 'block' ? 'none' : 'block';
    });

    // Close notification box if clicked outside
    document.addEventListener('click', (e) => {
        if (!notificationIcon.contains(e.target) && !notificationBox.contains(e.target)) {
            notificationBox.style.display = 'none';
        }
    });

    // Toggle language box visibility
    languageIcon.addEventListener('click', (e) => {
        e.preventDefault();
        languageBox.style.display =
            languageBox.style.display === 'block' ? 'none' : 'block';
    });

    // Mark all as read functionality
    markReadButton.addEventListener('click', (e) => {
        e.preventDefault();
        const notificationItems = document.querySelectorAll('.notification-item');
        notificationItems.forEach(item => {
            item.style.opacity = '0.5'; // Indicate read state visually
        });
        markReadButton.textContent = 'All notifications are read';
        markReadButton.style.pointerEvents = 'none'; // Disable button
    });

    // Initially hide notification box on page load
    notificationBox.style.display = 'none';
});