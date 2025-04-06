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
});