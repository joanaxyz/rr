async function showCancelReason(form) {
  window.MessageBox.showPrompt("Please provide a reason for cancellation:", {
    title: "Cancel Reservation",
    placeholder: "Type your reason here...",
    validator: (value) => {
      if (!value || value.trim().length === 0) {
        return "Please enter a reason before submitting.";
      }
      return true;
    },
  })
  .then(reason => {
    submitCancel(reason, form);
  })
  .catch(err => {
    console.log(err);
  });
}

function submitCancel(reason, form) {
  if (form) {
    form.querySelector(".cancel-reason-input").value = reason;
    form.submit();
  }
}

function deleteReservation(form) {
  if (form) {
    window.MessageBox.showConfirm("Are you sure you want to move this reservation to trash?", () => {
      form.submit();
    });
  }
}

function restoreReservation(form) {
  if (form) {
    window.MessageBox.showConfirm("Restore this reservation?", () => {
      form.submit();
    });
  }
}

function editReservation(reservationId) {
  window.location.href = `/reservations/${reservationId}/edit/`;
}
