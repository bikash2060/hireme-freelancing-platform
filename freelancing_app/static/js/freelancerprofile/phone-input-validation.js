document.addEventListener('DOMContentLoaded', function() {
    const phoneInput = document.getElementById('phone_number');
    if (phoneInput) {
        phoneInput.addEventListener('input', function(e) {
            this.value = this.value.replace(/\D/g, '');
            
            if (this.value.length > 10) {
                this.value = this.value.slice(0, 10);
            }
        });

        phoneInput.addEventListener('paste', function(e) {
            e.preventDefault();
            const pasteData = e.clipboardData.getData('text/plain').replace(/\D/g, '');
            const remainingDigits = 10 - this.value.length;
            const truncatedPaste = pasteData.substring(0, remainingDigits);
            document.execCommand('insertText', false, truncatedPaste);
        });

        const form = phoneInput.closest('form');
        if (form) {
            form.addEventListener('submit', function(e) {
                if (phoneInput.value.length !== 10) {
                    e.preventDefault();
                    phoneInput.focus();
                }
            });
        }
    }
});