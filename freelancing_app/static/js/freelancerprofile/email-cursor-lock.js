document.addEventListener('DOMContentLoaded', function() {
    const emailInput = document.getElementById('email');
    emailInput.addEventListener('mouseenter', function() {
        this.style.cursor = 'not-allowed';
    });
});