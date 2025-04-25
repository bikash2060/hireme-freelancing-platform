document.addEventListener('DOMContentLoaded', function () {
    const jobDescriptionTextarea = document.getElementById('job_description');
    const descCharCount = document.getElementById('desc-char-count');
    const maxChars = 500;

    if (jobDescriptionTextarea && descCharCount) {
        const updateDescCount = () => {
            const length = jobDescriptionTextarea.value.length;
            descCharCount.textContent = length;

            if (length >= maxChars) {
                descCharCount.style.color = '#e74c3c'; 
            } else if (length > maxChars * 0.9) {
                descCharCount.style.color = '#f39c12'; 
            } else {
                descCharCount.style.color = '#2ecc71';
            }
        };

        updateDescCount();

        jobDescriptionTextarea.addEventListener('input', function () {
            if (this.value.length > maxChars) {
                this.value = this.value.substring(0, maxChars);
            }
            updateDescCount();
        });

        jobDescriptionTextarea.addEventListener('paste', function (e) {
            e.preventDefault();
            const pasteData = e.clipboardData.getData('text/plain');
            const remainingChars = maxChars - this.value.length;
            if (remainingChars <= 0) return;

            const truncatedPaste = pasteData.substring(0, remainingChars);
            document.execCommand('insertText', false, truncatedPaste);
            updateDescCount();
        });

        jobDescriptionTextarea.addEventListener('keydown', function (e) {
            const keysAllowed = ['Backspace', 'Delete'];
            if (
                this.value.length >= maxChars &&
                !keysAllowed.includes(e.key) &&
                !e.ctrlKey &&
                !e.metaKey
            ) {
                e.preventDefault();
            }
        });
    }
});
