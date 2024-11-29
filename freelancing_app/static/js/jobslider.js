let currentIndex = 0;  // Keeps track of which set of job posts is visible
const jobSlider = document.querySelector('.job-slider');
const prevButton = document.querySelector('.prev-btn');
const nextButton = document.querySelector('.next-btn');
const jobBoxes = document.querySelectorAll('.job-box');
const totalJobs = jobBoxes.length;
const jobsPerPage = 4;  // Number of boxes visible at once

// Function to update visibility of job posts
function updateSlider() {
    // Hide all job boxes
    jobBoxes.forEach((box, index) => {
        if (index >= currentIndex && index < currentIndex + jobsPerPage) {
            box.style.display = 'block';
        } else {
            box.style.display = 'none';
        }
    });

    // Enable/disable previous button
    if (currentIndex === 0) {
        prevButton.disabled = true;
        prevButton.style.backgroundColor = 'white'; // Change background color to white
        prevButton.querySelector('i').style.color = '#1E88E5'; // Change icon color to blue
    } else {
        prevButton.disabled = false;
        prevButton.style.backgroundColor = '#1E88E5'; // Restore background color to blue
        prevButton.querySelector('i').style.color = 'white'; // Restore icon color to white
    }
}

// Event listener for the previous button
prevButton.addEventListener('click', () => {
    if (currentIndex > 0) {
        currentIndex -= jobsPerPage;
    }
    updateSlider();
});

// Event listener for the next button
nextButton.addEventListener('click', () => {
    if (currentIndex < totalJobs - jobsPerPage) {
        currentIndex += jobsPerPage;
    }
    updateSlider();
});

// Initialize the slider to show the first 4 jobs
updateSlider();
