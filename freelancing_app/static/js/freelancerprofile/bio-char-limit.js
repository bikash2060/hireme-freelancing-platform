document.addEventListener('DOMContentLoaded', function() {
    const bioTextarea = document.getElementById('bio');
    const charCount = document.getElementById('char-count');

    if (bioTextarea && charCount) {
        charCount.textContent = bioTextarea.value.length;

        function updateCount() {
            const length = bioTextarea.value.length;
            charCount.textContent = length;
        }

        bioTextarea.addEventListener('input', function() {
            if (this.value.length > 500) {
                this.value = this.value.substring(0, 500);
            }
            updateCount();
        });

        bioTextarea.addEventListener('paste', function(e) {
            e.preventDefault();
            const pasteData = e.clipboardData.getData('text/plain');
            const remainingChars = 500 - this.value.length;
            
            if (remainingChars <= 0) return;
            
            const truncatedPaste = pasteData.substring(0, remainingChars);
            document.execCommand('insertText', false, truncatedPaste);
            updateCount();
        });

        bioTextarea.addEventListener('keydown', function(e) {
            if (this.value.length >= 500 && 
                e.key !== 'Backspace' && 
                e.key !== 'Delete' &&
                !e.ctrlKey && !e.metaKey) {
                e.preventDefault();
            }
        });
    }
});