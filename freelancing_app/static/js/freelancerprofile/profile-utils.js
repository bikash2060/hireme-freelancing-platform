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

document.addEventListener('DOMContentLoaded', function() {
    // Skill Search Functionality
    document.getElementById('skills_search').addEventListener('input', function(e) {
        const searchTerm = e.target.value.toLowerCase();
        const skillOptions = document.querySelectorAll('.skill-option');
        
        skillOptions.forEach(option => {
            const skillName = option.querySelector('label').textContent.toLowerCase();
            option.style.display = skillName.includes(searchTerm) ? 'flex' : 'none';
        });
    });

    // Skill Selection Handling
    document.querySelectorAll('.skill-option input').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            updateSelectedSkills();
        });
    });

    // Remove Skill
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('remove-skill')) {
            const skillName = e.target.parentElement.textContent.trim();
            const checkbox = document.querySelector(`input[value="${skillName}"]`);
            if (checkbox) {
                checkbox.checked = false;
                updateSelectedSkills();
            }
        }
    });

    function updateSelectedSkills() {
        const selectedSkillsContainer = document.querySelector('.selected-skills-list');
        selectedSkillsContainer.innerHTML = '';
        
        document.querySelectorAll('.skill-option input:checked').forEach(checkbox => {
            const skillName = checkbox.value;
            const skillElement = document.createElement('span');
            skillElement.className = 'selected-skill';
            skillElement.innerHTML = `
                ${skillName}
                <i class="fas fa-times remove-skill"></i>
            `;
            selectedSkillsContainer.appendChild(skillElement);
        });
    }
    
    // Initialize with pre-selected skills
    document.querySelectorAll('input[value="React"], input[value="JavaScript"]').forEach(checkbox => {
        checkbox.checked = true;
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const showMoreBtn = document.querySelector('.show-more-btn');
    if (showMoreBtn) {
        showMoreBtn.addEventListener('click', function() {
            const experienceList = document.querySelector('.experience-list');
            experienceList.classList.toggle('show-experiences');
            
            const showText = this.querySelector('.show-text');
            const showLessText = this.querySelector('.show-less-text');
            const icon = this.querySelector('i');
            
            if (experienceList.classList.contains('show-experiences')) {
                showText.style.display = 'none';
                showLessText.style.display = 'inline';
            } else {
                showText.style.display = 'inline';
                showLessText.style.display = 'none';
            }
        });
    }
});

document.addEventListener('DOMContentLoaded', function() {
    const showMoreBtn = document.querySelector('.education-info .show-more-btn');
    if (showMoreBtn) {
        showMoreBtn.addEventListener('click', function() {
            const educationList = document.querySelector('.education-info .education-list');
            educationList.classList.toggle('show-educations');
            
            const showText = this.querySelector('.show-text');
            const showLessText = this.querySelector('.show-less-text');
            const icon = this.querySelector('i');
            
            if (educationList.classList.contains('show-educations')) {
                showText.style.display = 'none';
                showLessText.style.display = 'inline';
            } else {
                showText.style.display = 'inline';
                showLessText.style.display = 'none';
            }
        });
    }
});

document.addEventListener('DOMContentLoaded', function() {
    const showMoreBtn = document.querySelector('.certifications-info .show-more-btn');
    if (showMoreBtn) {
        showMoreBtn.addEventListener('click', function() {
            const certificationsList = document.querySelector('.certifications-info .certifications-list');
            certificationsList.classList.toggle('show-certifications');
            
            const showText = this.querySelector('.show-text');
            const showLessText = this.querySelector('.show-less-text');
            const icon = this.querySelector('i');
            
            if (certificationsList.classList.contains('show-certifications')) {
                showText.style.display = 'none';
                showLessText.style.display = 'inline';
            } else {
                showText.style.display = 'inline';
                showLessText.style.display = 'none';
            }
        });
    }
});

// Add this JavaScript to handle the show more/less functionality
document.addEventListener('DOMContentLoaded', function() {
    const showMoreBtn = document.querySelector('.portfolio-info .show-more-btn');
    if (showMoreBtn) {
        showMoreBtn.addEventListener('click', function() {
            const portfolioGrid = document.querySelector('.portfolio-info .portfolio-grid');
            portfolioGrid.classList.toggle('show-projects');
            
            const showText = this.querySelector('.show-text');
            const showLessText = this.querySelector('.show-less-text');
            const icon = this.querySelector('i');
            
            if (portfolioGrid.classList.contains('show-projects')) {
                showText.style.display = 'none';
                showLessText.style.display = 'inline';
            } else {
                showText.style.display = 'inline';
                showLessText.style.display = 'none';
            }
        });
    }
});