document.addEventListener('DOMContentLoaded',()=>{
    const searchbar = document.querySelector('.navbar-searchbar');
    if (!searchbar) return;
    
    const searchBtn = searchbar.querySelector('button');
    const searchInput = searchbar.querySelector('input');
    
    if (!searchBtn || !searchInput) return;
    
    const isRestaurants = window.location.href.includes("restaurants");
    
    if(!isRestaurants){
        searchBtn.addEventListener('click',()=>{
            const searchValue = searchInput.value.trim();
            localStorage.setItem("searchTerm", searchValue);
            window.location.href = "/restaurants/restaurants";
        })
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const searchValue = searchInput.value.trim();
                localStorage.setItem("searchTerm", searchValue);
                window.location.href = "/restaurants/restaurants"; 
            }
        });
    }
})