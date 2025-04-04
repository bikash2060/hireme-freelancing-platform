document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('confirmation-modal');
    const confirmBtn = document.getElementById('confirm-remove');
    const cancelBtn = document.getElementById('cancel-remove');
    const messageEl = document.getElementById('confirmation-message');
    
    let deleteUrl = '';
    
    document.querySelectorAll('.delete-action').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            
            const itemType = this.dataset.itemType || 'item';
            deleteUrl = this.getAttribute('href');
            console.log('Delete URL:', deleteUrl);
            messageEl.textContent = `Are you sure you want to delete this ${itemType}?`;
            
            modal.style.display = 'block';
        });
    });
    
    confirmBtn.addEventListener('click', function() {
        if (deleteUrl) {
            window.location.href = deleteUrl;
        }
        modal.style.display = 'none';
    });
    
    cancelBtn.addEventListener('click', function() {
        modal.style.display = 'none';
        deleteUrl = '';
    });
    
    window.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.style.display = 'none';
            deleteUrl = '';
        }
    });
});