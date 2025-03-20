function toggleFilterGroup(element) {
    const filterGroup = element.closest('.filter-group');
    const toggleIcon = element.querySelector('.toggle-icon');
    
    filterGroup.classList.toggle('closed');
    
    if (filterGroup.classList.contains('closed')) {
        toggleIcon.innerHTML = '▶';
    } else {
        toggleIcon.innerHTML = '▼';
    }
}

document.addEventListener("DOMContentLoaded", function() {
    const filterGroups = document.querySelectorAll('.filter-group');
    filterGroups.forEach(group => group.classList.add('closed'));
});