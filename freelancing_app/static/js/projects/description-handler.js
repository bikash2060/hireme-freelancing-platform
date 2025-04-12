document.addEventListener('DOMContentLoaded', function() {
    const descTextarea = document.getElementById('description');
    const charCount = document.getElementById('desc-char-count');

    if (descTextarea && charCount) {
        charCount.textContent = descTextarea.value.length;

        function updateCount() {
            const length = descTextarea.value.length;
            charCount.textContent = length;
        }

        descTextarea.addEventListener('input', function() {
            if (this.value.length > 500) {
                this.value = this.value.substring(0, 500);
            }
            updateCount();
        });

        descTextarea.addEventListener('paste', function(e) {
            e.preventDefault();
            const pasteData = e.clipboardData.getData('text/plain');
            const remainingChars = 500 - this.value.length;
            
            if (remainingChars <= 0) return;
            
            const truncatedPaste = pasteData.substring(0, remainingChars);
            document.execCommand('insertText', false, truncatedPaste);
            updateCount();
        });

        descTextarea.addEventListener('keydown', function(e) {
            if (this.value.length >= 500 && 
                e.key !== 'Backspace' && 
                e.key !== 'Delete' &&
                !e.ctrlKey && !e.metaKey) {
                e.preventDefault();
            }
        });
    }
});

