 // Toggle FAQ Items
 function toggleFaq(element) {
    const faqItem = element.closest('.faq-item');
    
    if (faqItem.classList.contains('active')) {
        faqItem.classList.remove('active');
    } else {
        faqItem.classList.add('active');
    }
}

// Show More/Less Toggle
function toggleShowMore() {
    const hiddenFaqs = document.querySelector('.hidden-faqs');
    const showMoreBtn = document.getElementById('show-more-btn');
    
    if (hiddenFaqs.style.display === 'none') {
        hiddenFaqs.style.display = 'block';
        showMoreBtn.textContent = 'Show Less';
    } else {
        hiddenFaqs.style.display = 'none';
        showMoreBtn.textContent = 'Show More';
    }
}