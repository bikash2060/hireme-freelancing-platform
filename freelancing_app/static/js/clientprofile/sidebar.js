const navLinks = document.querySelectorAll('.nav_link');
const contentSections = document.querySelectorAll('.user-basic-info, .user-password');

const sectionMapping = {
    "My Info": "user-basic-info",
    "Change Password": "user-password",
};

const hideAllSections = () => {
    contentSections.forEach(section => {
        section.style.display = 'none';
    });
};

const showSection = (sectionClass) => {
    const section = document.querySelector(`.${sectionClass}`);
    if (section) {
        section.style.display = 'block';
    }
};

const removeActiveClass = () => {
    navLinks.forEach(link => {
        link.classList.remove('active');
    });
};

hideAllSections();
showSection('user-basic-info');

const defaultLink = Array.from(navLinks).find(link => link.textContent.trim() === "My Info");
if (defaultLink) {
    defaultLink.classList.add('active');
}

navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault(); 

        const linkText = link.textContent.trim();

        const targetClass = sectionMapping[linkText];

        if (targetClass) {
            hideAllSections();
            showSection(targetClass);

            removeActiveClass();
            link.classList.add('active');
        }
    });
});

