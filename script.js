        const toggleBtn = document.querySelector('.toggle-btn');
        const sidebar = document.querySelector('.sidebar');

        toggleBtn.addEventListener('click', () => {
            sidebar.classList.toggle('active');
        });

document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById('searchInput');
    const searchResults = document.getElementById('searchResults');

    let searchIndex = [];

    // Fetch the search index JSON file
    fetch('search_index.json')
        .then(response => response.json())
        .then(data => {
            searchIndex = data;
        })
        .catch(error => {
            console.error('Error loading search index:', error);
        });

    // Function to perform the search
    searchInput.addEventListener('input', function () {
        const query = searchInput.value.toLowerCase();
        searchResults.innerHTML = '';

        if (query.length > 1) {  // Start searching after two characters
            const results = searchIndex.filter(entry => entry.title.toLowerCase().includes(query));
            results.forEach(result => {
                const resultItem = document.createElement('div');
                resultItem.innerHTML = `<a href="${result.url}">${result.title}</a>`;
                searchResults.appendChild(resultItem);
            });
        }
    });
});

// Search bar
function toggleSearch() {
    const searchBar = document.getElementById('searchBar');
    if (searchBar.style.display === 'inline-block' || searchBar.style.display === '') {
        searchBar.style.display = 'none';
    } else {
        searchBar.style.display = 'inline-block';
        searchBar.focus();
    }
}

// Filter Cards
function filterCards() {
    const query = document.getElementById('searchBar').value.toLowerCase();
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        const text = card.textContent.toLowerCase();
        card.style.display = text.includes(query) ? '' : 'none';
    });
}

// Filter cards by tag
function filterByTag(tag) {
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        const tags = card.querySelector('p:last-child').textContent;
        card.style.display = tags.includes(tag) ? '' : 'none';
    });
}
