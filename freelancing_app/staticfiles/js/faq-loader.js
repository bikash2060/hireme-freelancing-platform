let faqIndex = 3; 
const totalFaqs = document.querySelectorAll('.faq-item').length;
const faqs = document.querySelectorAll('.faq-item');
const showMoreButton = document.getElementById('show-more');
const showLessButton = document.getElementById('show-less');

function showMoreFAQ() {
    for (let i = faqIndex; i < faqIndex + 3 && i < totalFaqs; i++) {
        faqs[i].style.display = 'block';
    }
    faqIndex += 3;

    
    if (faqIndex >= totalFaqs) {
        showMoreButton.style.display = 'none'; 
    }

    if (faqIndex > 3) {
        showLessButton.style.display = 'inline-block';
    }
}

function showLessFAQ() {
    for (let i = 3; i < totalFaqs; i++) {
        faqs[i].style.display = 'none';
    }
    faqIndex = 3;

    showMoreButton.style.display = 'inline-block'; 
    showLessButton.style.display = 'none'; 
}

window.onload = () => {
    for (let i = 3; i < faqs.length; i++) {
        faqs[i].style.display = 'none';
    }

    if (totalFaqs > 3) {
        showLessButton.style.display = 'none'; 
    } else {
        showLessButton.style.display = 'none'; 
    }
    
    if (totalFaqs > 3) {
        showMoreButton.style.display = 'inline-block'; 
    } else {
        showMoreButton.style.display = 'none'; 
    }
};
