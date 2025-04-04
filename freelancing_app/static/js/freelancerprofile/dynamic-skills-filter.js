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
    });
    
    skillCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            updateSelectedSkills();
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
                }
            });
        });
    }
    
    updateSelectedSkills();
});