document.addEventListener('DOMContentLoaded', () => {
    const restaurants = JSON.parse(document.getElementById('restaurant-data').textContent);
    render(restaurants);
    const cuisineFContainer = document.querySelector('.cuisines-filter');
    const tagsFContainer = document.querySelector('.tags-filter');
    // Get all checked inputs inside it
    const cuisines = Array.from(
        cuisineFContainer.querySelectorAll('input[name="cuisines"]')
    );

    const tags = Array.from(
        tagsFContainer.querySelectorAll('input[name="tags"]')
    );

    let checkedCuisines = [];
    let checkedTags = [];
    let sortBy = 'newest';
    let sortOrder = "asc";


    cuisines.forEach(c => {
        c.addEventListener('change', () => {
            const cuisineId = parseInt(c.value, 10);
            if (c.checked) {
                if (!checkedCuisines.includes(cuisineId)) {
                    checkedCuisines.push(cuisineId);
                    console.log("pushed: ", cuisineId);
                }
            } else {
                checkedCuisines = checkedCuisines.filter(v => v !== cuisineId);
            }
            applyFiltersAndSort();
        });
    });

    tags.forEach(c => {
        c.addEventListener('change', () => {
            const tagId = parseInt(c.value, 10);
            if (c.checked) {
                if (!checkedTags.includes(tagId)) {
                    checkedTags.push(tagId);
                }
            } else {
                checkedTags = checkedTags.filter(v => v !== tagId);
            }
            applyFiltersAndSort();
        });
    });

    // Sort by radio buttons
    const sortByRadios = Array.from(document.querySelectorAll('input[name="sort_by"]'));
    sortByRadios.forEach(radio => {
        radio.addEventListener('change', (event) => {
            if (event.target.checked) {
                sortBy = event.target.value;
                applyFiltersAndSort();
            }
        });
    });

    // Sort order radio buttons
    const orderRadios = Array.from(document.querySelectorAll('input[name="order"]'));
    orderRadios.forEach(radio => {
        radio.addEventListener('change', (event) => {
            if (event.target.checked) {
                sortOrder = event.target.value;
                applyFiltersAndSort();
            }
        });
    });

    function applyFiltersAndSort() {
        let filtered = filterRestaurants(restaurants, checkedCuisines, checkedTags);
        if (sortBy) {
            filtered = sortRestaurants(filtered, sortBy, sortOrder);
        }
        render(filtered);
    }
})



function filterRestaurants(restaurants, cuisines, tags) {
    // cuisines and tags are arrays of selected IDs/values
    console.log('cusines checked: ', cuisines);
    return restaurants.filter(restaurant => {
        // Check if restaurant has at least one of the selected cuisines
        console.log('cusines: ', restaurant.cuisines);
        const matchesCuisine = cuisines.length === 0 || restaurant.cuisines.some(c => cuisines.includes(c.id));
        console.log('matches:', matchesCuisine);
        // Check if restaurant has at least one of the selected tags
        const matchesTags = tags.length === 0 || restaurant.tags.some(t => tags.includes(t.id));

        // Keep restaurant only if it matches both
        return matchesCuisine && matchesTags;
    });
}

function sortRestaurants(restaurants, sortBy, sortOrder) {
    const sorted = [...restaurants];
    const isAsc = sortOrder === 'asc';

    sorted.sort((a, b) => {
        let compareValue = 0;

        switch (sortBy) {
            case 'newest':
                // Sort by ID (assuming higher ID = newer)
                compareValue = a.id - b.id;
                break;
            case 'rating':
                // Sort by average rating
                compareValue = (Number(a.avg_rating) || 0) - (Number(b.avg_rating) || 0);
                break;
            case 'bookmarks':
                // Sort by bookmark count
                compareValue = (a.bookmark_count || 0) - (b.bookmark_count || 0);
                break;
            default:
                return 0;
        }

        return isAsc ? compareValue : -compareValue;
    });

    return sorted;
}


function render(restaurants) {
    const grid = document.querySelector('.restaurants-grid');
    grid.innerHTML = '';
    restaurants.forEach(restaurant => {
        const card = createRestaurantCard(restaurant);
        card.addEventListener('click', () => {
            bookRestaurant(restaurant.id);
        });
        grid.append(card);
    });
}

function createRestaurantCard(restaurant) {
    const card = document.createElement('div');
    card.className = "card";
    card.dataset.id = restaurant.id;

    const imageStyle = restaurant.image
        ? `url('${restaurant.image}')`
        : `linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.3))`;

    const isOpen = restaurant.is_open_now;
    const avgRating = Number(restaurant.avg_rating) || 0;
    const reviewCount = restaurant.review_count || 0;

    card.innerHTML = `
        <div class="left" style="background-image: ${imageStyle}"></div>

        <div class="center">
          <h3 class="restaurant-name">${restaurant.name}</h3>
          <p class="restaurant-cuisines">${restaurant.cuisines.map(c => c.name).join(', ')}</p>

          <div class="restaurant-details">
            <div class="restaurant-address">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M12,11.5A2.5,2.5 0 0,1 9.5,9A2.5,2.5 0 0,1 12,6.5A2.5,2.5 0 0,1 14.5,9A2.5,2.5 0 0,1 12,11.5
                         M12,2A7,7 0 0,0 5,9C5,14.25 12,22 12,22C12,22 19,14.25 19,9A7,7 0 0,0 12,2Z" />
              </svg>
              <span>${restaurant.address || "Address not available"}</span>
            </div>

            <div class="restaurant-hours ${isOpen ? "open" : "closed"}">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2
                         M16.2,16.2L11,13V7H12.5V12.2L17,14.7L16.2,16.2Z" />
              </svg>
              <span>
                ${isOpen
            ? `Open until ${restaurant.closing_time}`
            : restaurant.opening_time
                ? `Opens at ${restaurant.opening_time}`
                : "Hours not available"}
              </span>
            </div>

            <div class="restaurant-price-wrapper">
              <div class="restaurant-price">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2
                           M12,4A8,8 0 0,1 20,12A8,8 0 0,1 12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4Z"/>
                </svg>
                <span>${restaurant.price_range_display || "N/A"}</span>
              </div>
            </div>
          </div>

          ${restaurant.tags?.length
            ? `<div class="restaurant-tags">${restaurant.tags.map(t => t.tag).map(tag => `<span class="restaurant-tag">${tag}</span>`).join('')}</div>`
            : ""}

          <div class="restaurant-rating">
            <div class="stars" data-rating="${restaurant.avg_rating || 0}"></div>
            <span class="rating-text">
                ${avgRating.toFixed(1)} (${reviewCount})
            </span>
          </div>
        </div>
    `;

    return card;
}
