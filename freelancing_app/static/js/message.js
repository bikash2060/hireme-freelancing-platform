document.addEventListener('DOMContentLoaded', function () {
    const closeIcons = document.querySelectorAll('.close-message');
  
    closeIcons.forEach(icon => {
        icon.addEventListener('click', function () {
            const alertBox = this.parentElement;
            if (alertBox) {
                alertBox.style.display = 'none';
            }
        });
    });
  });