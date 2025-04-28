document.addEventListener('DOMContentLoaded', function () {
    const skillsSearch = document.getElementById('skills_search');
    const skillsOptions = document.getElementById('skills-options');
    const selectedSkillsList = document.querySelector('.selected-skills-list');

    const noResultsMsg = document.createElement('div');
    noResultsMsg.className = 'no-results-msg';
    noResultsMsg.textContent = 'No matching skills found';
    noResultsMsg.style.display = 'none';
    skillsOptions.parentNode.insertBefore(noResultsMsg, skillsOptions.nextSibling);

    skillsOptions.addEventListener('change', function (e) {
        if (e.target && e.target.name === 'skills') {
            const skillOption = e.target.closest('.skill-option');
            const levelSelector = skillOption.querySelector('.skill-level-selector');

            if (e.target.checked) {
                levelSelector.style.display = 'block';
            } else {
                levelSelector.style.display = 'none';
                levelSelector.querySelector('select').value = 'intermediate';
            }

            updateSelectedSkills();
            moveSelectedSkillsToTop();
        }
    });

    document.querySelectorAll('.skill-level-selector select').forEach(select => {
        select.addEventListener('click', e => e.stopPropagation());
        select.addEventListener('change', () => {
            updateSelectedSkills();
            moveSelectedSkillsToTop();
        });
    });

    skillsSearch.addEventListener('input', function () {
        const searchTerm = this.value.toLowerCase().trim();
        const skillOptions = skillsOptions.querySelectorAll('.skill-option');
        let hasMatches = false;

        skillOptions.forEach(option => {
            const skillName = option.querySelector('.skill-name').textContent.toLowerCase();
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

    document.querySelectorAll('input[name="skills"]:checked').forEach(checkbox => {
        const skillOption = checkbox.closest('.skill-option');
        const levelSelector = skillOption.querySelector('.skill-level-selector');
        levelSelector.style.display = 'block';
    });

    function updateSelectedSkills() {
        selectedSkillsList.innerHTML = '';
        const checkedSkills = document.querySelectorAll('input[name="skills"]:checked');

        checkedSkills.forEach(checkbox => {
            const skillId = checkbox.id;
            const skillName = checkbox.closest('.skill-option').querySelector('.skill-name').textContent;
            const levelSelector = checkbox.closest('.skill-option').querySelector('.skill-level-selector select');
            const selectedLevel = levelSelector ? levelSelector.value : 'intermediate';
            const levelText = levelSelector ? levelSelector.options[levelSelector.selectedIndex].text : 'Intermediate';

            const skillElement = document.createElement('div');
            skillElement.className = 'selected-skill';
            skillElement.innerHTML = `
                ${skillName} <span class="skill-level-badge">${levelText}</span>
                <span class="remove-skill" data-skill-id="${skillId}">
                    <i class="fas fa-times"></i>
                </span>
            `;

            selectedSkillsList.appendChild(skillElement);
        });

        document.querySelectorAll('.remove-skill').forEach(removeBtn => {
            removeBtn.addEventListener('click', function (e) {
                e.stopPropagation();
                const skillId = this.getAttribute('data-skill-id');
                const checkbox = document.getElementById(skillId);
                if (checkbox) {
                    checkbox.checked = false;
                    const skillOption = checkbox.closest('.skill-option');
                    const levelSelector = skillOption.querySelector('.skill-level-selector');
                    levelSelector.style.display = 'none';
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

    updateSelectedSkills(); 
    moveSelectedSkillsToTop(); 
});
