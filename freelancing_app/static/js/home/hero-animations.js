document.addEventListener('DOMContentLoaded', function() {
    const statNumbers = document.querySelectorAll('.stat-number');
    
    statNumbers.forEach(stat => {
        const target = parseInt(stat.getAttribute('data-count'));
        const suffix = stat.textContent.includes('%') ? '%' : '';
        const duration = 2000; 
        const startTime = Date.now();
        
        const animateCount = () => {
            const now = Date.now();
            const progress = Math.min(1, (now - startTime) / duration);
            const value = Math.floor(progress * target);
            
            stat.textContent = value + suffix;
            
            if (progress < 1) {
                requestAnimationFrame(animateCount);
            }
        };
        
        const observer = new IntersectionObserver((entries) => {
            if (entries[0].isIntersecting) {
                animateCount();
                observer.unobserve(stat);
            }
        });
        
        observer.observe(stat);
    });
    
    const floatingImages = document.querySelectorAll('.floating-image');
    
    floatingImages.forEach((img, index) => {
        const duration = 3 + (index * 0.5);
        const yMovement = 20 + (index * 5);
        
        gsap.to(img, {
            y: yMovement,
            duration: duration,
            repeat: -1,
            yoyo: true,
            ease: "sine.inOut"
        });
    });
    
    const heroSection = document.querySelector('.hero-section');
    
    gsap.to(heroSection, {
        '--circle-scale': 1.1,
        duration: 8,
        repeat: -1,
        yoyo: true,
        ease: "sine.inOut"
    });
});