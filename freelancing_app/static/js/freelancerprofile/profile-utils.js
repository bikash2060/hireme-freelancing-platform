// Toggles visibility of sensitive text (e.g. email) between hidden and revealed states.
document.addEventListener("DOMContentLoaded", function() {
    const emailField = document.getElementById("email");
    const toggleButton = document.querySelector(".visibility-toggle");
    
    function toggleEmailVisibility() {
        if (emailField.dataset.hidden === "true") {
            emailField.textContent = emailField.dataset.original;
            emailField.dataset.hidden = "false";
            toggleButton.textContent = "Hide";
        } else {
            emailField.dataset.original = emailField.textContent;
            const [username, domain] = emailField.textContent.split("@");
            emailField.textContent = username.slice(0, 4) + "***@" + domain;
            emailField.dataset.hidden = "true";
            toggleButton.textContent = "Reveal";
        }
    }
    
    emailField.dataset.original = emailField.textContent;
    const [username, domain] = emailField.textContent.split("@");
    emailField.textContent = username.slice(0, 4) + "***@" + domain;
    emailField.dataset.hidden = "true";
    
    toggleButton.addEventListener("click", toggleEmailVisibility);
});

// Handles profile image preview/removal, bio character limit, email/phone input behaviors, and UI interactions.
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

// Manages skill selection with live search, dynamic tag display, and skill count feedback.
document.addEventListener('DOMContentLoaded', function() {
    const skillsSearch = document.getElementById('skills_search');
    const skillsOptions = document.getElementById('skills-options');
    const selectedSkillsList = document.querySelector('.selected-skills-list');
    const skillCheckboxes = document.querySelectorAll('input[name="skills"]');
    
    const noResultsMsg = document.createElement('div');
    noResultsMsg.className = 'no-results-msg';
    noResultsMsg.textContent = 'No matching skills found';
    noResultsMsg.style.display = 'none';
    skillsOptions.parentNode.insertBefore(noResultsMsg, skillsOptions.nextSibling);
    
    skillsSearch.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase().trim();
        const skillOptions = skillsOptions.querySelectorAll('.skill-option');
        let hasMatches = false;
        
        skillOptions.forEach(option => {
            const skillName = option.querySelector('label').textContent.toLowerCase();
            if (searchTerm === '' || skillName.includes(searchTerm)) {
                option.style.display = 'flex';
                hasMatches = true;
            } else {
                option.style.display = 'none';
            }
        });
        
        if (searchTerm !== '' && !hasMatches) {
            noResultsMsg.style.display = 'block';
            skillsOptions.style.display = 'none';
        } else {
            noResultsMsg.style.display = 'none';
            skillsOptions.style.display = 'block';
        }
    });
    
    skillCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            updateSelectedSkills();
        });
    });
    
    function updateSelectedSkills() {
        selectedSkillsList.innerHTML = '';
        
        const checkedSkills = document.querySelectorAll('input[name="skills"]:checked');
        
        checkedSkills.forEach(checkbox => {
            const skillId = checkbox.id;
            const skillName = checkbox.nextElementSibling.nextElementSibling.textContent; 
            
            const skillElement = document.createElement('div');
            skillElement.className = 'selected-skill';
            skillElement.innerHTML = `
                ${skillName}
                <span class="remove-skill" data-skill-id="${skillId}">
                    <i class="fas fa-times"></i>
                </span>
            `;
            
            selectedSkillsList.appendChild(skillElement);
        });
        
        document.querySelectorAll('.remove-skill').forEach(removeBtn => {
            removeBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                const skillId = this.getAttribute('data-skill-id');
                const checkbox = document.getElementById(skillId);
                if (checkbox) {
                    checkbox.checked = false;
                    updateSelectedSkills();
                }
            });
        });
        
        const hintElement = document.querySelector('.tags-hint');
        if (checkedSkills.length >= 5) {
            hintElement.textContent = 'Great! Your profile is better now.';
            hintElement.style.color = '#28a745';
        } else {
            hintElement.textContent = `Add ${5 - checkedSkills.length} more skills to increase your visibility`;
            hintElement.style.color = '#6c757d';
        }
    }
    
    updateSelectedSkills();
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