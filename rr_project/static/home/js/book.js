async function bookRestaurant(restaurantId) {
    console.log('click');
    const restaurantUrl = window.getRestaurantDetailUrl 
        ? window.getRestaurantDetailUrl(restaurantId) 
        : `/restaurants/${restaurantId}/`;
    window.location.href = restaurantUrl;
}

function bookmarkRestaurant(restaurantId) {
    
}