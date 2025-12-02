document.addEventListener('DOMContentLoaded',()=>{
    const searchbar = document.querySelector('.navbar-searchbar');
    if (!searchbar) return;
    
    const searchBtn = searchbar.querySelector('button');
    const searchInput = searchbar.querySelector('input');
    
    if (!searchBtn || !searchInput) return;
    
    const currentPath = window.location.pathname;
    const isRestaurants = currentPath.startsWith('/restaurants/') && currentPath !== '/restaurants/';
    
    if(!isRestaurants){
        // Get the restaurants URL from window variable or use fallback
        let restaurantsUrl = window.restaurantsListUrl;
        
        // Validate and normalize the URL
        if (!restaurantsUrl) {
            restaurantsUrl = "/restaurants/";
        } else {
            // Ensure URL is properly formatted
            restaurantsUrl = restaurantsUrl.trim();
            // Remove any double 'restaurants' in the path
            restaurantsUrl = restaurantsUrl.replace(/\/restaurants\/restaurants/g, '/restaurants');
            // Ensure it ends with / if it's the list page
            if (!restaurantsUrl.endsWith('/') && !restaurantsUrl.match(/\/\d+\//)) {
                restaurantsUrl = restaurantsUrl + '/';
            }
        }
        
        searchBtn.addEventListener('click',()=>{
            const searchValue = searchInput.value.trim();
            localStorage.setItem("searchTerm", searchValue);
            window.location.href = restaurantsUrl;
        })
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const searchValue = searchInput.value.trim();
                localStorage.setItem("searchTerm", searchValue);
                window.location.href = restaurantsUrl; 
            }
        });
    }
})