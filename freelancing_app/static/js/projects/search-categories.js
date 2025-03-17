document.addEventListener("DOMContentLoaded", () => {
    const categoriesSearchInput = document.getElementById("categories-search");
    const categoriesList = document.getElementById("categories-list");
    const noCategoriesMessage = document.createElement('div');
    noCategoriesMessage.className = 'no-categories-message';
    noCategoriesMessage.innerText = 'No categories found';

    const filterCategories = () => {
        const searchValue = categoriesSearchInput.value.toLowerCase().trim();
        const categoryItems = categoriesList.querySelectorAll(".category-item");
        let foundMatchingCategories = false;

        categoryItems.forEach((item) => {
            const categoryName = item.dataset.categoryName;

            if (categoryName.includes(searchValue)) {
                item.style.display = "block";
                foundMatchingCategories = true;
            } else {
                item.style.display = "none";
            }
        });

        if (searchValue && !foundMatchingCategories) {
            if (!document.querySelector('.no-categories-message')) {
                categoriesList.appendChild(noCategoriesMessage);
            }
        } else {
            const existingMessage = document.querySelector('.no-categories-message');
            if (existingMessage) {
                existingMessage.remove();
            }
        }
    };

    categoriesSearchInput.addEventListener("input", filterCategories);

    categoriesSearchInput.addEventListener("keypress", (event) => {
        if (event.key === "Enter") {
            event.preventDefault();
        }
    });
});

document.addEventListener("DOMContentLoaded", () => {
    const categoriesList = document.getElementById("categories-list");
    const selectedCategoriesContainer = document.getElementById("selected-categories");

    function addCategory(categoryId, categoryName) {
        if (document.querySelector(`[data-category-id="${categoryId}"]`)) return;

        const categoryChip = document.createElement("div");
        categoryChip.className = "category-chip";
        categoryChip.dataset.categoryId = categoryId;
        categoryChip.innerHTML = `
            ${categoryName}
            <span class="remove-category" data-category-id="${categoryId}">
                <i class="fa-solid fa-minus"></i>
            </span>
        `;

        selectedCategoriesContainer.appendChild(categoryChip);

        categoryChip.querySelector(".remove-category").addEventListener("click", () => {
            removeCategory(categoryId);
        });
    }

    function removeCategory(categoryId) {
        const categoryChip = document.querySelector(`[data-category-id="${categoryId}"]`);
        if (categoryChip) categoryChip.remove();

        const checkbox = categoriesList.querySelector(`input[value="${categoryId}"]`);
        if (checkbox) checkbox.checked = false;
    }

    categoriesList.addEventListener("change", (event) => {
        const checkbox = event.target;
        const categoryId = checkbox.value;
        const categoryName = checkbox.dataset.categoryName;

        if (checkbox.checked) {
            addCategory(categoryId, categoryName);
        } else {
            removeCategory(categoryId);
        }
    });

    const checkedCategories = categoriesList.querySelectorAll("input[name='categories-select']:checked");
    checkedCategories.forEach((checkbox) => {
        const categoryId = checkbox.value;
        const categoryName = checkbox.dataset.categoryName;
        addCategory(categoryId, categoryName);
    });
});