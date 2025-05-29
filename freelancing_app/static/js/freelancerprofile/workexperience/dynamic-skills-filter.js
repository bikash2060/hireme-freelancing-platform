document.addEventListener('DOMContentLoaded', function () {
    const skillsSearch = document.getElementById('skills_search');
    const skillsOptions = document.getElementById('skills-options');
    const selectedSkillsList = document.querySelector('.selected-skills-list');

    // Add debug logging
    console.log('Skills search element:', skillsSearch);
    console.log('Skills options element:', skillsOptions);
    console.log('Selected skills list element:', selectedSkillsList);

    const noResultsMsg = document.createElement('div');
    noResultsMsg.className = 'no-results-msg';
    noResultsMsg.textContent = 'No matching skills found';
    noResultsMsg.style.display = 'none';
    skillsOptions.parentNode.insertBefore(noResultsMsg, skillsOptions.nextSibling);

    // Initialize selected skills on page load
    function initializeSelectedSkills() {
        const checkedSkills = document.querySelectorAll('input[name="skills"]:checked');
        console.log('Initializing selected skills:', checkedSkills.length);
        updateSelectedSkills();
        moveSelectedSkillsToTop();
    }

    // Handle checkbox change using event delegation
    skillsOptions.addEventListener('change', function (e) {
        if (e.target && e.target.name === 'skills') {
            updateSelectedSkills();
            moveSelectedSkillsToTop();
        }
    });

    // Real-time search
    skillsSearch.addEventListener('input', function () {
        console.log('Search input event triggered');
        const searchTerm = this.value.toLowerCase().trim();
        console.log('Search term:', searchTerm);
        
        const skillOptions = skillsOptions.querySelectorAll('.skill-option');
        console.log('Number of skill options:', skillOptions.length);
        
        let hasMatches = false;

        skillOptions.forEach(option => {
            const skillLabel = option.querySelector('label');
            if (!skillLabel) {
                console.log('No label found for option:', option);
                return;
            }
            const skillName = skillLabel.textContent.toLowerCase();
            console.log('Checking skill:', skillName);
            
            if (searchTerm === '' || skillName.includes(searchTerm)) {
                option.style.display = 'flex';
                hasMatches = true;
            } else {
                option.style.display = 'none';
            }
        });

        if (searchTerm !== '' && !hasMatches) {
            noResultsMsg.style.display = 'block';
            skillsOptions.style.display = 'none';
        } else {
            noResultsMsg.style.display = 'none';
            skillsOptions.style.display = 'block';
        }

        updateSelectedSkills();
        moveSelectedSkillsToTop();
    });

    function updateSelectedSkills() {
        selectedSkillsList.innerHTML = '';
        const checkedSkills = document.querySelectorAll('input[name="skills"]:checked');
        console.log('Updating selected skills:', checkedSkills.length);

        checkedSkills.forEach(checkbox => {
            const skillId = checkbox.id;
            const skillLabel = checkbox.closest('.skill-option').querySelector('label');
            if (!skillLabel) {
                console.log('No label found for checked skill:', skillId);
                return;
            }
            const skillName = skillLabel.textContent;

            const skillElement = document.createElement('div');
            skillElement.className = 'selected-skill';
            skillElement.innerHTML = `
                ${skillName}
                <span class="remove-skill" data-skill-id="${skillId}">
                    <i class="fas fa-times"></i>
                </span>
            `;

            selectedSkillsList.appendChild(skillElement);
        });

        // Remove skill event
        document.querySelectorAll('.remove-skill').forEach(removeBtn => {
            removeBtn.addEventListener('click', function (e) {
                e.stopPropagation();
                const skillId = this.getAttribute('data-skill-id');
                const checkbox = document.getElementById(skillId);
                if (checkbox) {
                    checkbox.checked = false;
                    updateSelectedSkills();
                    moveSelectedSkillsToTop();
                }
            });
        });
    }

    function moveSelectedSkillsToTop() {
        const allSkillOptions = Array.from(skillsOptions.querySelectorAll('.skill-option'));
        const selected = [];
        const unselected = [];

        allSkillOptions.forEach(option => {
            const checkbox = option.querySelector('input[name="skills"]');
            if (checkbox && checkbox.checked) {
                selected.push(option);
            } else {
                unselected.push(option);
            }
        });

        skillsOptions.innerHTML = '';
        [...selected, ...unselected].forEach(option => {
            skillsOptions.appendChild(option);
        });
    }

    // Initialize everything on page load
    initializeSelectedSkills();
});
