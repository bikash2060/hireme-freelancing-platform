function initializeProjectForm() {
    const form = document.getElementById('project-form');
    
    if (!form) return;
    
    let statusInput = document.getElementById('status_input');
    if (!statusInput) {
        statusInput = document.createElement('input');
        statusInput.type = 'hidden';
        statusInput.name = 'status';
        statusInput.id = 'status_input';
        statusInput.value = 'draft'; 
        form.appendChild(statusInput);
    }
    
    document.querySelectorAll('button[type="submit"]').forEach(button => {
        button.addEventListener('click', function() {
            statusInput.value = this.value;
        });
    });
    
}
document.addEventListener('DOMContentLoaded', initializeProjectForm);