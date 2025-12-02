function setupMoreLessToggle() {
    const toggles = document.querySelectorAll('.more-toggle');
    
    toggles.forEach(toggle => {
        toggle.addEventListener('click', (e) => {
            e.preventDefault();
            const filterType = toggle.dataset.toggle; // 'cuisines' or 'tags'
            const containerClass = `hidden-${filterType}`;
            const container = toggle.closest(`.${filterType}-filter`).querySelector(`.${containerClass}`);
            
            if (container) {
                const isExpanded = container.classList.contains('expanded');
                if (isExpanded) {
                    container.classList.remove('expanded');
                    toggle.textContent = '+ MORE';
                } else {
                    container.classList.add('expanded');
                    toggle.textContent = '- LESS';
                }
            }
        });
    });
}

document.addEventListener('DOMContentLoaded', () => {
    // Handle +MORE and -LESS toggle
    setupMoreLessToggle();
    let address = document.getElementById('address').textContent;

    const restaurants = JSON.parse(document.getElementById('restaurant-data').textContent);
    const paginator = new Paginator(restaurants, 5);
    renderPage(paginator);
    const cuisineFContainer = document.querySelector('.cuisines-filter');
    const tagsFContainer = document.querySelector('.tags-filter');
    
    // Get all checked inputs inside it (including hidden ones)
    const cuisines = Array.from(
        cuisineFContainer.querySelectorAll('input[name="cuisines"]')
    );

    const tags = Array.from(
        tagsFContainer.querySelectorAll('input[name="tags"]')
    );

    // Get dropdown elements
    const guestCountSelect = document.getElementById('guest_count_select');
    const operatingDaySelect = document.getElementById('operating_day_select');

    let checkedCuisines = [];
    let checkedTags = [];
    let selectedGuestCount = '';
    let selectedOperatingDay = '';
    let sortBy = 'newest';
    let sortOrder = "asc";
    let searchTerm = '';
    const searchInput = document.querySelector('input[type="search"]');


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

    const contextGuestCount = guestCountSelect.dataset.value;
    const contextOperatingDay = operatingDaySelect.dataset.value;
    let shouldApplyFilters = false;
    
    if (contextGuestCount) {
        guestCountSelect.value = contextGuestCount;
        selectedGuestCount = contextGuestCount;
        shouldApplyFilters = true;
        console.log("gcount: ", contextGuestCount);
    }
    
    if (contextOperatingDay && contextOperatingDay != 'None') {
        operatingDaySelect.value = contextOperatingDay;
        selectedOperatingDay = contextOperatingDay;
        shouldApplyFilters = true;
    }
    const searchValue = searchInput.value;
    console.log('searchvalue:', searchValue);
    if (searchValue == ''){
        const savedSearchTerm = localStorage.getItem("searchTerm");
        if (savedSearchTerm) {
            searchInput.value = savedSearchTerm;
            localStorage.removeItem("searchTerm");
        }
    }

    searchTerm = searchInput.value;

    if(searchTerm){
        shouldApplyFilters = true;
    }

    if (address && address !== 'Select Location') {
        shouldApplyFilters = true;
    }

    // Apply filters if any context values were set
    if (shouldApplyFilters) {
        applyFiltersAndSort();
    }

    // Guest count dropdown
    guestCountSelect.addEventListener('change', (e) => {
        selectedGuestCount = e.target.value;
        applyFiltersAndSort();
    });

    // Operating day dropdown
    operatingDaySelect.addEventListener('change', (e) => {
        selectedOperatingDay = e.target.value;
        applyFiltersAndSort();
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

    const searchbar = document.querySelector('.navbar-searchbar');
    const searchBtn = searchbar.querySelector('button');
    searchBtn.addEventListener('click',()=>{
        searchTerm = searchInput.value.trim();
        applyFiltersAndSort();
    });
    
    
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            searchTerm = searchInput.value.trim();
            applyFiltersAndSort();
        }
    });

    const addressForm = document.getElementById('addressForm');
    if (addressForm) {
        addressForm.addEventListener('submit', () => {
            setTimeout(() => {
                address = document.getElementById('address').textContent;
                applyFiltersAndSort();
                if (window.LoadingOverlay) {
                    window.LoadingOverlay.hide();
                }
            }, 100);
        });
    }
    
    function applyFiltersAndSort() {
        const resultNumbers = document.querySelector('.results-count');
        let filtered = filterRestaurants(restaurants, checkedCuisines, checkedTags, selectedGuestCount, selectedOperatingDay, address, searchTerm);
        if (sortBy) {
            filtered = sortRestaurants(filtered, sortBy, sortOrder);
        }
        paginator.setItems(filtered);
        renderPage(paginator);
        resultNumbers.textContent = `${filtered.length} restaurants found`;
    }

    setupPaginationControls(paginator);
})



