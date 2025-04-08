document.addEventListener('DOMContentLoaded', function() {
    const educationList = document.querySelector('.education-info .education-list');
    const showMoreBtn = document.querySelector('.education-info .show-more-btn');
    const hiddenEducation = document.querySelectorAll('.education-info .hidden-education');
    
    if (showMoreBtn && hiddenEducation.length > 0) {
        showMoreBtn.addEventListener('click', function() {
            const isExpanded = educationList.classList.contains('show-all');
            
            if (isExpanded) {
                educationList.classList.remove('show-all');
                showMoreBtn.innerHTML = `
                    Show all ${hiddenEducation.length + 2} Education
                    <i class="fas fa-chevron-down"></i>
                `;
            } else {
                educationList.classList.add('show-all');
                showMoreBtn.innerHTML = `
                    Show Less
                    <i class="fas fa-chevron-up"></i>
                `;
            }
        });
    }
}); 