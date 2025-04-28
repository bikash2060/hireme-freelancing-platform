document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('confirmation-modal');
    const confirmBtn = document.getElementById('confirm-remove');
    const cancelBtn = document.getElementById('cancel-remove');
    const messageEl = document.getElementById('confirmation-message');
    
    let deleteUrl = '#';
    
    function showModal() {
        modal.style.display = 'block';
        void modal.offsetWidth;
        modal.classList.add('show');
        
        setTimeout(() => {
            cancelBtn.focus();
        }, 100);
    }
    
    function hideModal() {
        modal.classList.remove('show');
        setTimeout(() => {
            modal.style.display = 'none';
        }, 250); 
    }
    
    document.querySelectorAll('.delete-action').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            
            const itemType = this.dataset.itemType || 'item';
            deleteUrl = this.getAttribute('href') || '#';
            messageEl.textContent = `Are you sure you want to delete this ${itemType}? This action cannot be undone.`;
            
            showModal();
        });
    });
    
    confirmBtn.addEventListener('click', function() {
        if (deleteUrl) {
            this.innerHTML = '<span class="spinner"></span>Removing...';
            this.disabled = true;
            
            setTimeout(() => {
                if (deleteUrl === '#') {
                    hideModal();
                    setTimeout(() => {
                        confirmBtn.innerHTML = 'Remove';
                        confirmBtn.disabled = false;
                    }, 300);
                } else {
                    window.location.href = deleteUrl;
                }
            }, 1000);
        }
    });
    
    cancelBtn.addEventListener('click', function() {
        hideModal();
        deleteUrl = '';
    });
    
    window.addEventListener('click', function(e) {
        if (e.target === modal) {
            hideModal();
            deleteUrl = '';
        }
    });
    
    document.addEventListener('keydown', function(e) {
        if (modal.classList.contains('show')) {
            if (e.key === 'Escape') {
                hideModal();
                deleteUrl = '';
            } else if (e.key === 'Enter') {
                if (document.activeElement === confirmBtn) {
                    confirmBtn.click();
                }
            }
        }
    });
});