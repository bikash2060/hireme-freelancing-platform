document.addEventListener('DOMContentLoaded', function() {
    const track = document.querySelector('.testimonial-track');
    const slides = document.querySelectorAll('.testimonial-slide');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const dotsContainer = document.querySelector('.slider-dots');
    
    let slideWidth = slides[0].getBoundingClientRect().width;
    let slideMargin = parseInt(window.getComputedStyle(slides[0]).marginLeft) + 
                      parseInt(window.getComputedStyle(slides[0]).marginRight);
    let slideIndex = 0;
    let slidesPerView = getSlidesPerView();
    let maxIndex = slides.length - slidesPerView;
    
    createDots();
    updateDots();
    updateButtons();
    
    window.addEventListener('resize', function() {
        slideWidth = slides[0].getBoundingClientRect().width;
        slidesPerView = getSlidesPerView();
        maxIndex = slides.length - slidesPerView;
        
        if (slideIndex > maxIndex) {
            slideIndex = maxIndex;
        }
        
        updateSliderPosition();
        updateDots();
        updateButtons();
    });
    
    prevBtn.addEventListener('click', function() {
        if (slideIndex > 0) {
            slideIndex--;
            updateSliderPosition();
            updateDots();
            updateButtons();
        }
    });
    
    nextBtn.addEventListener('click', function() {
        if (slideIndex < maxIndex) {
            slideIndex++;
            updateSliderPosition();
            updateDots();
            updateButtons();
        }
    });
    
    function getSlidesPerView() {
        const viewportWidth = window.innerWidth;
        if (viewportWidth < 768) {
            return 1;
        } else if (viewportWidth < 1024) {
            return 2;
        } else {
            return 3;
        }
    }
    
    function updateSliderPosition() {
        const position = -(slideIndex * (slideWidth + slideMargin));
        track.style.transform = `translateX(${position}px)`;
    }
    
    function createDots() {
        const dotCount = maxIndex + 1;
        for (let i = 0; i < dotCount; i++) {
            const dot = document.createElement('button');
            dot.classList.add('slider-dot');
            dot.setAttribute('aria-label', `Slide ${i + 1}`);
            dot.addEventListener('click', function() {
                slideIndex = i;
                updateSliderPosition();
                updateDots();
                updateButtons();
        });
        dotsContainer.appendChild(dot);
        }
    }
    
    function updateDots() {
        const dots = document.querySelectorAll('.slider-dot');
        dots.forEach((dot, index) => {
        if (index === slideIndex) {
            dot.classList.add('active');
        } else {
            dot.classList.remove('active');
        }
        });
    }
    
    function updateButtons() {
        prevBtn.disabled = slideIndex === 0;
        nextBtn.disabled = slideIndex === maxIndex;
    }
    
    let autoSlideInterval = setInterval(autoSlide, 5000);
    
    function autoSlide() {
        if (slideIndex < maxIndex) {
            slideIndex++;
        } else {
            slideIndex = 0;
        }
        updateSliderPosition();
        updateDots();
        updateButtons();
    }
    
    track.addEventListener('mouseenter', function() {
        clearInterval(autoSlideInterval);
    });
    
    track.addEventListener('mouseleave', function() {
        autoSlideInterval = setInterval(autoSlide, 5000);
    });
    
    let touchStartX = 0;
    let touchEndX = 0;
    
    track.addEventListener('touchstart', function(e) {
        touchStartX = e.changedTouches[0].screenX;
        clearInterval(autoSlideInterval);
    }, { passive: true });
    
    track.addEventListener('touchend', function(e) {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipe();
        autoSlideInterval = setInterval(autoSlide, 5000);
    }, { passive: true });
    
    function handleSwipe() {
        const swipeThreshold = 50;
        if (touchEndX < touchStartX - swipeThreshold && slideIndex < maxIndex) {
            slideIndex++;
        } else if (touchEndX > touchStartX + swipeThreshold && slideIndex > 0) {
            slideIndex--;
        }
        updateSliderPosition();
        updateDots();
        updateButtons();
    }
});