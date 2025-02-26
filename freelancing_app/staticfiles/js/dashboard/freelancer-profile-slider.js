document.querySelectorAll('.slider-container').forEach((container) => {
    const slider = container.querySelector('.slider');
    const items = container.querySelectorAll('.slider-item');
    const prevButton = container.querySelector('.prev-btn');
    const nextButton = container.querySelector('.next-btn');
    let currentIndex = 0;
    const totalItems = items.length;

    function showSlide(index) {
        currentIndex = Math.min(Math.max(index, 0), totalItems - 1);
        const offset = -currentIndex * 100;
        slider.style.transform = `translateX(${offset}%)`;

        prevButton.style.display = currentIndex === 0 ? 'none' : 'block';
        nextButton.style.display = currentIndex === totalItems - 1 ? 'none' : 'block';
    }

    prevButton.addEventListener('click', () => showSlide(currentIndex - 1));
    nextButton.addEventListener('click', () => showSlide(currentIndex + 1));

    showSlide(currentIndex);
});
