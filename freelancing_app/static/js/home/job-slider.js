let currentIndex = 0;
const jobSlider = document.querySelector('.job-slider');
const prevButton = document.querySelector('.prev-btn');
const nextButton = document.querySelector('.next-btn');
const jobBoxes = document.querySelectorAll('.job-box');
const totalJobs = jobBoxes.length;
const jobsPerPage = 4;

function updateSlider() {
    jobBoxes.forEach((box, index) => {
        if (index >= currentIndex && index < currentIndex + jobsPerPage) {
            box.style.display = 'block';
        } else {
            box.style.display = 'none';
        }
    });

    if (currentIndex === 0) {
        prevButton.disabled = true;
        prevButton.style.backgroundColor = 'white';
        prevButton.querySelector('i').style.color = '#1E88E5';
    } else {
        prevButton.disabled = false;
        prevButton.style.backgroundColor = '#1E88E5';
        prevButton.querySelector('i').style.color = 'white';
    }
}

prevButton.addEventListener('click', () => {
    if (currentIndex > 0) {
        currentIndex -= jobsPerPage;
    }
    updateSlider();
});

nextButton.addEventListener('click', () => {
    if (currentIndex < totalJobs - jobsPerPage) {
        currentIndex += jobsPerPage;
    }
    updateSlider();
});

updateSlider();
