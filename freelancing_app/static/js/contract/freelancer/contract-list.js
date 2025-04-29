document.addEventListener('DOMContentLoaded', function() {
    const contractCards = document.querySelectorAll('.contract-card');
    const searchInput = document.getElementById('contract-search');
    const statusCheckboxes = document.querySelectorAll('.dropdown-content input[type="checkbox"]');
    const sortOptions = document.querySelectorAll('input[name="sort"]');
    
    searchInput.addEventListener('input', filterContracts);
    
    statusCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', handleStatusFilter);
    });
    
    sortOptions.forEach(option => {
        option.addEventListener('change', sortContracts);
    });
    
    initializeDropdowns();
    function filterContracts() {
        const searchValue = searchInput.value.toLowerCase();
        const selectedStatuses = getSelectedStatuses();
        
        contractCards.forEach(card => {
            const cardTitle = card.querySelector('.contract-title').textContent.toLowerCase();
            const freelancerName = card.querySelector('.info-value').textContent.toLowerCase();
            const cardStatus = card.getAttribute('data-status');
            
            const matchesSearch = cardTitle.includes(searchValue) || freelancerName.includes(searchValue);
            const matchesFilter = selectedStatuses.includes('all') || selectedStatuses.includes(cardStatus);
            
            if (matchesSearch && matchesFilter) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
        
        checkNoResults();
    }
    
    function handleStatusFilter(e) {
        if (e.target.value === 'all') {
            statusCheckboxes.forEach(checkbox => {
                if (checkbox.value !== 'all') {
                    checkbox.checked = e.target.checked;
                }
            });
        } else {
            const allCheckbox = document.querySelector('input[value="all"]');
            const otherCheckboxes = Array.from(statusCheckboxes).filter(checkbox => checkbox.value !== 'all');
            const allOthersChecked = otherCheckboxes.every(checkbox => checkbox.checked);
            const noneChecked = otherCheckboxes.every(checkbox => !checkbox.checked);
            
            if (allOthersChecked) {
                allCheckbox.checked = true;
            } else if (noneChecked) {
                allCheckbox.checked = false;
                e.target.checked = true; 
            } else {
                allCheckbox.checked = false;
            }
        }
        
        filterContracts();
    }

    function getSelectedStatuses() {
        const selected = [];
        statusCheckboxes.forEach(checkbox => {
            if (checkbox.checked) {
                selected.push(checkbox.value);
            }
        });
        return selected.length ? selected : ['all'];
    }

    function sortContracts() {
        const sortValue = document.querySelector('input[name="sort"]:checked').value;
        const cardsArray = Array.from(contractCards);
        const contractsContainer = document.querySelector('.contracts-container');
        
        cardsArray.sort((a, b) => {
            switch (sortValue) {
                case 'newest':
                    return new Date(b.getAttribute('data-date')) - new Date(a.getAttribute('data-date'));
                case 'oldest':
                    return new Date(a.getAttribute('data-date')) - new Date(b.getAttribute('data-date'));
                case 'amount-high':
                    return parseFloat(b.getAttribute('data-amount')) - parseFloat(a.getAttribute('data-amount'));
                case 'amount-low':
                    return parseFloat(a.getAttribute('data-amount')) - parseFloat(b.getAttribute('data-amount'));
                default:
                    return 0;
            }
        });
        
        contractCards.forEach(card => {
            contractsContainer.removeChild(card);
        });
        
        cardsArray.forEach(card => {
            contractsContainer.appendChild(card);
        });
        
        filterContracts();
    }

    function checkNoResults() {
        const visibleCards = Array.from(contractCards).filter(card => card.style.display !== 'none');
        
        const existingMessage = document.querySelector('.no-results-message');
        if (existingMessage) {
            existingMessage.remove();
        }
        
        if (visibleCards.length === 0 && contractCards.length > 0) {
            const noResultsMessage = document.createElement('div');
            noResultsMessage.className = 'no-results-message';
            noResultsMessage.innerHTML = `
                <div class="no-data-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="11" cy="11" r="8"></circle>
                        <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                        <line x1="11" y1="8" x2="11" y2="14"></line>
                        <line x1="8" y1="11" x2="14" y2="11"></line>
                    </svg>
                </div>
                <h3>No Matching Contracts</h3>
                <p>Try adjusting your search or filters to find what you're looking for.</p>
                <button class="reset-filters-btn">Reset Filters</button>
            `;
            
            document.querySelector('.contracts-container').appendChild(noResultsMessage);
            
            document.querySelector('.reset-filters-btn').addEventListener('click', resetFilters);
        }
    }
    

    function resetFilters() {
        searchInput.value = '';
        
        statusCheckboxes.forEach(checkbox => {
            checkbox.checked = checkbox.value === 'all';
        });
        
        document.querySelector('input[value="newest"]').checked = true;
        
        filterContracts();
        sortContracts();
    }
    
    function initializeDropdowns() {
        const filterBtns = document.querySelectorAll('.filter-btn');
        
        filterBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const dropdown = this.nextElementSibling;
                if (window.innerWidth <= 768) {
                    if (dropdown.style.display === 'block') {
                        dropdown.style.display = 'none';
                    } else {
                        document.querySelectorAll('.dropdown-content').forEach(el => {
                            el.style.display = 'none';
                        });
                        dropdown.style.display = 'block';
                    }
                }
            });
        });
        
        document.addEventListener('click', function(event) {
            if (window.innerWidth <= 768) {
                if (!event.target.closest('.filter-dropdown')) {
                    document.querySelectorAll('.dropdown-content').forEach(el => {
                        el.style.display = 'none';
                    });
                }
            }
        });
    }
    
    const style = document.createElement('style');
    style.innerHTML = `
        .no-results-message {
            background-color: #fff;
            border-radius: 12px;
            padding: 40px 20px;
            text-align: center;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            margin: 20px 0;
            width: 100%;
        }
        
        .reset-filters-btn {
            display: inline-flex;
            align-items: center;
            padding: 10px 20px;
            background-color: #f1f5f9;
            color: #334155;
            font-weight: 500;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .reset-filters-btn:hover {
            background-color: #e2e8f0;
        }
    `;
    document.head.appendChild(style);
});