document.addEventListener("DOMContentLoaded", () => {
    initStars();
});



function initStars(){
    const stars = document.querySelectorAll('.stars, .review-stars, .rating-stars, .modal-review-stars');
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

    const starPath = "M12 17.27L18.18 21 16.54 13.97 22 9.24 14.81 8.62 12 2 9.19 8.62 2 9.24 7.46 13.97 5.82 21 12 17.27Z";
    
    const fullStarSVG = `<svg viewBox="0 0 24 24" width="24" height="24" xmlns="http://www.w3.org/2000/svg" fill="currentColor">
        <path d="${starPath}"/>
    </svg>`;

    // Half star: Using two overlapping paths - one clipped for left half, one for outline
    const clipId = `half-clip-${Math.random().toString(36).substr(2, 9)}`;
    const halfStarSVG = `<svg viewBox="0 0 24 24" width="24" height="24" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <clipPath id="${clipId}">
                <rect x="0" y="0" width="12" height="24"/>
            </clipPath>
        </defs>
        <g fill="currentColor">
            <path d="${starPath}" clip-path="url(#${clipId})"/>
            <path d="${starPath}" opacity="0.3"/>
        </g>
    </svg>`;

    const emptyStarSVG = `<svg viewBox="0 0 24 24" width="24" height="24" xmlns="http://www.w3.org/2000/svg" fill="currentColor" opacity="0.3">
        <path d="${starPath}"/>
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
