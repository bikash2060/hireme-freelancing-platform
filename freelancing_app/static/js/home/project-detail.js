document.addEventListener('DOMContentLoaded', function() {
    const copyBtn = document.querySelector('.share-project-card .copy-btn');
    const shareInput = document.querySelector('.share-project-card .share-link-input');
    
    if (copyBtn && shareInput) {
        copyBtn.addEventListener('click', function() {
            shareInput.select();
            shareInput.setSelectionRange(0, 99999); // For mobile devices
            
            navigator.clipboard.writeText(shareInput.value)
                .then(() => {
                    const originalContent = copyBtn.innerHTML;
                    copyBtn.innerHTML = '<i class="fas fa-check"></i> Copied!';
                    
                    setTimeout(() => {
                        copyBtn.innerHTML = originalContent;
                    }, 2000);
                })
                .catch(err => {
                    console.error('Failed to copy: ', err);
                });
        });
    }
    
    const shareOptions = document.querySelectorAll('.share-project-card .share-option');
    const projectUrl = document.querySelector('.share-link-input').value;
    const projectTitle = "E-commerce Platform Development";
    
    shareOptions.forEach(option => {
        option.addEventListener('click', function() {
            let shareUrl = '';
            
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
            
            if (shareUrl) {
                window.open(shareUrl, '_blank', 'width=600,height=400');
            }
        });
    });
});