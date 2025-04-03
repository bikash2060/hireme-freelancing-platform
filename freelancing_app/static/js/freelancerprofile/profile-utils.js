

document.addEventListener('DOMContentLoaded', function() {
    const jobDescriptionTextarea = document.getElementById('job_description');
    const descCharCount = document.getElementById('desc-char-count');
    const maxChars = 500;

    if (jobDescriptionTextarea && descCharCount) {
        descCharCount.textContent = jobDescriptionTextarea.value.length;
        
        function updateDescCount() {
            const length = jobDescriptionTextarea.value.length;
            descCharCount.textContent = length;
            
            if (length > maxChars * 0.9) {
                descCharCount.style.color = '#e74c3c';
            } else {
                descCharCount.style.color = '#2ecc71';
            }
        }
        
        jobDescriptionTextarea.addEventListener('input', function() {
            if (this.value.length > maxChars) {
                this.value = this.value.substring(0, maxChars);
            }
            updateDescCount();
        });
        
        jobDescriptionTextarea.addEventListener('paste', function(e) {
            e.preventDefault();
            const pasteData = e.clipboardData.getData('text/plain');
            const remainingChars = maxChars - this.value.length;
            
            if (remainingChars <= 0) return;
            
            const truncatedPaste = pasteData.substring(0, remainingChars);
            document.execCommand('insertText', false, truncatedPaste);
            updateDescCount();
        });
        
        jobDescriptionTextarea.addEventListener('keydown', function(e) {
            if (this.value.length >= maxChars && 
                e.key !== 'Backspace' && 
                e.key !== 'Delete' &&
                !e.ctrlKey && !e.metaKey) {
                e.preventDefault();
            }
        });
        
        updateDescCount();
    }

    const currentlyWorkingCheckbox = document.getElementById('currently_working');
    const endDateInput = document.getElementById('end_date');

    if (currentlyWorkingCheckbox && endDateInput) {
        if (currentlyWorkingCheckbox.checked) {
            endDateInput.disabled = true;
            endDateInput.value = '';
        }

        currentlyWorkingCheckbox.addEventListener('change', function() {
            if (currentlyWorkingCheckbox.checked) {
                endDateInput.disabled = true;
                endDateInput.value = '';
                endDateInput.style.backgroundColor = '#f8f9fa';
                endDateInput.style.cursor = 'not-allowed';
            } else {
                endDateInput.disabled = false;
                endDateInput.style.backgroundColor = ''; 
                endDateInput.style.cursor = ''; 
            }
        });
    }
});

