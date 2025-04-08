document.addEventListener('DOMContentLoaded', function () {
    const currentlyWorkingCheckbox = document.getElementById('currently_working');
    const endDateInput = document.getElementById('end_date');

    if (currentlyWorkingCheckbox && endDateInput) {
        const toggleEndDate = () => {
            if (currentlyWorkingCheckbox.checked) {
                endDateInput.disabled = true;
                endDateInput.value = '';
                endDateInput.style.backgroundColor = '#f8f9fa';
                endDateInput.style.cursor = 'not-allowed';
            } else {
                endDateInput.disabled = false;
                endDateInput.style.backgroundColor = '';
                endDateInput.style.cursor = '';
            }
        };

        toggleEndDate(); 

        currentlyWorkingCheckbox.addEventListener('change', toggleEndDate);
    }
});


document.addEventListener('DOMContentLoaded', function () {
    const currentlyStudyingCheckbox = document.getElementById('currently_studying');
    const endDateInput = document.getElementById('end_date');

    if (currentlyStudyingCheckbox && endDateInput) {
        const toggleEndDate = () => {
            if (currentlyStudyingCheckbox.checked) {
                endDateInput.disabled = true;
                endDateInput.value = '';
                endDateInput.style.backgroundColor = '#f8f9fa';
                endDateInput.style.cursor = 'not-allowed';
            } else {
                endDateInput.disabled = false;
                endDateInput.style.backgroundColor = '';
                endDateInput.style.cursor = '';
            }
        };

        toggleEndDate();
        currentlyStudyingCheckbox.addEventListener('change', toggleEndDate);
    }
});
