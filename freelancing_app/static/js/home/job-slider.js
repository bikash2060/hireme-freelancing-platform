let currentIndex = 0;
const cardGrid = document.querySelector('.card-grid');
const prevButton = document.querySelector('.prev-btn');
const nextButton = document.querySelector('.next-btn');
const projectCards = document.querySelectorAll('.project-card');
const totalProjects = projectCards.length;
const cardsPerPage = 4;

function updateSlider() {
    projectCards.forEach((card, index) => {
        if (index >= currentIndex && index < currentIndex + cardsPerPage) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });

    prevButton.disabled = currentIndex === 0;
    nextButton.disabled = currentIndex >= totalProjects - cardsPerPage || totalProjects <= cardsPerPage;

    function updateButtonStyle(button) {
        if (button.disabled) {
            button.style.backgroundColor = 'white';
            button.querySelector('i').style.color = '#1E88E5';
        } else {
            button.style.backgroundColor = '#1E88E5';
            button.querySelector('i').style.color = 'white';
        }
    }

    updateButtonStyle(prevButton);
    updateButtonStyle(nextButton);
}

prevButton.addEventListener('click', () => {
    if (currentIndex > 0) {
        currentIndex -= cardsPerPage;
        updateSlider();
    }
});

nextButton.addEventListener('click', () => {
    if (currentIndex < totalProjects - cardsPerPage) {
        currentIndex += cardsPerPage;
        updateSlider();
    }
});

document.addEventListener('DOMContentLoaded', () => {
    updateSlider();
});
