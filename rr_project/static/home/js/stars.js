document.addEventListener("DOMContentLoaded", () => {
    initStars();
});



function initStars(){
    const stars = document.querySelectorAll('.stars, .review-stars, .rating-stars');
    stars.forEach(star => {
        const rating = parseFloat(star.dataset.rating) || 0;
        star.innerHTML = generateStars(rating);
    });
}

function generateStars(rating = 0) {
    let starsHTML = '';
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);

    const fullStarSVG = `<svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor">
        <path d="M12 17.27L18.18 21 16.54 13.97 22 9.24 14.81 8.62 12 2 9.19 8.62 2 9.24 7.46 13.97 5.82 21 12 17.27Z"/>
    </svg>`;

    const halfStarSVG = `<svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor">
        <path d="M12 17.27L12 2 9.19 8.62 2 9.24 7.46 13.97 5.82 21 12 17.27Z"/>
    </svg>`;

    const emptyStarSVG = `<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M12 17.27L18.18 21 16.54 13.97 22 9.24 14.81 8.62 12 2 9.19 8.62 2 9.24 7.46 13.97 5.82 21 12 17.27Z"/>
    </svg>`;

    for (let i = 0; i < fullStars; i++) {
        starsHTML += fullStarSVG;
    }

    if (hasHalfStar) {
        starsHTML += halfStarSVG;
    }

    for (let i = 0; i < emptyStars; i++) {
        starsHTML += emptyStarSVG;
    }

    return starsHTML;
}
