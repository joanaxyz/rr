document.addEventListener('DOMContentLoaded',()=>{
    const searchbar = document.querySelector('.navbar-searchbar');
    const searchBtn = searchbar.querySelector('button');
    const searchInput = searchbar.querySelector('input');
    const isRestaurants = window.location.href.includes("restaurants");
    
    if(!isRestaurants){
        searchBtn.addEventListener('click',()=>{
            window.location.href = "/restaurants/restaurants";
            localStorage.setItem("searchTerm", searchInput.value);
        })
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                window.location.href = "/restaurants/restaurants"; 
                localStorage.setItem("searchTerm", searchInput.value);
            }
        });
    }
})