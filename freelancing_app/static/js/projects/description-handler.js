document.addEventListener('DOMContentLoaded', function() {
    // Function to create character counter handler
    function createCharacterCounter(textareaId, counterId, maxLength) {
        const textarea = document.getElementById(textareaId);
        const charCount = document.getElementById(counterId);

        if (textarea && charCount) {
            charCount.textContent = textarea.value.length;

            function updateCount() {
                const length = textarea.value.length;
                charCount.textContent = length;
            }

            textarea.addEventListener('input', function() {
                if (this.value.length > maxLength) {
                    this.value = this.value.substring(0, maxLength);
                }
                updateCount();
            });

            textarea.addEventListener('paste', function(e) {
                e.preventDefault();
                const pasteData = e.clipboardData.getData('text/plain');
                const remainingChars = maxLength - this.value.length;
                
                if (remainingChars <= 0) return;
                
                const truncatedPaste = pasteData.substring(0, remainingChars);
                document.execCommand('insertText', false, truncatedPaste);
                updateCount();
            });

            textarea.addEventListener('keydown', function(e) {
                if (this.value.length >= maxLength && 
                    e.key !== 'Backspace' && 
                    e.key !== 'Delete' &&
                    !e.ctrlKey && !e.metaKey) {
                    e.preventDefault();
                }
            });
        }
    }

    // Initialize character counters for both textareas
    createCharacterCounter('description', 'desc-char-count', 500);
    createCharacterCounter('additional_info', 'additional-info-char-count', 500);
});

