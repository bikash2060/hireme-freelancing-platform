document.addEventListener("DOMContentLoaded", () => {
    const skillsSearchInput = document.getElementById("skills-search");
    const skillsList = document.getElementById("skills-list");
    const noSkillsMessage = document.createElement('div');
    noSkillsMessage.className = 'no-skills-message';
    noSkillsMessage.innerText = 'No skills found';

    const filterSkills = () => {
        const searchValue = skillsSearchInput.value.toLowerCase().trim();
        const skillItems = skillsList.querySelectorAll(".skill-item");
        let foundMatchingSkills = false;

        skillItems.forEach((item) => {
            const skillName = item.dataset.skillName;

            if (skillName.includes(searchValue)) {
                item.style.display = "block";
                foundMatchingSkills = true;
            } else {
                item.style.display = "none";
            }
        });

        if (searchValue && !foundMatchingSkills) {
            if (!document.querySelector('.no-skills-message')) {
                skillsList.appendChild(noSkillsMessage);
            }
        } else {
            const existingMessage = document.querySelector('.no-skills-message');
            if (existingMessage) {
                existingMessage.remove();
            }
        }
    };

    skillsSearchInput.addEventListener("input", filterSkills);

    skillsSearchInput.addEventListener("keypress", (event) => {
        if (event.key === "Enter") {
            event.preventDefault();
        }
    });
});

document.addEventListener("DOMContentLoaded", () => {
    const skillsList = document.getElementById("skills-list");
    const selectedSkillsContainer = document.getElementById("selected-skills");

    function addSkill(skillId, skillName) {
        if (document.querySelector(`[data-skill-id="${skillId}"]`)) return;

        const skillChip = document.createElement("div");
        skillChip.className = "skill-chip";
        skillChip.dataset.skillId = skillId;
        skillChip.innerHTML = `
            ${skillName}
            <span class="remove-skill" data-skill-id="${skillId}">
                <i class="fa-solid fa-minus"></i>
            </span>
        `;

        selectedSkillsContainer.appendChild(skillChip);

        skillChip.querySelector(".remove-skill").addEventListener("click", () => {
            removeSkill(skillId);
        });
    }

    function removeSkill(skillId) {
        const skillChip = document.querySelector(`[data-skill-id="${skillId}"]`);
        if (skillChip) skillChip.remove();

        const checkbox = skillsList.querySelector(`input[value="${skillId}"]`);
        if (checkbox) checkbox.checked = false;
    }

    skillsList.addEventListener("change", (event) => {
        const checkbox = event.target;
        const skillId = checkbox.value;
        const skillName = checkbox.dataset.skillName;

        if (checkbox.checked) {
            addSkill(skillId, skillName);
        } else {
            removeSkill(skillId);
        }
    });

    const checkedSkills = skillsList.querySelectorAll("input[name='skills-select']:checked");
    checkedSkills.forEach((checkbox) => {
        const skillId = checkbox.value;
        const skillName = checkbox.dataset.skillName;
        addSkill(skillId, skillName);
    });
});
