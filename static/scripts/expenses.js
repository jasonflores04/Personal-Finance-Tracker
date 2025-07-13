// Dropdown Menu in the Form
const all_categories = document.getElementById('categories');
const input_category = document.getElementById('input-category');

// Dynamically inputs chosen category to input category section
all_categories.addEventListener('change', function() {
    const category = all_categories.value;
    input_category.value = category;
});

// Dropdown Menu for Showing Specific Categories
const choose_category = document.getElementById('choose-category');
const choose_categories = document.getElementById('choose-categories');

// Dynamically submits chosen category
choose_category.addEventListener('change', function() {
    choose_categories.submit()
});