function filterRestaurants(restaurants, cuisines, tags, guestCount, operatingDay, address, searchTerm) {
    // cuisines and tags are arrays of selected IDs/values
    console.log('cusines checked: ', cuisines);
    return restaurants.filter(restaurant => {
        // Check if restaurant has at least one of the selected cuisines
        console.log('cusines: ', restaurant.cuisines);
        const matchesCuisine = cuisines.length === 0 || restaurant.cuisines.some(c => cuisines.includes(c.id));
        console.log('matches:', matchesCuisine);
        // Check if restaurant has at least one of the selected tags
        const matchesTags = tags.length === 0 || restaurant.tags.some(t => tags.includes(t.id));

        // Check if restaurant can accommodate the selected guest count
        let matchesGuestCount = true;
        if (guestCount) {
            if (guestCount === '1') matchesGuestCount = restaurant.max_guest_count >= 1;
            else if (guestCount === '2') matchesGuestCount = restaurant.max_guest_count >= 2;
            else if (guestCount === '3-4') matchesGuestCount = restaurant.max_guest_count >= 3;
            else if (guestCount === '5-6') matchesGuestCount = restaurant.max_guest_count >= 5;
            else if (guestCount === '7-10') matchesGuestCount = restaurant.max_guest_count >= 7;
            else if (guestCount === '11-20') matchesGuestCount = restaurant.max_guest_count >= 11;
            else if (guestCount === '20+') matchesGuestCount = restaurant.max_guest_count >= 20;
            else if (guestCount === 'Any') matchesGuestCount = true;
        }

        // Check if restaurant operates on the selected day
        let matchesOperatingDay = true;
        if (operatingDay && operatingDay !== 'Any Day') {
            const operatingDays = restaurant.operating_days.split(',').map(d => d.trim());
            matchesOperatingDay = operatingDays.includes(operatingDay);
        }

        let matchesAddress = true;
        if(address && address !== 'Select Location') {
            const restaurantAddress = restaurant.address.toLowerCase();
            matchesAddress = restaurantAddress.includes(address.toLowerCase());
        }

        let matchesName = true;
        if(searchTerm) {
            const restaurantName = restaurant.name.toLowerCase();
            matchesName = restaurantName.includes(searchTerm.toLowerCase());
        }

        // Keep restaurant only if it matches all filters
        return matchesCuisine && matchesTags && matchesGuestCount && matchesOperatingDay && matchesAddress && matchesName;
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


function renderPage(paginator) {
    const grid = document.querySelector('.restaurants-grid');
    const restaurants = paginator.getCurrentPageItems();
    grid.innerHTML = '';
    restaurants.forEach(restaurant => {
        const card = createRestaurantCard(restaurant);
        card.addEventListener('click', () => {
            bookRestaurant(restaurant.id);
        });
        grid.append(card);
    });
    initStars();
    updatePaginationControls(paginator);
}

function setupPaginationControls(paginator) {
    const paginationContainer = document.querySelector('.pagination');
    paginationContainer.addEventListener('click', (e) => {
        if (e.target.classList.contains('pagination-prev')) {
            e.preventDefault();
            paginator.previousPage();
            renderPage(paginator);
            window.scrollTo(0, 0);
        } else if (e.target.classList.contains('pagination-next')) {
            e.preventDefault();
            paginator.nextPage();
            renderPage(paginator);
            window.scrollTo(0, 0);
        } else if (e.target.classList.contains('pagination-number')) {
            e.preventDefault();
            const pageNum = parseInt(e.target.dataset.page);
            paginator.currentPage = pageNum;
            renderPage(paginator);
            window.scrollTo(0, 0);
        }
    });
}

function updatePaginationControls(paginator) {
    const paginationContainer = document.querySelector('.pagination');
    if (!paginationContainer) return;
    
    if (paginator.totalPages <= 1) {
        paginationContainer.innerHTML = '';
        return;
    }

    paginationContainer.innerHTML = '';

    if (paginator.hasPreviousPage()) {
        const prev = document.createElement('a');
        prev.href = '#';
        prev.className = 'pagination-prev';
        prev.textContent = '« Previous';
        paginationContainer.append(prev);
    } else {
        const prev = document.createElement('span');
        prev.className = 'disabled';
        prev.textContent = '« Previous';
        paginationContainer.append(prev);
    }

    for (let i = 1; i <= paginator.totalPages; i++) {
        if (i === paginator.currentPage) {
            const span = document.createElement('span');
            span.className = 'current';
            span.textContent = i;
            paginationContainer.append(span);
        } else if (i > paginator.currentPage - 3 && i < paginator.currentPage + 3) {
            const link = document.createElement('a');
            link.href = '#';
            link.className = 'pagination-number';
            link.dataset.page = i;
            link.textContent = i;
            paginationContainer.append(link);
        }
    }

    if (paginator.hasNextPage()) {
        const next = document.createElement('a');
        next.href = '#';
        next.className = 'pagination-next';
        next.textContent = 'Next »';
        paginationContainer.append(next);
    } else {
        const next = document.createElement('span');
        next.className = 'disabled';
        next.textContent = 'Next »';
        paginationContainer.append(next);
    }
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
          <div class="card-header">
            <div class="header-title">
              <h3 class="restaurant-name">${restaurant.name}</h3>
              <div class="restaurant-rating">
                <div class="stars" data-rating="${restaurant.avg_rating || 0}"></div>
                <span class="rating-text">${avgRating.toFixed(1)}</span>
                <span class="review-count">(${reviewCount})</span>
              </div>
            </div>
            <div class="header-meta">
              <div class="restaurant-price">
                <span>${restaurant.price_range_display || "N/A"}</span>
              </div>
            </div>
          </div>

          <p class="restaurant-cuisines">${restaurant.cuisines.map(c => c.name).join(', ')}</p>

          <div class="restaurant-details">
            <div class="details-row">
              <div class="restaurant-address">
                <i class="fas fa-map-marker-alt"></i>
                <span>${restaurant.address || "Address not available"}</span>
              </div>

              <div class="restaurant-guests">
                <i class="fas fa-users"></i>
                <span>Up to ${restaurant.max_guest_count} guests</span>
              </div>
            </div>

            <div class="details-row">
              <div class="restaurant-hours ${isOpen ? "open" : "closed"}">
                <i class="fas fa-clock"></i>
                <span>
                  ${isOpen
              ? `Open until ${restaurant.closing_time}`
              : restaurant.opening_time
                  ? `Opens at ${restaurant.opening_time}`
                  : "Hours not available"}
                </span>
              </div>

              <div class="restaurant-operating-days">
                <i class="fas fa-calendar-alt"></i>
                <span class="operating-days-text">${restaurant.operating_days || "Hours not available"}</span>
              </div>
            </div>
          </div>

          ${restaurant.tags?.length
            ? `<div class="restaurant-tags">${restaurant.tags.map(t => t.tag).map(tag => `<span class="restaurant-tag">${tag}</span>`).join('')}</div>`
            : ""}
        </div>
    `;

    return card;
}
