let faqIndex = 3; // Start with the first 3 questions visible
const totalFaqs = document.querySelectorAll('.faq-item').length;
const faqs = document.querySelectorAll('.faq-item');
const showMoreButton = document.getElementById('show-more');
const showLessButton = document.getElementById('show-less');

// Function to show more FAQs
function showMoreFAQ() {
    for (let i = faqIndex; i < faqIndex + 3 && i < totalFaqs; i++) {
        faqs[i].style.display = 'block';
    }
    faqIndex += 3;

    // If all FAQs are displayed, hide the Show More button and show the Show Less button
    if (faqIndex >= totalFaqs) {
        showMoreButton.style.display = 'none'; // Hide Show More button
    }

    // Show the Show Less button only if there are more than 3 questions displayed
    if (faqIndex > 3) {
        showLessButton.style.display = 'inline-block';
    }
}

// Function to show less FAQs
function showLessFAQ() {
    for (let i = 3; i < totalFaqs; i++) {
        faqs[i].style.display = 'none';
    }
    faqIndex = 3;

    showMoreButton.style.display = 'inline-block'; // Show Show More button
    showLessButton.style.display = 'none'; // Hide Show Less button
}

// Initial state: Hide all FAQs except the first 3
window.onload = () => {
    for (let i = 3; i < faqs.length; i++) {
        faqs[i].style.display = 'none';
    }

    // Show or hide the Show Less button based on the total number of FAQs
    if (totalFaqs > 3) {
        showLessButton.style.display = 'none'; // Hide Show Less initially
    } else {
        showLessButton.style.display = 'none'; // No Show Less button if there are only 3 questions
    }
    
    // Show More button is shown initially if there are more than 3 questions
    if (totalFaqs > 3) {
        showMoreButton.style.display = 'inline-block'; // Show Show More button
    } else {
        showMoreButton.style.display = 'none'; // Hide Show More button if there are only 3 questions
    }
};
