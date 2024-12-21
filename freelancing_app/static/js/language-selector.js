document.addEventListener('DOMContentLoaded', () => {
    const languageSearch = document.getElementById('language-search');
    const languageOptions = document.querySelectorAll('.language-option');
    const selectedLanguagesContainer = document.getElementById('selected-languages');
    const languagesInput = document.getElementById('languages');
    
    let selectedLanguages = [];

    // Predefined languages (e.g. from database)
    const predefinedLanguages = ['English', 'Nepali'];

    // Display predefined selected languages
    function displayPredefinedLanguages() {
        predefinedLanguages.forEach(language => {
            const div = document.createElement('div');
            div.classList.add('selected-language');
            div.innerHTML = `<span>${language}</span>
                             <span class="remove-language" data-language="${language}"><i class="fas fa-times"></i></span>`;
            selectedLanguagesContainer.appendChild(div);
        });
    }

    // Call the function to display predefined languages
    displayPredefinedLanguages();

    // Filter language options based on search
    languageSearch.addEventListener('input', () => {
        const query = languageSearch.value.toLowerCase();

        // Show/hide language options based on the search query
        languageOptions.forEach(option => {
            const language = option.textContent.toLowerCase();
            if (query && language.includes(query) && !selectedLanguages.includes(language)) {
                option.style.display = 'block'; // Show if it matches the query
            } else {
                option.style.display = 'none'; // Hide if it doesn't match
            }
        });

        // If the search bar is empty, hide all options
        if (!query) {
            languageOptions.forEach(option => option.style.display = 'none');
        }
    });

    // Select a language option
    languageOptions.forEach(option => {
        option.addEventListener('click', () => {
            const language = option.getAttribute('data-language');
            
            // Allow selecting only one language
            if (selectedLanguages.length > 0) {
                alert("You can only select one language at a time.");
                return;
            }

            selectedLanguages.push(language);
            option.style.display = 'none'; // Hide the language options after selection
            updateSelectedLanguages();
        });
    });

    // Update the selected languages display
    function updateSelectedLanguages() {
        selectedLanguagesContainer.innerHTML = ''; // Clear the existing selected languages

        // Add predefined languages to the display
        displayPredefinedLanguages();

        // Add the newly selected language
        selectedLanguages.forEach(language => {
            const div = document.createElement('div');
            div.classList.add('selected-language');
            div.innerHTML = `<span>${language.charAt(0).toUpperCase() + language.slice(1)}</span>
                             <span class="remove-language" data-language="${language}"><i class="fas fa-times"></i></span>`;
            selectedLanguagesContainer.appendChild(div);
        });

        // Update the hidden input field with selected languages
        languagesInput.value = selectedLanguages.join(',');
    }

    // Remove a language from the selected list
    selectedLanguagesContainer.addEventListener('click', (e) => {
        if (e.target.classList.contains('remove-language') || e.target.tagName.toLowerCase() === 'i') {
            const language = e.target.getAttribute('data-language') || e.target.parentElement.getAttribute('data-language');
            selectedLanguages = selectedLanguages.filter(lang => lang !== language);
            updateSelectedLanguages();

            // Also, show the language option again when removed
            const option = document.querySelector(`.language-option[data-language="${language}"]`);
            if (option) {
                option.style.display = 'block';
            }
        }
    });
});
