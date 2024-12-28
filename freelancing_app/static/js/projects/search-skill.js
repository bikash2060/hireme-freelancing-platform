document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('skills-search');
    const skillsSelect = document.getElementById('skills-select');
    const selectedSkillsContainer = document.getElementById('selected-skills');
    let selectedSkills = [];

    // Function to filter the skills based on search input
    searchInput.addEventListener('input', function () {
        const query = searchInput.value.toLowerCase();
        const options = skillsSelect.querySelectorAll('option');
        let matches = false;

        options.forEach(option => {
            const skill = option.value.toLowerCase();
            const isMatch = skill.includes(query);
            option.style.display = isMatch ? 'block' : 'none';
            if (isMatch) matches = true;
        });

        // Show the select dropdown if there are matches
        skillsSelect.style.display = matches && query.length > 0 ? 'block' : 'none';
    });

    // Event listener for selecting a skill from the dropdown
    skillsSelect.addEventListener('change', function () {
        const selectedOption = skillsSelect.options[skillsSelect.selectedIndex];
        const selectedSkill = selectedOption.value;

        if (!selectedSkills.includes(selectedSkill)) {
            selectedSkills.push(selectedSkill);
            updateSelectedSkills();
        }

        // Hide the dropdown after selection
        skillsSelect.style.display = 'none';
        searchInput.value = ''; // Clear the search input
    });

    // Function to update the displayed selected skills
    function updateSelectedSkills() {
        selectedSkillsContainer.innerHTML = ''; // Clear current selected skills

        selectedSkills.forEach(skill => {
            const skillDiv = document.createElement('div');
            skillDiv.classList.add('selected-skill');
            skillDiv.textContent = skill;
            const removeButton = document.createElement('span');
            removeButton.textContent = '×';
            removeButton.classList.add('remove');
            removeButton.addEventListener('click', function () {
                selectedSkills = selectedSkills.filter(s => s !== skill);
                updateSelectedSkills();
            });
            skillDiv.appendChild(removeButton);
            selectedSkillsContainer.appendChild(skillDiv);
        });
    }
});
