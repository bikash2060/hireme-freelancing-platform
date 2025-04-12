document.addEventListener('DOMContentLoaded', function() {
    const fixedOption = document.getElementById('fixed_budget_option');
    const rangeOption = document.getElementById('range_budget_option');
    const fixedFields = document.getElementById('fixed-budget-fields');
    const rangeFields = document.getElementById('range-budget-fields');
    
    function toggleBudgetFields() {
        if (rangeOption.checked) {
            rangeFields.classList.remove('hidden');
            fixedFields.classList.add('hidden');
        } else {
            fixedFields.classList.remove('hidden');
            rangeFields.classList.add('hidden');
        }
    }
    
    // Set initial state
    toggleBudgetFields();
    
    // Add event listeners
    fixedOption.addEventListener('change', toggleBudgetFields);
    rangeOption.addEventListener('change', toggleBudgetFields);
});