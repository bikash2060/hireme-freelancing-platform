document.addEventListener('DOMContentLoaded', function() {
    const uploadContainer = document.querySelector('.file-upload-container');
    const fileInput = document.querySelector('.file-upload-input');
    const filePreview = document.getElementById('file-preview');
    const progressBar = document.getElementById('upload-progress');
    const progressFill = document.querySelector('.progress-fill');
    const statusText = document.getElementById('status-text');
    const maxSize = 5 * 1024 * 1024; // 5MB in bytes

    uploadContainer.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadContainer.classList.add('drag-over');
    });

    uploadContainer.addEventListener('dragleave', () => {
        uploadContainer.classList.remove('drag-over');
    });

    uploadContainer.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadContainer.classList.remove('drag-over');
        if (e.dataTransfer.files.length) {
            fileInput.files = e.dataTransfer.files;
            handleFiles(fileInput.files);
        }
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length) {
            handleFiles(fileInput.files);
        }
    });

    function handleFiles(files) {
        filePreview.innerHTML = '';
        let validFiles = 0;
        
        Array.from(files).forEach((file, index) => {
            if (file.size > maxSize) {
                statusText.textContent = `File "${file.name}" exceeds 5MB limit`;
                statusText.style.color = '#ff4d4f';
                return;
            }
            
            validFiles++;
            const fileItem = document.createElement('div');
            fileItem.className = 'file-preview-item';
            
            const fileType = file.name.split('.').pop().toLowerCase();
            const fileIcon = getFileIcon(fileType);
            
            fileItem.innerHTML = `
                <div class="file-icon">
                    <i class="fas ${fileIcon}"></i>
                </div>
                <div class="file-info">
                    <div class="file-name">${file.name}</div>
                    <div class="file-size">${formatFileSize(file.size)}</div>
                </div>
                <button class="remove-file" data-index="${index}">
                    <i class="fas fa-times"></i>
                </button>
            `;
            
            filePreview.appendChild(fileItem);
        });
        
        if (validFiles > 0) {
            filePreview.style.display = 'block';
            statusText.textContent = `${validFiles} file(s) selected`;
            statusText.style.color = '#666';
        }
        
        document.querySelectorAll('.remove-file').forEach(button => {
            button.addEventListener('click', function() {
                const index = this.getAttribute('data-index');
                removeFile(index);
            });
        });
    }
    
    function removeFile(index) {
        const dt = new DataTransfer();
        const files = fileInput.files;
        
        for (let i = 0; i < files.length; i++) {
            if (i != index) {
                dt.items.add(files[i]);
            }
        }
        
        fileInput.files = dt.files;
        handleFiles(fileInput.files);
        
        if (fileInput.files.length === 0) {
            filePreview.style.display = 'none';
            statusText.textContent = '';
        }
    }
    
    function getFileIcon(fileType) {
        const icons = {
            pdf: 'fa-file-pdf',
            doc: 'fa-file-word',
            docx: 'fa-file-word',
            jpg: 'fa-file-image',
            jpeg: 'fa-file-image',
            png: 'fa-file-image',
            gif: 'fa-file-image',
            default: 'fa-file'
        };
        
        return icons[fileType] || icons.default;
    }
    
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    function simulateUpload() {
        progressBar.style.display = 'block';
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 10;
            if (progress >= 100) {
                progress = 100;
                clearInterval(interval);
                statusText.textContent = 'Upload complete!';
                statusText.style.color = '#52c41a';
            }
            progressFill.style.width = progress + '%';
            statusText.textContent = `Uploading... ${Math.round(progress)}%`;
        }, 200);
    }
    
    document.querySelector('form').addEventListener('submit', function(e) {
        if (fileInput.files.length > 0) {
            e.preventDefault();
            simulateUpload();
        }
    });
});