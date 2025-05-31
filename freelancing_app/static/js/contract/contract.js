document.addEventListener('DOMContentLoaded', function() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.querySelector('#uploadArea input[type="file"]');
    const filePreview = document.getElementById('filePreview');
    
    if (uploadArea && fileInput && filePreview) {
        uploadArea.addEventListener('click', function(e) {
            if (e.target !== fileInput) {
                fileInput.click();
            }
        });
        
        uploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', function() {
            this.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('dragover');
            fileInput.files = e.dataTransfer.files;
            updateFilePreview();
        });
        
        fileInput.addEventListener('change', updateFilePreview);
        
        function updateFilePreview() {
            filePreview.innerHTML = '';
            
            if (fileInput.files.length > 0) {
                filePreview.classList.add('active');
                
                for (let i = 0; i < fileInput.files.length; i++) {
                    const file = fileInput.files[i];
                    const fileItem = document.createElement('div');
                    fileItem.className = 'file-preview-item';
                    
                    let iconClass = 'fa-file';
                    if (file.type.includes('image')) iconClass = 'fa-file-image';
                    else if (file.type.includes('pdf')) iconClass = 'fa-file-pdf';
                    else if (file.type.includes('word')) iconClass = 'fa-file-word';
                    else if (file.type.includes('excel')) iconClass = 'fa-file-excel';
                    else if (file.type.includes('zip')) iconClass = 'fa-file-archive';
                    
                    fileItem.innerHTML = `
                        <i class="fas ${iconClass}"></i>
                        <span>${file.name}</span>
                        <span class="remove-file"><i class="fas fa-times"></i></span>
                    `;
                    
                    filePreview.appendChild(fileItem);
                    
                    // Add remove file functionality
                    const removeBtn = fileItem.querySelector('.remove-file');
                    removeBtn.addEventListener('click', function() {
                        // Create new DataTransfer to remove the file
                        const dataTransfer = new DataTransfer();
                        for (let j = 0; j < fileInput.files.length; j++) {
                            if (j !== i) {
                                dataTransfer.items.add(fileInput.files[j]);
                            }
                        }
                        fileInput.files = dataTransfer.files;
                        updateFilePreview();
                    });
                }
            } else {
                filePreview.classList.remove('active');
            }
        }
    }
    
    const starInputs = document.querySelectorAll('.rating-stars input');
    starInputs.forEach(input => {
        input.addEventListener('change', function() {
            const rating = this.value;
            console.log('Selected rating:', rating);
        });
    });
});