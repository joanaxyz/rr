document.addEventListener("DOMContentLoaded", function() {
    initStars();
});

function initStars() {
    var stars = document.querySelectorAll('.stars, .review-stars, .rating-stars');
    stars.forEach(function(star) {
        var rating = parseFloat(star.dataset.rating) || 0;
        star.innerHTML = generateStars(rating);
    });
}

function generateStars(rating) {
    if (rating === void 0) { rating = 0; }
    var starsHTML = '';
    var fullStars = Math.floor(rating);
    var hasHalfStar = rating % 1 >= 0.5;
    var emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);

    // Removed fill colors so CSS can control
    var fullStarSVG = '<svg viewBox="0 0 24 24"><path d="M12 17.27L18.18 21 16.54 13.97 22 9.24 14.81 8.62 12 2 9.19 8.62 2 9.24 7.46 13.97 5.82 21 12 17.27Z"/></svg>';

    var halfStarSVG = '<svg viewBox="0 0 24 24">'
                    + '<g>'
                    + '<path d="M12 17.27L18.18 21 16.54 13.97 22 9.24 14.81 8.62 12 2 9.19 8.62 2 9.24 7.46 13.97 5.82 21 12 17.27Z"/>'
                    + '<path d="M12 17.27L18.18 21 16.54 13.97 22 9.24 14.81 8.62 12 2 9.19 8.62 2 9.24 7.46 13.97 5.82 21 12 17.27Z" opacity="0.3"/>'
                    + '</g>'
                    + '</svg>';

    var emptyStarSVG = '<svg class="empty" viewBox="0 0 24 24"><path d="M12 17.27L18.18 21 16.54 13.97 22 9.24 14.81 8.62 12 2 9.19 8.62 2 9.24 7.46 13.97 5.82 21 12 17.27Z"/></svg>';

    for (var i = 0; i < fullStars; i++) {
        starsHTML += fullStarSVG;
    }

    if (hasHalfStar) {
        starsHTML += halfStarSVG;
    }

    for (var i = 0; i < emptyStars; i++) {
        starsHTML += emptyStarSVG;
    }

    return starsHTML;
}
