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
    const searchbar = document.querySelector('.navbar-searchbar');
    const searchInput = searchbar ? searchbar.querySelector('input') : null;


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
    const searchValue = searchInput ? searchInput.value : '';
    console.log('searchvalue:', searchValue);
    if (searchInput && searchValue == ''){
        const savedSearchTerm = localStorage.getItem("searchTerm");
        if (savedSearchTerm) {
            searchInput.value = savedSearchTerm;
            localStorage.removeItem("searchTerm");
        }
    }

    searchTerm = searchInput ? searchInput.value : '';

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

    if (searchbar && searchInput) {
        const searchBtn = searchbar.querySelector('button');
        if (searchBtn) {
            searchBtn.addEventListener('click',()=>{
                searchTerm = searchInput.value.trim();
                applyFiltersAndSort();
            });
        }
        
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                searchTerm = searchInput.value.trim();
                applyFiltersAndSort();
            }
        });
    }

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
        if (resultNumbers) {
            resultNumbers.innerHTML = `<strong>${filtered.length}</strong> restaurants found`;
        }
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

// Set up pagination event delegation once
let paginationListenerSetup = false;

function setupPaginationControls(paginator) {
    const paginationContainer = document.querySelector('.pagination');
    if (!paginationContainer) return;
    
    // Set up event delegation once
    if (!paginationListenerSetup) {
        paginationListenerSetup = true;
        paginationContainer.addEventListener('click', (e) => {
            e.preventDefault();
            const target = e.target.closest('a, span');
            if (!target) return;
            
            if (target.classList.contains('pagination-prev') && !target.classList.contains('disabled')) {
                paginator.previousPage();
                renderPage(paginator);
                window.scrollTo({ top: 0, behavior: 'smooth' });
            } else if (target.classList.contains('pagination-next') && !target.classList.contains('disabled')) {
                paginator.nextPage();
                renderPage(paginator);
                window.scrollTo({ top: 0, behavior: 'smooth' });
            } else if (target.classList.contains('pagination-number') && target.dataset.page) {
                const pageNum = parseInt(target.dataset.page);
                paginator.currentPage = pageNum;
                renderPage(paginator);
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        });
    }
}

function updatePaginationControls(paginator) {
    const paginationContainer = document.querySelector('.pagination');
    if (!paginationContainer) return;
    
    if (paginator.totalPages <= 1) {
        paginationContainer.innerHTML = '';
        return;
    }

    paginationContainer.innerHTML = '';

    // Previous button
    if (paginator.hasPreviousPage()) {
        const prev = document.createElement('a');
        prev.href = '#';
        prev.className = 'pagination-prev';
        prev.innerHTML = '<i class="fas fa-chevron-left"></i>';
        paginationContainer.append(prev);
    } else {
        const prev = document.createElement('span');
        prev.className = 'pagination-prev disabled';
        prev.innerHTML = '<i class="fas fa-chevron-left"></i>';
        paginationContainer.append(prev);
    }

    // Show all page numbers (or limit to 10 if too many)
    const maxPages = 10;
    let startPage = 1;
    let endPage = paginator.totalPages;
    
    if (paginator.totalPages > maxPages) {
        // Show pages around current page
        const half = Math.floor(maxPages / 2);
        startPage = Math.max(1, paginator.currentPage - half);
        endPage = Math.min(paginator.totalPages, startPage + maxPages - 1);
        
        // Adjust if we're near the end
        if (endPage - startPage < maxPages - 1) {
            startPage = Math.max(1, endPage - maxPages + 1);
        }
        
        // Show first page if not in range
        if (startPage > 1) {
            const first = document.createElement('a');
            first.href = '#';
            first.className = 'pagination-number';
            first.dataset.page = 1;
            first.textContent = '1';
            paginationContainer.append(first);
            
            if (startPage > 2) {
                const ellipsis = document.createElement('span');
                ellipsis.className = 'pagination-ellipsis';
                ellipsis.textContent = '...';
                paginationContainer.append(ellipsis);
            }
        }
    }

    for (let i = startPage; i <= endPage; i++) {
        if (i === paginator.currentPage) {
            const span = document.createElement('span');
            span.className = 'pagination-number current';
            span.textContent = i;
            paginationContainer.append(span);
        } else {
            const link = document.createElement('a');
            link.href = '#';
            link.className = 'pagination-number';
            link.dataset.page = i;
            link.textContent = i;
            paginationContainer.append(link);
        }
    }

    // Show last page if not in range
    if (paginator.totalPages > maxPages && endPage < paginator.totalPages) {
        if (endPage < paginator.totalPages - 1) {
            const ellipsis = document.createElement('span');
            ellipsis.className = 'pagination-ellipsis';
            ellipsis.textContent = '...';
            paginationContainer.append(ellipsis);
        }
        
        const last = document.createElement('a');
        last.href = '#';
        last.className = 'pagination-number';
        last.dataset.page = paginator.totalPages;
        last.textContent = paginator.totalPages;
        paginationContainer.append(last);
    }

    // Next button
    if (paginator.hasNextPage()) {
        const next = document.createElement('a');
        next.href = '#';
        next.className = 'pagination-next';
        next.innerHTML = '<i class="fas fa-chevron-right"></i>';
        paginationContainer.append(next);
    } else {
        const next = document.createElement('span');
        next.className = 'pagination-next disabled';
        next.innerHTML = '<i class="fas fa-chevron-right"></i>';
        paginationContainer.append(next);
    }
}

function createRestaurantCard(restaurant) {
    const card = document.createElement('div');
    card.className = "restaurant-card";
    card.dataset.id = restaurant.id;

    const imageUrl = restaurant.image || 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=800';
    const isOpen = restaurant.is_open_now;
    const avgRating = Number(restaurant.avg_rating) || 0;
    const reviewCount = restaurant.review_count || 0;
    const priceRange = restaurant.price_range_display || "$$";
    const cuisines = restaurant.cuisines?.slice(0, 3) || [];
    const tags = restaurant.tags || [];
    const address = restaurant.address || restaurant.city || "Address not available";
    const maxGuests = restaurant.max_guest_count || 0;
    const operatingDays = restaurant.operating_days || "N/A";
    const hoursText = isOpen 
        ? `Open until ${restaurant.closing_time || "N/A"}`
        : restaurant.opening_time 
            ? `Opens at ${restaurant.opening_time}`
            : "Hours not available";

    card.innerHTML = `
        <div class="card-image" style="background-image: url('${imageUrl}')">
            <div class="card-overlay">
                <div class="card-rating">
                    <i class="fas fa-star"></i>
                    <span>${avgRating > 0 ? avgRating.toFixed(1) : "New"}</span>
                </div>
            </div>
        </div>
        
        <div class="card-content">
            <div class="card-header">
                <h3>${restaurant.name}</h3>
                <span class="card-price">${priceRange}</span>
            </div>
            
            <div class="card-cuisines">
                ${cuisines.map(c => `<span class="cuisine-tag">${c.name}</span>`).join('')}
            </div>
            
            <div class="card-info">
                <span class="info-item">
                    <i class="fas fa-location-dot"></i>
                    ${address.length > 30 ? address.substring(0, 30) + '...' : address}
                </span>
                <span class="info-item ${isOpen ? 'open' : 'closed'}">
                    <i class="fas fa-clock"></i>
                    ${isOpen ? 'Open Now' : 'Closed'}
                </span>
            </div>
            
            <div class="card-details">
                <div class="detail-item">
                    <i class="fas fa-users"></i>
                    <span>Up to ${maxGuests} guests</span>
                </div>
                <div class="detail-item">
                    <i class="fas fa-calendar-alt"></i>
                    <span>${operatingDays}</span>
                </div>
            </div>
            
            ${tags.length > 0 ? `
                <div class="card-tags">
                    ${tags.slice(0, 4).map(t => `<span class="tag-badge">${t.tag}</span>`).join('')}
                </div>
            ` : ''}
            
            <div class="card-actions">
                <button class="btn-book" onclick="event.stopPropagation(); bookRestaurant('${restaurant.id}')">
                    Book Now
                    <i class="fas fa-arrow-right"></i>
                </button>
            </div>
        </div>
    `;

    return card;
}
