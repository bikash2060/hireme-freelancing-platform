// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function () {
    // Select all close icons in the messages
    const closeIcons = document.querySelectorAll('.close-message');
  
    // Add a click event listener to each close icon
    closeIcons.forEach(icon => {
        icon.addEventListener('click', function () {
            // Find the parent message container and hide it
            const alertBox = this.parentElement;
            if (alertBox) {
                alertBox.style.display = 'none';
            }
        });
    });
  });
  