// Toggles action menu visibility for project items and closes others when clicking outside.
document.addEventListener('DOMContentLoaded', function() {
    const actionBtns = document.querySelectorAll('.action-btn');
    
    actionBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            const parent = this.closest('.project-actions');
            parent.classList.toggle('active');
            
            document.querySelectorAll('.project-actions').forEach(el => {
                if (el !== parent) {
                    el.classList.remove('active');
                }
            });
        });
    });
    
    document.addEventListener('click', function() {
        document.querySelectorAll('.project-actions').forEach(el => {
            el.classList.remove('active');
        });
    });
});
