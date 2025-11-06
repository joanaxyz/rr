// Prompt user for a cancellation reason
async function showCancelReason(form) {
  window.MessageBox.showPrompt("Please provide a reason for cancellation:", {
    title: "Cancel Reservation",
    placeholder: "Type your reason here...",
    validator: (value) => {
      if (!value || value.trim().length === 0) {
        return "Please enter a reason before submitting.";
      }
      return true;
    }
  })
  .then(reason => {
    submitCancel(reason, form);
  })
  .catch(err => {
    console.log(err);
  });
}

// Submit cancel form with reason
function submitCancel(reason, form) {
  if (form) {
    form.querySelector(".cancel-reason-input").value = reason;
    form.submit();
  }
}

// Confirm before restoring cancelled reservation
function restoreReservation(form) {
  if (form) {
    window.MessageBox.showConfirm("Do you want to restore this cancelled reservation?", () => {
      form.submit();
    });
  }
}

// Redirect to edit reservation page
function editReservation(reservationId) {
  window.location.href = `/reservations/${reservationId}/edit/`;
}
