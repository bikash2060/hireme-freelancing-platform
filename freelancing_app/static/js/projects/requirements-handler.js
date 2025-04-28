document.addEventListener('DOMContentLoaded', function () {
    const requirementsList = document.getElementById('requirements-list');
    const addRequirementBtn = document.getElementById('add-requirement');
    const clearRequirementsBtn = document.getElementById('clear-requirements');
    const hiddenInput = document.getElementById('key_requirements');

    function initializeRequirements() {
        if (hiddenInput && hiddenInput.value) {
            const decodedValue = hiddenInput.value.replace(/\\u000A/g, '\n');
            const existingReqs = decodedValue.split('\n').filter(req => req.trim());
            if (existingReqs.length > 0) {
                requirementsList.innerHTML = '';
                existingReqs.forEach(req => {
                    const cleanReq = req.trim().replace(/\\u000A/g, '');
                    if (cleanReq) {
                        addRequirementItem(cleanReq);
                    }
                });
            } else {
                updateEmptyState();
            }
        } else {
            updateEmptyState();
        }
    }

    initializeRequirements();

    updateHiddenInput();

    addRequirementBtn.addEventListener('click', () => {
        addRequirementItem();
    });

    clearRequirementsBtn.addEventListener('click', () => {
        requirementsList.innerHTML = '';
        updateEmptyState();
        updateHiddenInput();
    });

    requirementsList.addEventListener('click', function (e) {
        if (e.target.closest('.remove-req-btn')) {
            e.target.closest('.requirement-item').remove();
            updateHiddenInput();
            updateEmptyState();
        }
    });

    requirementsList.addEventListener('input', function (e) {
        if (e.target.classList.contains('requirement-input')) {
            updateHiddenInput();
        }
    });

    function addRequirementItem(value = '') {
        const emptyState = requirementsList.querySelector('.empty-state');
        if (emptyState) emptyState.remove();

        const li = document.createElement('li');
        li.className = 'requirement-item';
        li.innerHTML = `
            <input type="text" class="requirement-input" placeholder="Type requirement here" value="${value.replace(/"/g, '&quot;')}">
            <button type="button" class="remove-req-btn" title="Remove requirement">
                <i class="fas fa-times"></i>
            </button>
        `;
        requirementsList.appendChild(li);
        if (!value) {
            li.querySelector('.requirement-input').focus();
        }
        updateHiddenInput();
    }

    function updateHiddenInput() {
        const items = requirementsList.querySelectorAll('.requirement-item:not(.empty-state)');
        const requirements = Array.from(items)
            .map(item => item.querySelector('.requirement-input').value.trim())
            .filter(val => val);
        hiddenInput.value = requirements.join('\n');
    }

    function updateEmptyState() {
        const existingEmptyState = requirementsList.querySelector('.empty-state');
        if (existingEmptyState) {
            existingEmptyState.remove();
        }

        if (requirementsList.querySelectorAll('.requirement-item:not(.empty-state)').length === 0) {
            const emptyState = document.createElement('li');
            emptyState.className = 'requirement-item empty-state';
            emptyState.innerHTML = `
                <i class="fas fa-inbox"></i>
                <span>No requirements added yet</span>
            `;
            requirementsList.appendChild(emptyState);
        }
    }
});