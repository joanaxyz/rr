document.addEventListener("DOMContentLoaded", () => {
  const reservations = [
    { guest: "Joshua", table: "A1", seats: 2, time: "6:00 PM", status: "Pending" },
    { guest: "Maria", table: "B2", seats: 4, time: "7:30 PM", status: "Confirmed" },
  ];

  const tbody = document.querySelector("#reservationsTable tbody");
  reservations.forEach(r => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${r.guest}</td>
      <td>${r.table}</td>
      <td>${r.seats}</td>
      <td>${r.time}</td>
      <td>${r.status}</td>
      <td><button class="view-btn">View</button></td>
    `;
    tbody.appendChild(row);
  });

  // Update totals
  document.getElementById("totalReservations").textContent = reservations.length;
  document.getElementById("upcomingCount").textContent = reservations.filter(r => r.status === "Pending").length;
  document.getElementById("totalTables").textContent = 10; // Example
});
