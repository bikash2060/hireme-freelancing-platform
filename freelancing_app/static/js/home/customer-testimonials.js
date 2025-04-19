// Testimonial Tabs Functionality
document.addEventListener('DOMContentLoaded', function() {
    const tabButtons = document.querySelectorAll('.testimonials-section .tab-button');
    const tabContents = document.querySelectorAll('.testimonials-section .testimonial-tab');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            tabButtons.forEach(btn => btn.classList.remove('active'));
            
            button.classList.add('active');
            
            tabContents.forEach(tab => {
                tab.classList.remove('active');
                tab.style.display = 'none';
            });
            
            const tabId = button.getAttribute('data-tab');
            const tabContent = document.getElementById(`${tabId}-tab`);
            
            setTimeout(() => {
                tabContent.style.display = 'block';
                
                tabContent.offsetHeight;
                
                setTimeout(() => {
                    tabContent.classList.add('active');
                }, 10);
            }, 100);
        });
    });
    
    const testimonialItems = document.querySelectorAll('.testimonial-item');
    
    const animateOnScroll = () => {
        testimonialItems.forEach((item, index) => {
            const itemPosition = item.getBoundingClientRect().top;
            const screenPosition = window.innerHeight;
            
            if (itemPosition < screenPosition - 100) {
                setTimeout(() => {
                    item.classList.add('animate');
                }, index * 100);
            }
        });
    };
    
    testimonialItems.forEach((item, index) => {
        item.style.opacity = '0';
        item.style.transform = 'translateY(20px)';
        item.style.transition = `all 0.4s ease ${index * 0.1}s`;
    });
    
    setTimeout(() => {
        testimonialItems.forEach(item => {
            item.style.opacity = '1';
            item.style.transform = 'translateY(0)';
        });
    }, 300);
    
    window.addEventListener('scroll', animateOnScroll);
});