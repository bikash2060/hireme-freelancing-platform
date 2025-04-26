document.addEventListener('DOMContentLoaded', function() {
    console.log('Attachments handler initialized');
    
    const uploadContainer = document.querySelector('.file-upload-container');
    const fileInput = document.querySelector('.file-upload-input');
    const filePreview = document.getElementById('file-preview');
    const attachmentsData = document.getElementById('existing-attachments-data');
    
    if (!filePreview) {
        console.error('File preview container not found');
        return;
    }
    
    console.log('File preview element:', filePreview);
    console.log('Debug info:', filePreview.getAttribute('data-debug-info'));
    
    const progressBar = document.getElementById('upload-progress');
    const progressFill = document.querySelector('.progress-fill');
    const statusText = document.getElementById('status-text');
    const maxSize = 5 * 1024 * 1024; // 5MB in bytes
    
    // Get existing attachments with better error handling
    let existingAttachments = [];
    try {
        if (attachmentsData && attachmentsData.textContent.trim()) {
            console.log('Found attachments data:', attachmentsData.textContent.trim());
            existingAttachments = JSON.parse(attachmentsData.textContent.trim());
            console.log('Successfully parsed attachments:', existingAttachments);
        } else {
            console.log('No attachments data found');
        }
    } catch (e) {
        console.error('Error parsing existing attachments:', e);
        if (attachmentsData) {
            console.error('Raw data that caused error:', attachmentsData.textContent);
        }
    }
    
    const deletedAttachments = new Set();

    // Add a hidden input to track deleted attachments
    const deletedAttachmentsInput = document.createElement('input');
    deletedAttachmentsInput.type = 'hidden';
    deletedAttachmentsInput.name = 'deleted_attachments';
    deletedAttachmentsInput.id = 'deleted-attachments-input';
    uploadContainer.appendChild(deletedAttachmentsInput);

    // Show existing attachments on load
    function showExistingAttachments() {
        if (!existingAttachments || !Array.isArray(existingAttachments)) {
            console.warn('No valid existing attachments found');
            return;
        }

        existingAttachments.forEach(attachment => {
            try {
                if (!attachment || !attachment.id || !attachment.name) {
                    console.warn('Invalid attachment data:', attachment);
                    return;
                }

                const fileItem = document.createElement('div');
                fileItem.className = 'attachment-item';
                fileItem.dataset.attachmentId = attachment.id;
                
                const fileType = attachment.name.split('.').pop().toLowerCase();
                const fileIcon = getFileIconClass(fileType);
                const fileSize = formatFileSize(attachment.size || 0);
                const uploadTime = attachment.uploaded_at ? getTimeAgo(new Date(attachment.uploaded_at)) : 'Unknown time';
                
                fileItem.innerHTML = `
                    <div class="attachment-details">
                        <div class="attachment-name">${attachment.name}</div>
                        <div class="attachment-meta">
                            ${fileSize} · Uploaded ${uploadTime}
                        </div>
                    </div>
                    <a href="${attachment.url || '#'}" class="download-btn" download>
                        <i class="fas fa-download"></i>
                    </a>
                    <button class="remove-btn" data-id="${attachment.id}">
                        <i class="fas fa-times"></i>
                    </button>
                `;
                
                filePreview.appendChild(fileItem);
                
                // Add event listener for the remove button
                const removeBtn = fileItem.querySelector('.remove-btn');
                if (removeBtn) {
                    removeBtn.addEventListener('click', function() {
                        const attachmentId = this.getAttribute('data-id');
                        handleDeleteAttachment(attachmentId, fileItem);
                    });
                }
            } catch (e) {
                console.error('Error displaying attachment:', e);
            }
        });
        
        if (existingAttachments.length > 0) {
            filePreview.style.display = 'block';
        }
    }

    // Handle deletion of an existing attachment
    function handleDeleteAttachment(attachmentId, fileItem) {
        if (attachmentId) {
            deletedAttachments.add(attachmentId);
            updateDeletedAttachmentsInput();
        }
        
        if (fileItem && fileItem.parentNode) {
            fileItem.parentNode.removeChild(fileItem);
        }
        
        // Hide the file preview if no more files
        if (filePreview.children.length === 0) {
            filePreview.style.display = 'none';
        }
    }
    
    // Update the hidden input value with deleted attachment IDs
    function updateDeletedAttachmentsInput() {
        deletedAttachmentsInput.value = Array.from(deletedAttachments).join(',');
    }

    // Initialize on page load
    showExistingAttachments();

    // File type to icon class mapping
    function getFileIconClass(fileType) {
        const icons = {
            'pdf': 'pdf-icon',
            'doc': 'doc-icon',
            'docx': 'doc-icon',
            'png': 'image-icon',
            'jpg': 'image-icon',
            'jpeg': 'image-icon'
        };
        return icons[fileType] || 'default-icon';
    }

    // Format file size
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 KB';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }

    // Get time ago string
    function getTimeAgo(date) {
        const seconds = Math.floor((new Date() - date) / 1000);
        const intervals = {
            year: 31536000,
            month: 2592000,
            week: 604800,
            day: 86400,
            hour: 3600,
            minute: 60
        };

        for (let [unit, secondsInUnit] of Object.entries(intervals)) {
            const interval = Math.floor(seconds / secondsInUnit);
            if (interval >= 1) {
                return `${interval} ${unit}${interval === 1 ? '' : 's'} ago`;
            }
        }
        return 'just now';
    }

    // Handle file uploads
    fileInput.addEventListener('change', handleFiles);
    
    function handleFiles(event) {
        const files = event.target.files;
        if (!files.length) return;

        Array.from(files).forEach(file => {
            if (file.size > maxSize) {
                statusText.textContent = `File "${file.name}" exceeds 5MB limit`;
                return;
            }

            const fileItem = document.createElement('div');
            fileItem.className = 'attachment-item';
            
            const fileType = file.name.split('.').pop().toLowerCase();
            const fileIcon = getFileIconClass(fileType);
            const fileSize = formatFileSize(file.size);
            
            fileItem.innerHTML = `
                <div class="attachment-icon ${fileIcon}"></div>
                <div class="attachment-details">
                    <div class="attachment-name">${file.name}</div>
                    <div class="attachment-meta">
                        ${fileSize} · Just uploaded
                    </div>
                </div>
                <button class="remove-btn">
                    <i class="fas fa-times"></i>
                </button>
            `;
            
            filePreview.appendChild(fileItem);
            
            // Add event listener for the remove button
            const removeBtn = fileItem.querySelector('.remove-btn');
            if (removeBtn) {
                removeBtn.addEventListener('click', function() {
                    if (fileItem && fileItem.parentNode) {
                        fileItem.parentNode.removeChild(fileItem);
                    }
                    
                    // Hide the file preview if no more files
                    if (filePreview.children.length === 0) {
                        filePreview.style.display = 'none';
                    }
                });
            }
        });
        
        filePreview.style.display = 'block';
    }

    // Handle drag and drop
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
        const dt = e.dataTransfer;
        fileInput.files = dt.files;
        handleFiles({ target: { files: dt.files } });
    });
    
    // Add event listener to the form for submission
    const projectForm = document.getElementById('project-form');
    if (projectForm) {
        projectForm.addEventListener('submit', function() {
            // Make sure the deleted attachments are included
            updateDeletedAttachmentsInput();
        });
    }
});