document.addEventListener('DOMContentLoaded', function () {
    const alerts = document.querySelectorAll('.alert');

    alerts.forEach(alert => {
        const progressBar = alert.querySelector('.progress');
        const textWidth = alert.querySelector("span").offsetWidth;
        setTimeout(() => {
            progressBar.style.transform = "scaleX(0)";
        }, 50);

        setTimeout(() => {
            alert.classList.add('fade-out');
            setTimeout(() => {
                alert.remove();
            }, 300);
        }, 4000);

        alert.querySelector('.close-message').addEventListener('click', function () {
            alert.classList.add('fade-out');
            setTimeout(() => {
                alert.remove();
            }, 300);
        });
    });
});
