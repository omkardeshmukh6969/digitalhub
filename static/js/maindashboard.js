// Handle search form submission
document.querySelector('.search-form').addEventListener('submit', function (e) {
    e.preventDefault();
    const searchInput = document.querySelector('#searchInput').value.trim();

    if (searchInput === '') {
        alert('Please enter a search term.');
    } else {
        console.log('Searching for:', searchInput);
        // You can implement actual search functionality here
        // For example: window.location.href = `/search?query=${searchInput}`;
    }
});

// Fetch dynamic card data from the backend API
function fetchCardData() {
    fetch('/api/cards')  // The API endpoint to get card data
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();  // Convert the response to JSON
        })
        .then(data => {
            populateCards(data);  // Pass the fetched data to the populateCards function
        })
        .catch(error => {
            console.error('Error fetching card data:', error);
            document.querySelector('.card-grid').innerHTML = '<p>Failed to load card data.</p>';  // Display an error message
        });
}
// Handle search form submission
document.querySelector('.search-form').addEventListener('submit', function (e) {
    e.preventDefault();
    const searchInput = document.querySelector('#searchInput').value.trim();

    if (searchInput === '') {
        alert('Please enter a search term.');
    } else {
        console.log('Searching for:', searchInput);
        // Fetch search results from the backend
        fetchSearchResults(searchInput);
    }
});

// Function to fetch search results from the API
function fetchSearchResults(query) {
    fetch(`/api/search?query=${encodeURIComponent(query)}`)  // Encode the query for URL
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            populateCards(data);  // Populate the cards with search results
        })
        .catch(error => {
            console.error('Error fetching search results:', error);
            document.querySelector('.card-grid').innerHTML = '<p>Failed to load search results.</p>';  // Display an error message
        });
}

// Function to dynamically populate cards
function populateCards(data) {
    const cardContainer = document.querySelector('.card-grid');  // Assuming your cards are inside a container with class `card-grid`

    data.forEach((item, index) => {
        let card;

        // Check if a card already exists at this index
        if (index < cardContainer.children.length) {
            card = cardContainer.children[index];
        } else {
            // Create a new card element if not enough cards exist
            card = document.createElement('a');
            card.className = 'card';
            card.innerHTML = `
                <div class="card__background"></div>
                <div class="card__content">
                    <p class="card__category"></p>
                    <h3 class="card__heading"></h3>
                </div>
            `;
            cardContainer.appendChild(card);  // Add the new card to the card grid
        }

        // Update the card content
        card.querySelector('.card__category').textContent = item.category;
        card.querySelector('.card__heading').textContent = item.description;
        card.href = item.link;
    });
}

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Fetch card data and populate the page when DOM content is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    fetchCardData();  // Call the fetchCardData function to get dynamic content
});
