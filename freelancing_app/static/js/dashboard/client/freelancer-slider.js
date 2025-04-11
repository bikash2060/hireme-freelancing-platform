document.addEventListener('DOMContentLoaded', function() {
    const sliders = document.querySelectorAll('.freelancer-project-slider');
    
    sliders.forEach(slider => {
        const track = slider.querySelector('.slider-track');
        const slides = slider.querySelectorAll('.slide');
        const prevBtn = slider.querySelector('.slider-prev');
        const nextBtn = slider.querySelector('.slider-next');
        const dots = slider.querySelectorAll('.dot');
        
        let currentIndex = 0;
        const slideCount = slides.length;
        
        updateSlider();
        
        nextBtn.addEventListener('click', () => {
            currentIndex = (currentIndex + 1) % slideCount;
            updateSlider();
        });
        
        prevBtn.addEventListener('click', () => {
            currentIndex = (currentIndex - 1 + slideCount) % slideCount;
            updateSlider();
        });
        
        dots.forEach((dot, index) => {
            dot.addEventListener('click', () => {
                currentIndex = index;
                updateSlider();
            });
        });
        
        function updateSlider() {
            track.style.transform = `translateX(-${currentIndex * 100}%)`;
            
            dots.forEach((dot, index) => {
                dot.classList.toggle('active', index === currentIndex);
            });
        }
    });
});