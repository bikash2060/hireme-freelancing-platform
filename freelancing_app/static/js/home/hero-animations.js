document.addEventListener('DOMContentLoaded', function() {   
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

