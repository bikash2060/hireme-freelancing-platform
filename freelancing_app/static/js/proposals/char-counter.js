document.addEventListener('DOMContentLoaded', function() {
    // Function to create character counter handler
    function createCharacterCounter(textareaId, counterId, maxLength) {
        const textarea = document.getElementById(textareaId);
        const charCount = document.getElementById(counterId);

        if (textarea && charCount) {
            // Initialize count
            charCount.textContent = textarea.value.length;

            function updateCount() {
                const length = textarea.value.length;
                charCount.textContent = length;
                
                // Optional: Add visual feedback when approaching limit
                if (length > maxLength * 0.9) {
                    charCount.style.color = '#ff6b6b';
                } else {
                    charCount.style.color = '';
                }
            }

            // Handle regular input
            textarea.addEventListener('input', function() {
                if (this.value.length > maxLength) {
                    this.value = this.value.substring(0, maxLength);
                }
                updateCount();
            });

            // Handle paste events
            textarea.addEventListener('paste', function(e) {
                e.preventDefault();
                const pasteData = e.clipboardData.getData('text/plain');
                const remainingChars = maxLength - this.value.length;
                
                if (remainingChars <= 0) return;
                
                const truncatedPaste = pasteData.substring(0, remainingChars);
                document.execCommand('insertText', false, truncatedPaste);
                updateCount();
            });

            // Prevent typing when max length reached
            textarea.addEventListener('keydown', function(e) {
                if (this.value.length >= maxLength && 
                    e.key !== 'Backspace' && 
                    e.key !== 'Delete' &&
                    !e.ctrlKey && !e.metaKey) {
                    e.preventDefault();
                }
            });

            // Initial update
            updateCount();
        }
    }

    // Initialize character counters for all textareas
    createCharacterCounter('cover_letter', 'cover-letter-char-count', 3000);
    createCharacterCounter('approach_methodology', 'approach-methodology-char-count', 2000);
    createCharacterCounter('relevant_experience', 'relevant-experience-char-count', 1500);
    createCharacterCounter('questions_for_client', 'questions-client-char-count', 500);
});