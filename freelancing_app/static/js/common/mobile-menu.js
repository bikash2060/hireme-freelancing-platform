document.addEventListener('DOMContentLoaded', function() {
    const hamburgerMenu = document.querySelector('.hamburger-menu');
    const mobileNav = document.querySelector('.mobile-nav');
    
    if (hamburgerMenu && mobileNav) {
        hamburgerMenu.addEventListener('click', function(e) {
            e.stopPropagation(); 
            toggleMobileMenu();
        });
        
        document.addEventListener('click', function(event) {
            if (mobileNav.classList.contains('show') && 
                !mobileNav.contains(event.target) && 
                !hamburgerMenu.contains(event.target)) {
                toggleMobileMenu();
            }
        });
    }
    
    function toggleMobileMenu() {
        const isOpen = mobileNav.classList.contains('show');
        
        hamburgerMenu.innerHTML = isOpen 
            ? '<i class="fas fa-bars"></i>' 
            : '<i class="fas fa-times"></i>';
        
        if (!isOpen) {
            mobileNav.classList.add('show');
        } else {
            mobileNav.classList.remove('show');
        }
    }
});