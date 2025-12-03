// ========================== Reservation Management ==========================

// ------------------------- Reservation Actions -------------------------
function confirmReservation(form, name, table_numbers) {
    if (!form) {
        console.error('Form not found');
        return;
    }
    window.Modal.confirm(
        `Are you sure you want to confirm reservation by ${name} at table/s ${table_numbers}?`,
        () => { 
            const actionInput = form.querySelector('input[name="action"]');
            if (actionInput) {
                actionInput.value = "confirm";
                form.submit();
            } else {
                console.error('Action input not found');
            }
        }
    );
}

function completeReservation(form, name, table_numbers) {
    if (!form) {
        console.error('Form not found');
        return;
    }
    window.Modal.confirm(
        `Are you sure you want to complete reservation by ${name} at table/s ${table_numbers}?`,
        () => { 
            const actionInput = form.querySelector('input[name="action"]');
            if (actionInput) {
                actionInput.value = "complete";
                form.submit();
            } else {
                console.error('Action input not found');
            }
        }
    );
}

function deleteReservation(form, name, table_numbers) {
    if (!form) {
        console.error('Form not found');
        return;
    }
    window.Modal.confirm(
        `Are you sure you want to delete reservation by ${name} at table/s ${table_numbers}?`,
        () => { 
            const actionInput = form.querySelector('input[name="action"]');
            if (actionInput) {
                actionInput.value = "delete";
                form.submit();
            } else {
                console.error('Action input not found');
            }
        }
    );
}

function cancelReservation(form, name, table_numbers) {
    if (!form) {
        console.error('Form not found');
        return;
    }
    window.Modal.confirm(
        `Are you sure you want to cancel reservation by ${name} at table/s ${table_numbers}?`,
        () => { 
            promptReason(reason => { 
                const reasonInput = form.querySelector('input[name="cancellation_reason"]');
                const actionInput = form.querySelector('input[name="action"]');
                if (reasonInput && actionInput) {
                    reasonInput.value = reason; 
                    actionInput.value = "cancel"; 
                    form.submit();
                } else {
                    console.error('Form inputs not found');
                }
            }); 
        }
    );
}

function confirmCancelReservation(form, name, table_numbers) {
    if (!form) {
        console.error('Form not found');
        return;
    }
    window.Modal.confirm(
        `Are you sure you want to confirm cancel reservation by ${name} at table/s ${table_numbers}?`,
        () => { 
            const actionInput = form.querySelector('input[name="action"]');
            if (actionInput) {
                actionInput.value = "confirm_cancel";
                form.submit();
            } else {
                console.error('Action input not found');
            }
        }
    );
}

function promptReason(callback) {
    window.Modal.prompt("Please provide a reason for cancellation:", {
        title: "Cancel Reservation",
        placeholder: "Type your reason here...",
        validator: value => value && value.trim().length > 0 ? true : "Please enter a reason before submitting."
    }).then(callback).catch(err => console.log(err));
}

// ------------------------- Filters + Pagination -------------------------
const rowsPerPage = 5; // items per page
let currentPage = 1;

document.addEventListener("DOMContentLoaded", () => {
    const table = document.querySelector(".reservation-table tbody");
    const filters = {
        status: document.getElementById("statusFilter"),
        dateFrom: document.getElementById("dateFromFilter"),
        dateTo: document.getElementById("dateToFilter"),
        guestCount: document.getElementById("guestCountFilter"),
        name: document.getElementById("nameSearchFilter"),
        email: document.getElementById("emailSearchFilter")
    };
    const resetBtn = document.getElementById("resetFilters");

    function filterAndPaginate(goToLastPage = false) {
        const rows = Array.from(table.rows);

        // Filter rows
        const filteredRows = rows.filter(row => {
            const ds = row.dataset;
            if (filters.status.value && ds.status.toLowerCase() !== filters.status.value.toLowerCase()) return false;
            if (filters.dateFrom.value && ds.date < filters.dateFrom.value) return false;
            if (filters.dateTo.value && ds.date > filters.dateTo.value) return false;
            if (filters.guestCount.value && parseInt(ds.guestCount) < parseInt(filters.guestCount.value)) return false;
            if (filters.name.value && !ds.name.toLowerCase().includes(filters.name.value.toLowerCase())) return false;
            if (filters.email.value && !ds.email.toLowerCase().includes(filters.email.value.toLowerCase())) return false;
            return true;
        });

        // Hide all rows first
        rows.forEach(row => row.style.display = "none");

        // Pagination
        const totalPages = Math.ceil(filteredRows.length / rowsPerPage);
        if (goToLastPage) {
            currentPage = totalPages || 1; // show last page
        } else if (currentPage > totalPages) {
            currentPage = totalPages || 1;
        }

        const startIndex = (currentPage - 1) * rowsPerPage;
        const endIndex = startIndex + rowsPerPage;
        filteredRows.slice(startIndex, endIndex).forEach(row => row.style.display = "");

        renderPageButtons(totalPages);
    }

    function renderPageButtons(totalPages) {
        const container = document.getElementById("pagination-container");
        container.innerHTML = "";

        if (totalPages === 0) return;

        const maxButtons = 5;
        let startPage = Math.max(1, currentPage - 2);
        let endPage = Math.min(totalPages, startPage + maxButtons - 1);
        if (endPage - startPage < maxButtons - 1) startPage = Math.max(1, endPage - maxButtons + 1);

        // Prev button
        const prevBtn = document.createElement("button");
        prevBtn.textContent = "«";
        prevBtn.disabled = currentPage === 1;
        prevBtn.onclick = () => { currentPage--; filterAndPaginate(); };
        container.appendChild(prevBtn);

        // Page numbers
        for (let i = startPage; i <= endPage; i++) {
            const btn = document.createElement("button");
            btn.textContent = i;
            if (i === currentPage) btn.classList.add("active");
            btn.onclick = () => { currentPage = i; filterAndPaginate(); };
            container.appendChild(btn);
        }

        // Next button
        const nextBtn = document.createElement("button");
        nextBtn.textContent = "»";
        nextBtn.disabled = currentPage === totalPages;
        nextBtn.onclick = () => { currentPage++; filterAndPaginate(); };
        container.appendChild(nextBtn);
    }

    // Attach filter events
    Object.values(filters).forEach(f => f.addEventListener("input", () => { currentPage = 1; filterAndPaginate(); }));
    Object.values(filters).forEach(f => f.addEventListener("change", () => { currentPage = 1; filterAndPaginate(); }));

    // Reset button
    resetBtn.addEventListener("click", () => {
        Object.values(filters).forEach(f => f.value = "");
        currentPage = 1;
        filterAndPaginate();
    });

    // Initial load
    filterAndPaginate();
});

// ------------------------- Reservation Modal -------------------------
// Reservation modal is now handled by info_modal.js using Modal.show()

// ------------------------- Floor Plan -------------------------
document.addEventListener('DOMContentLoaded', () => {
    const floorPlan = document.querySelector('.floor-plan');
    if (floorPlan) {
        const data = JSON.parse(floorPlan.dataset.floorplan);
        const width = data.width || 900;
        const height = data.height || 600;

        floorPlan.style.width = width + 'px';
        floorPlan.style.height = height + 'px';
        floorPlan.style.minWidth = width + 'px';
        floorPlan.style.minHeight = height + 'px';

        const container = floorPlan.parentElement;
        if (container) container.style.minHeight = Math.min(height, 500) + 'px';

        FloorPlanUtils.initializeFloorPlan(floorPlan);
    }
});
