document.addEventListener("DOMContentLoaded", () => {
    const languageSearchInput = document.getElementById("language-search");
    const languagesList = document.getElementById("languages-list");
    const noLanguagesMessage = document.createElement('div');
    noLanguagesMessage.className = 'no-languages-message';
    noLanguagesMessage.innerText = 'No language found';
    const selectedLanguagesContainer = document.getElementById("selected-languages");

    const filterLanguages = () => {
        const searchValue = languageSearchInput.value.toLowerCase().trim();
        const languageItems = languagesList.querySelectorAll(".language-item");
        let foundMatchingLanguages = false;

        languageItems.forEach((item) => {
            const languageName = item.dataset.languageName.toLowerCase();

            if (languageName.includes(searchValue)) {
                item.style.display = "block";
                foundMatchingLanguages = true;
            } else {
                item.style.display = "none";
            }
        });

        if (searchValue && !foundMatchingLanguages) {
            if (!document.querySelector('.no-languages-message')) {
                languagesList.appendChild(noLanguagesMessage);
            }
        } else {
            const existingMessage = document.querySelector('.no-languages-message');
            if (existingMessage) {
                existingMessage.remove();
            }
        }
    };

    function addLanguage(languageName) {
        if (selectedLanguagesContainer.querySelector(`.language-chip[data-language-name="${languageName}"]`)) return;

        const languageChip = document.createElement("div");
        languageChip.className = "language-chip";
        languageChip.dataset.languageName = languageName;
        languageChip.innerHTML = `
            ${languageName}
            <span class="remove-language" data-language-name="${languageName}">
                <i class="fa-solid fa-minus"></i>
            </span>
        `;

        selectedLanguagesContainer.appendChild(languageChip);

        languageChip.querySelector(".remove-language").addEventListener("click", () => {
            removeLanguage(languageName);
        });
    }

    function removeLanguage(languageName) {
        const languageChip = document.querySelector(`.language-chip[data-language-name="${languageName}"]`);
        if (languageChip) languageChip.remove();

        const checkbox = languagesList.querySelector(`input[value="${languageName}"]`);
        if (checkbox) checkbox.checked = false;
    }

    languagesList.addEventListener("change", (event) => {
        const checkbox = event.target;
        const languageName = checkbox.parentElement.dataset.languageName;

        if (checkbox.checked) {
            addLanguage(languageName);
        } else {
            removeLanguage(languageName);
        }
    });

    const checkedLanguages = languagesList.querySelectorAll("input[name='languages-select']:checked");
    checkedLanguages.forEach((checkbox) => {
        const languageName = checkbox.parentElement.dataset.languageName;
        if (languageName) {
            addLanguage(languageName);
        }
    });

    languageSearchInput.addEventListener("input", filterLanguages);

    languageSearchInput.addEventListener("keypress", (event) => {
        if (event.key === "Enter") {
            event.preventDefault();
        }
    });
});