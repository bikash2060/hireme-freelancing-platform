document.addEventListener('DOMContentLoaded', function() {
    const showMoreBtns = document.querySelectorAll('.show-more-btn');
    
    showMoreBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const experienceList = this.closest('.card-body').querySelector('.experience-list');
            const experienceCount = this.dataset.count;
            experienceList.classList.toggle('show-all');
            
            if (experienceList.classList.contains('show-all')) {
                this.innerHTML = `Show Less <i class="fas fa-chevron-up"></i>`;
                this.classList.add('show-less');
            } else {
                this.innerHTML = `Show all ${experienceCount} Experiences <i class="fas fa-chevron-down"></i>`;
                this.classList.remove('show-less');
            }
        });
    });
});