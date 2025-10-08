document.addEventListener("DOMContentLoaded", () => {
    console.log("✅ Dashboard loaded");

    // Example: Profile dropdown toggle
    const profileBtn = document.querySelector("#profileBtn");
    const profileMenu = document.querySelector("#profileMenu");

    if (profileBtn && profileMenu) {
        profileBtn.addEventListener("click", () => {
            profileMenu.classList.toggle("show");
        });

        // Hide dropdown if clicked outside
        document.addEventListener("click", (event) => {
            if (!profileBtn.contains(event.target) && !profileMenu.contains(event.target)) {
                profileMenu.classList.remove("show");
            }
        });
    }

    // Example: Load reservations dynamically (fake data for now)
    const reservationCard = document.querySelector("#upcomingReservations");
    if (reservationCard) {
        // Later: replace with Django API fetch
        const reservations = [
            { restaurant: "La Bella", date: "2025-09-30", guests: 2 },
            { restaurant: "Ocean View Grill", date: "2025-10-02", guests: 4 }
        ];

        let html = "<ul>";
        reservations.forEach(r => {
            html += `<li>${r.restaurant} - ${r.date} (${r.guests} guests)</li>`;
        });
        html += "</ul>";

        reservationCard.innerHTML += html;
    }
});
