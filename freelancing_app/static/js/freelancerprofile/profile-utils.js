function toggleVisibility(fieldId, button) {
    const field = document.getElementById(fieldId);
    
    if (field.dataset.hidden === "true") {
        field.textContent = field.dataset.original;
        field.dataset.hidden = "false";
        button.textContent = "Hide";
    } else {
        field.dataset.original = field.textContent;
        const [username, domain] = field.textContent.split("@");
        field.textContent = username.slice(0, 4) + "***@" + domain;
        field.dataset.hidden = "true";
        button.textContent = "Reveal";
    }
}

document.addEventListener("DOMContentLoaded", function () {
    toggleVisibility("email", document.querySelector("[onclick=\"toggleVisibility('email', this)\"]"));
});

document.addEventListener('DOMContentLoaded', function() {
    const profileImageInput = document.getElementById('profile_image');
    const imagePreview = document.getElementById('image-preview');
    const currentImage = document.querySelector('.current-image');
    const imageOverlay = document.querySelector('.image-overlay');

    if (currentImage) {
        currentImage.addEventListener('mouseenter', function() {
            imageOverlay.style.opacity = '1';
        });
        
        currentImage.addEventListener('mouseleave', function() {
            imageOverlay.style.opacity = '0';
        });
        
        currentImage.addEventListener('click', function() {
            profileImageInput.click();
        });
    }

    if (profileImageInput) {
        profileImageInput.addEventListener('change', function(e) {
            if (e.target.files.length > 0) {
                const file = e.target.files[0];
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    imagePreview.innerHTML = `
                        <div class="preview-container">
                            <img src="${e.target.result}" alt="Image Preview" class="preview-img">
                        </div>
                    `;
                    imagePreview.style.display = 'block';
                    currentImage.style.display = 'none';
                };
                
                reader.readAsDataURL(file);
            }
        });
    }

    const removeImageBtn = document.getElementById('remove-image');
    const confirmationModal = document.getElementById('confirmation-modal');
    const cancelRemoveBtn = document.getElementById('cancel-remove');
    const confirmRemoveBtn = document.getElementById('confirm-remove');
    
    if (removeImageBtn && confirmationModal) {
        removeImageBtn.addEventListener('click', function(e) {
            e.preventDefault();
            confirmationModal.style.display = 'block';
        });
        
        cancelRemoveBtn.addEventListener('click', function() {
            confirmationModal.style.display = 'none';
        });
        
        confirmRemoveBtn.addEventListener('click', function() {
            window.location.href = removeImageBtn.getAttribute('href');
        });
        
        confirmationModal.addEventListener('click', function(e) {
            if (e.target === this) {
                this.style.display = 'none';
            }
        });
    }

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
    
    const emailInput = document.getElementById('email');
    emailInput.addEventListener('mouseenter', function() {
        this.style.cursor = 'not-allowed';
    });

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