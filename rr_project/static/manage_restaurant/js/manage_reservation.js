function confirmReservation(form, name, table_numbers) {
  window.MessageBox.showConfirm(`Are you sure you want to confirm reservation by ${name} at table/s ${table_numbers}?`, ()=>{
    document.querySelector('input[name="action"]').value = "confirm";
    form.submit();
  });
}

function completeReservation(form, name, table_numbers, table_numbers) {
  window.MessageBox.showConfirm(`Are you sure you want to complete reservation by ${name} at table/s ${table_numbers}?`, ()=>{
    document.querySelector('input[name="action"]').value = "complete";
    form.submit();
  });
}

function deleteReservation(form, name, table_numbers, table_numbers) {
  window.MessageBox.showConfirm(`Are you sure you want to delete reservation by ${name} at table/s ${table_numbers}?`, ()=>{
    document.querySelector('input[name="action"]').value = "delete";
    form.submit();
  });
}

function cancelReservation(form, name, table_numbers) {
  window.MessageBox.showConfirm(
    `Are you sure you want to cancel reservation by ${name} at table/s ${table_numbers}?`,
    () => {
      promptReason((reason) => {
        const reasonInput = document.querySelector('input[name="cancellation_reason"]');
        if (reasonInput) {
          reasonInput.value = reason;
        }
        document.querySelector('input[name="action"]').value = "cancel";
        form.submit();
      });
    }
  );
}

function confirmCancelReservation(form, name, table_numbers) {
    window.MessageBox.showConfirm(
    `Are you sure you want to confirm cancel reservation by ${name} at table/s ${table_numbers}?`,
    () => {
      document.querySelector('input[name="action"]').value = "confirm_canel";
        form.submit();
    }
  );
}

function promptReason(callback) {
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
    callback(reason);
  })
  .catch(err => {
    console.log(err);
  });
}
