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
