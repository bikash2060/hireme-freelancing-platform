document.addEventListener('DOMContentLoaded', function() {
    const skillsSearch = document.getElementById('skills_search');
    const skillsOptions = document.getElementById('skills-options');
    const selectedSkillsList = document.querySelector('.selected-skills-list');
    const skillCheckboxes = document.querySelectorAll('input[name="skills"]');
    
    const noResultsMsg = document.createElement('div');
    noResultsMsg.className = 'no-results-msg';
    noResultsMsg.textContent = 'No matching skills found';
    noResultsMsg.style.display = 'none';
    skillsOptions.parentNode.insertBefore(noResultsMsg, skillsOptions.nextSibling);
    
    // Function to sort skills with checked ones first
    function sortSkillsWithSelectedFirst() {
        const container = document.getElementById('skills-options');
        const skills = Array.from(container.querySelectorAll('.skill-option'));
        
        // Sort skills - checked ones first, then alphabetically
        skills.sort((a, b) => {
            const aChecked = a.querySelector('input').checked;
            const bChecked = b.querySelector('input').checked;
            
            if (aChecked && !bChecked) return -1;
            if (!aChecked && bChecked) return 1;
            
            const aName = a.querySelector('label').textContent.toLowerCase();
            const bName = b.querySelector('label').textContent.toLowerCase();
            return aName.localeCompare(bName);
        });
        
        // Reappend sorted skills
        skills.forEach(skill => {
            container.appendChild(skill);
        });
    }
    
    skillsSearch.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase().trim();
        const skillOptions = skillsOptions.querySelectorAll('.skill-option');
        let hasMatches = false;
        
        skillOptions.forEach(option => {
            const skillName = option.querySelector('label').textContent.toLowerCase();
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
        
        // Re-sort when searching to keep checked items on top
        if (searchTerm === '') {
            sortSkillsWithSelectedFirst();
        }
    });
    
    skillCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            updateSelectedSkills();
            sortSkillsWithSelectedFirst();
        });
    });
    
    function updateSelectedSkills() {
        selectedSkillsList.innerHTML = '';
        
        const checkedSkills = document.querySelectorAll('input[name="skills"]:checked');
        
        checkedSkills.forEach(checkbox => {
            const skillId = checkbox.id;
            const skillName = checkbox.nextElementSibling.nextElementSibling.textContent; 
            
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
        
        document.querySelectorAll('.remove-skill').forEach(removeBtn => {
            removeBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                const skillId = this.getAttribute('data-skill-id');
                const checkbox = document.getElementById(skillId);
                if (checkbox) {
                    checkbox.checked = false;
                    updateSelectedSkills();
                    sortSkillsWithSelectedFirst();
                }
            });
        });
    }
    
    // Initial setup
    sortSkillsWithSelectedFirst();
    updateSelectedSkills();
});