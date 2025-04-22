// Share Project Functionality
document.addEventListener('DOMContentLoaded', function() {
    // Copy to clipboard functionality
    const copyBtn = document.querySelector('.share-project-card .copy-btn');
    const shareInput = document.querySelector('.share-project-card .share-link-input');
    
    if (copyBtn && shareInput) {
        copyBtn.addEventListener('click', function() {
            // Select the text
            shareInput.select();
            shareInput.setSelectionRange(0, 99999); // For mobile devices
            
            // Copy the text
            navigator.clipboard.writeText(shareInput.value)
                .then(() => {
                    // Update button text temporarily
                    const originalContent = copyBtn.innerHTML;
                    copyBtn.innerHTML = '<i class="fas fa-check"></i> Copied!';
                    
                    // Reset button text after 2 seconds
                    setTimeout(() => {
                        copyBtn.innerHTML = originalContent;
                    }, 2000);
                })
                .catch(err => {
                    console.error('Failed to copy: ', err);
                });
        });
    }
    
    // Share options functionality
    const shareOptions = document.querySelectorAll('.share-project-card .share-option');
    const projectUrl = document.querySelector('.share-link-input').value;
    const projectTitle = "E-commerce Platform Development";
    
    shareOptions.forEach(option => {
        option.addEventListener('click', function() {
            let shareUrl = '';
            
            // Create appropriate share URLs based on the platform
            if (option.classList.contains('facebook')) {
                shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(projectUrl)}`;
            } else if (option.classList.contains('twitter')) {
                shareUrl = `https://twitter.com/intent/tweet?url=${encodeURIComponent(projectUrl)}&text=${encodeURIComponent('Check out this project: ' + projectTitle)}`;
            } else if (option.classList.contains('linkedin')) {
                shareUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(projectUrl)}`;
            } else if (option.classList.contains('whatsapp')) {
                shareUrl = `https://api.whatsapp.com/send?text=${encodeURIComponent('Check out this project: ' + projectTitle + ' ' + projectUrl)}`;
            } else if (option.classList.contains('email')) {
                shareUrl = `mailto:?subject=${encodeURIComponent('Interesting Project: ' + projectTitle)}&body=${encodeURIComponent('Check out this project: ' + projectUrl)}`;
            }
            
            // Open share URL in a new window
            if (shareUrl) {
                window.open(shareUrl, '_blank', 'width=600,height=400');
            }
        });
    });
    
    // Add hover effects to similar project cards
    const projectCards = document.querySelectorAll('.similar-projects-section .project-card');
    projectCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 15px 30px rgba(0, 0, 0, 0.1)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = '';
            this.style.boxShadow = '';
        });
    });
});