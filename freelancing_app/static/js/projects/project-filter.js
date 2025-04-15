document.addEventListener('DOMContentLoaded', function () {
    // Reset filters on page load by removing URL parameters
    if (window.location.search) {
        window.history.replaceState({}, document.title, window.location.pathname);
    }

    const filters = document.querySelectorAll('input[type="checkbox"], .search-input');

    filters.forEach(input => {
        input.addEventListener('change', () => {
            applyFilters();
        });
    });

    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        searchInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                applyFilters();
            }
        });
    }

    // Category search functionality
    const categorySearchInput = document.querySelector('.category-search-input');
    if (categorySearchInput) {
        categorySearchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const categoryItems = document.querySelectorAll('.category-items .dropdown-item');
            const categoryItemsContainer = document.querySelector('.category-items');
            let hasMatches = false;
            
            categoryItems.forEach(item => {
                const categoryName = item.textContent.trim().toLowerCase();
                if (categoryName.includes(searchTerm)) {
                    item.style.display = 'block';
                    hasMatches = true;
                } else {
                    item.style.display = 'none';
                }
            });

            // Remove existing no-results message if it exists
            const existingNoResults = categoryItemsContainer.querySelector('.no-categories-found');
            if (existingNoResults) {
                existingNoResults.remove();
            }

            // Add no-results message if no matches found
            if (!hasMatches) {
                const noResultsMessage = document.createElement('div');
                noResultsMessage.className = 'no-categories-found';
                noResultsMessage.style.padding = '10px';
                noResultsMessage.style.textAlign = 'center';
                noResultsMessage.style.color = '#666';
                noResultsMessage.textContent = 'No categories found matching your search';
                categoryItemsContainer.appendChild(noResultsMessage);
            }
        });
    }

    function applyFilters() {
        const params = new URLSearchParams();

        const searchVal = document.querySelector('.search-input').value;
        if (searchVal.trim()) {
            params.append('search', searchVal.trim());
        }

        document.querySelectorAll('input[type="checkbox"]:checked').forEach(checkbox => {
            params.append(checkbox.name, checkbox.value);
        });

        const url = `${window.location.pathname}?${params.toString()}`;
        window.location.href = url;
    }

    const resetBtn = document.querySelector('.clear-filters-btn');
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            window.location.href = window.location.pathname;
        });
    }
});
