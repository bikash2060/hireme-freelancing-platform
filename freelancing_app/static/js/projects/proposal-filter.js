document.addEventListener('DOMContentLoaded', function () {
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

            const existingNoResults = categoryItemsContainer.querySelector('.no-categories-found');
            if (existingNoResults) {
                existingNoResults.remove();
            }

            if (!hasMatches) {
                const noResultsMessage = document.createElement('div');
                noResultsMessage.className = 'no-categories-found';
                noResultsMessage.style.padding = '10px';
                noResultsMessage.style.textAlign = 'center';
                noResultsMessage.style.color = '#666';
                noResultsMessage.style.fontSize = '14px';
                noResultsMessage.textContent = 'No categories found';
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

function removeFilterParam(paramName) {
    const url = new URL(window.location.href);
    url.searchParams.delete(paramName);
    window.location.href = url.toString();
}

function removeMultiFilterParam(paramName, valueToRemove) {
    const url = new URL(window.location.href);
    let params = url.searchParams.getAll(paramName);
    params = params.filter(val => val !== valueToRemove);
    url.searchParams.delete(paramName);
    params.forEach(val => url.searchParams.append(paramName, val));
    window.location.href = url.toString();
}

