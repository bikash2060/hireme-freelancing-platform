document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('contract-search');
    const contractCards = document.querySelectorAll('.contract-card');
    const filterCheckboxes = document.querySelectorAll('.filter-dropdown input[type="checkbox"]');
    const sortRadios = document.querySelectorAll('.filter-dropdown input[type="radio"]');
    const contractsContainer = document.querySelector('.contracts-container');

    // Search functionality
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        
        contractCards.forEach(card => {
            const title = card.querySelector('.contract-title').textContent.toLowerCase();
            const freelancerName = card.querySelector('.freelancer-info .info-value').textContent.toLowerCase();
            const shouldShow = title.includes(searchTerm) || freelancerName.includes(searchTerm);
            card.style.display = shouldShow ? 'block' : 'none';
        });
    });

    // Filter functionality
    filterCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const selectedStatuses = Array.from(filterCheckboxes)
                .filter(cb => cb.checked)
                .map(cb => cb.value);

            contractCards.forEach(card => {
                const status = card.dataset.status;
                const shouldShow = selectedStatuses.includes('all') || selectedStatuses.includes(status);
                card.style.display = shouldShow ? 'block' : 'none';
            });
        });
    });

    // Sort functionality
    sortRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            const sortValue = this.value;
            const cardsArray = Array.from(contractCards);
            
            cardsArray.sort((a, b) => {
                switch(sortValue) {
                    case 'newest':
                        return new Date(b.dataset.date) - new Date(a.dataset.date);
                    case 'oldest':
                        return new Date(a.dataset.date) - new Date(b.dataset.date);
                    case 'amount-high':
                        return parseFloat(b.dataset.amount) - parseFloat(a.dataset.amount);
                    case 'amount-low':
                        return parseFloat(a.dataset.amount) - parseFloat(b.dataset.amount);
                    default:
                        return 0;
                }
            });

            // Reorder the cards in the container
            cardsArray.forEach(card => {
                contractsContainer.appendChild(card);
            });
        });
    });

    // Dropdown toggle functionality
    const filterButtons = document.querySelectorAll('.filter-btn');
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            const dropdown = this.nextElementSibling;
            dropdown.classList.toggle('show');
        });
    });

    // Close dropdowns when clicking outside
    document.addEventListener('click', function(event) {
        if (!event.target.matches('.filter-btn')) {
            document.querySelectorAll('.dropdown-content').forEach(dropdown => {
                if (dropdown.classList.contains('show')) {
                    dropdown.classList.remove('show');
                }
            });
        }
    });
});