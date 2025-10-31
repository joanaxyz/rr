document.addEventListener("DOMContentLoaded", () => {
    const restaurantData = JSON.parse(document.getElementById('context').textContent);
    const restaurantLength = restaurantData.count;
    setInterval(() => {
        nextSlide(restaurantLength);
    }, 5000);
});


let currentSlide = 0;

function goToSlide(index) {
    const cards = document.querySelectorAll('.restaurant-card');
    const dots = document.querySelectorAll('.pagination-dot');
    
    // Remove active class from current slide
    cards[currentSlide].classList.remove('active');
    dots[currentSlide].classList.remove('active');
    
    // Add active class to new slide
    currentSlide = index;
    cards[currentSlide].classList.add('active');
    dots[currentSlide].classList.add('active');
}

function nextSlide(restaurantLength) {
    const nextIndex = (currentSlide + 1) % restaurantLength;
    goToSlide(nextIndex);
}

function prevSlide(restaurantLength) {
    const prevIndex = currentSlide === 0 ? restaurantLength - 1 : currentSlide - 1;
    goToSlide(prevIndex);
}