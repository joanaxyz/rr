// ------------------------- Reservation Actions -------------------------
function confirmReservation(form, name, table_numbers) {
  window.MessageBox.showConfirm(
    `Are you sure you want to confirm reservation by ${name} at table/s ${table_numbers}?`,
    () => { form.querySelector('input[name="action"]').value = "confirm"; form.submit(); }
  );
}

function completeReservation(form, name, table_numbers) {
  window.MessageBox.showConfirm(
    `Are you sure you want to complete reservation by ${name} at table/s ${table_numbers}?`,
    () => { form.querySelector('input[name="action"]').value = "complete"; form.submit(); }
  );
}

function deleteReservation(form, name, table_numbers) {
  window.MessageBox.showConfirm(
    `Are you sure you want to delete reservation by ${name} at table/s ${table_numbers}?`,
    () => { form.querySelector('input[name="action"]').value = "delete"; form.submit(); }
  );
}

function cancelReservation(form, name, table_numbers) {
  window.MessageBox.showConfirm(
    `Are you sure you want to cancel reservation by ${name} at table/s ${table_numbers}?`,
    () => { promptReason(reason => { form.querySelector('input[name="cancellation_reason"]').value = reason; form.querySelector('input[name="action"]').value = "cancel"; form.submit(); }); }
  );
}

function confirmCancelReservation(form, name, table_numbers) {
  window.MessageBox.showConfirm(
    `Are you sure you want to confirm cancel reservation by ${name} at table/s ${table_numbers}?`,
    () => { form.querySelector('input[name="action"]').value = "confirm_cancel"; form.submit(); }
  );
}

function promptReason(callback) {
  window.MessageBox.showPrompt("Please provide a reason for cancellation:", {
    title: "Cancel Reservation",
    placeholder: "Type your reason here...",
    validator: value => value && value.trim().length > 0 ? true : "Please enter a reason before submitting."
  }).then(callback).catch(err => console.log(err));
}

// ------------------------- Filters -------------------------
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

  function filterTable() {
    Array.from(table.rows).forEach(row => {
      const ds = row.dataset;
      let show = true;

      if (filters.status.value && ds.status.toLowerCase() !== filters.status.value.toLowerCase()) show = false;
      if (filters.dateFrom.value && ds.date < filters.dateFrom.value) show = false;
      if (filters.dateTo.value && ds.date > filters.dateTo.value) show = false;
      if (filters.guestCount.value && parseInt(ds.guestCount) < parseInt(filters.guestCount.value)) show = false;
      if (filters.name.value && !ds.name.toLowerCase().includes(filters.name.value.toLowerCase())) show = false;
      if (filters.email.value && !ds.email.toLowerCase().includes(filters.email.value.toLowerCase())) show = false;

      row.style.display = show ? "" : "none";
    });
  }

  Object.values(filters).forEach(f => { f.addEventListener("input", filterTable); f.addEventListener("change", filterTable); });
  resetBtn.addEventListener("click", () => { Object.values(filters).forEach(f => f.value = ""); filterTable(); });

  // ------------------------- Reservation Modal -------------------------
  window.openReservationInfo = function(button) {
    const row = button.closest("tr");
    const name = row.cells[1].innerText;
    const email = row.getAttribute("data-email") || "-"; // <-- getAttribute on row

    document.getElementById("infoName").innerText = name;
    document.getElementById("infoEmail").innerText = email;
    document.getElementById("infoGuestCount").innerText = row.cells[4].innerText;
    document.getElementById("infoStatus").innerText = row.cells[6].innerText;
    document.getElementById("infoDate").innerText = row.cells[2].innerText;
    document.getElementById("infoTime").innerText = row.cells[3].innerText;
    document.getElementById("infoTables").innerText = row.cells[5].innerText;

    document.getElementById("reservationModal").style.display = "block";
  }


  window.closeReservationInfo = function() {
    document.getElementById("reservationModal").style.display = "none";
  }
});


// ------------------------- Floor Plan -------------------------

document.addEventListener('DOMContentLoaded',()=>{
  const floorPlan = document.querySelector('.floor-plan');
    if (floorPlan) {
        loadFloorplanDimensions(floorPlan);
        FloorPlanUtils.initializeFloorPlan(floorPlan);
    }
});

function loadFloorplanDimensions(floorPlanElement) {
    const data = JSON.parse(floorPlanElement.dataset.floorplan);
    const width = data.width || 900;
    const height = data.height || 600;
    floorPlanElement.style.width = width + 'px';
    floorPlanElement.style.height = height + 'px';
    floorPlanElement.style.minWidth = width + 'px';
    floorPlanElement.style.minHeight = height + 'px';
    
    const container = floorPlanElement.parentElement;
    if (container) {
        container.style.minHeight = Math.min(height, 500) + 'px';
    }
}