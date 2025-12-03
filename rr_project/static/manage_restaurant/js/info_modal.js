/**
 * Open Reservation Info Modal
 * @param {HTMLElement} button - The info button element
 */
let reservationModalInstance = null;

function openReservationInfo(button) {
  console.log('openReservationInfo called', button);
  
  // Check if Modal is available
  if (!window.Modal || !window.Modal.show) {
    console.error('Modal.show is not available');
    alert('Modal system not loaded. Please refresh the page.');
    return;
  }
  
  // Extract data from the table row
  const row = button.closest('tr');
  if (!row) {
    console.error('Table row not found');
    return;
  }
  
  const cells = row.querySelectorAll('td');
  
  // Get text content from the row
  const name = cells[1]?.textContent.trim() || '-';
  const date = cells[2]?.textContent.trim() || '-';
  const time = cells[3]?.textContent.trim() || '-';
  const guestCount = cells[4]?.textContent.trim() || '-';
  const tables = cells[5]?.textContent.trim() || '-';
  const status = cells[6]?.querySelector('.status-badge')?.textContent.trim() || '-';

  // Get reservation ID from the form's hidden input
  const form = row.querySelector('form');
  const reservationIdInput = form ? form.querySelector('input[name="reservation_id"]') : null;
  const reservationId = reservationIdInput ? reservationIdInput.value : null;

  console.log('Reservation data:', { name, date, time, guestCount, tables, status, reservationId });

  // Create modal content with initial data
  const modalContent = `
    <div class="reservation-info-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem;">
      <div class="info-item" style="display: flex; flex-direction: column; gap: 0.5rem;">
        <label style="font-size: 0.75rem; font-weight: 600; color: var(--gray-600); text-transform: uppercase; letter-spacing: 0.5px;">Guest Name</label>
        <p id="infoName" style="font-size: 0.875rem; color: var(--gray-900); margin: 0;">${escapeHtml(name)}</p>
      </div>
      <div class="info-item" style="display: flex; flex-direction: column; gap: 0.5rem;">
        <label style="font-size: 0.75rem; font-weight: 600; color: var(--gray-600); text-transform: uppercase; letter-spacing: 0.5px;">Email</label>
        <p id="infoEmail" style="font-size: 0.875rem; color: var(--gray-900); margin: 0;">-</p>
      </div>
      <div class="info-item" style="display: flex; flex-direction: column; gap: 0.5rem;">
        <label style="font-size: 0.75rem; font-weight: 600; color: var(--gray-600); text-transform: uppercase; letter-spacing: 0.5px;">Guest Count</label>
        <p id="infoGuestCount" style="font-size: 0.875rem; color: var(--gray-900); margin: 0;">${escapeHtml(guestCount)}</p>
      </div>
      <div class="info-item" style="display: flex; flex-direction: column; gap: 0.5rem;">
        <label style="font-size: 0.75rem; font-weight: 600; color: var(--gray-600); text-transform: uppercase; letter-spacing: 0.5px;">Status</label>
        <p id="infoStatus" style="font-size: 0.875rem; color: var(--gray-900); margin: 0;">${escapeHtml(status)}</p>
      </div>
      <div class="info-item" style="display: flex; flex-direction: column; gap: 0.5rem;">
        <label style="font-size: 0.75rem; font-weight: 600; color: var(--gray-600); text-transform: uppercase; letter-spacing: 0.5px;">Reservation Date</label>
        <p id="infoDate" style="font-size: 0.875rem; color: var(--gray-900); margin: 0;">${escapeHtml(date)}</p>
      </div>
      <div class="info-item" style="display: flex; flex-direction: column; gap: 0.5rem;">
        <label style="font-size: 0.75rem; font-weight: 600; color: var(--gray-600); text-transform: uppercase; letter-spacing: 0.5px;">Reservation Time</label>
        <p id="infoTime" style="font-size: 0.875rem; color: var(--gray-900); margin: 0;">${escapeHtml(time)}</p>
      </div>
      <div class="info-item" style="display: flex; flex-direction: column; gap: 0.5rem;">
        <label style="font-size: 0.75rem; font-weight: 600; color: var(--gray-600); text-transform: uppercase; letter-spacing: 0.5px;">Tables</label>
        <p id="infoTables" style="font-size: 0.875rem; color: var(--gray-900); margin: 0;">${escapeHtml(tables)}</p>
      </div>
      <div class="info-item" style="display: flex; flex-direction: column; gap: 0.5rem;">
        <label style="font-size: 0.75rem; font-weight: 600; color: var(--gray-600); text-transform: uppercase; letter-spacing: 0.5px;">Booked At</label>
        <p id="infoCreatedAt" style="font-size: 0.875rem; color: var(--gray-900); margin: 0;">-</p>
      </div>
      <div class="info-item full-width" style="grid-column: 1 / -1; display: flex; flex-direction: column; gap: 0.5rem;">
        <label style="font-size: 0.75rem; font-weight: 600; color: var(--gray-600); text-transform: uppercase; letter-spacing: 0.5px;">Notes</label>
        <p id="infoNotes" style="font-size: 0.875rem; color: var(--gray-900); margin: 0; white-space: pre-wrap; word-break: break-word;">-</p>
      </div>
      <div class="info-item full-width" style="grid-column: 1 / -1; display: flex; flex-direction: column; gap: 0.5rem;">
        <label style="font-size: 0.75rem; font-weight: 600; color: var(--gray-600); text-transform: uppercase; letter-spacing: 0.5px;">Cancellation Reason</label>
        <p id="infoCancellationReason" style="font-size: 0.875rem; color: var(--gray-900); margin: 0; white-space: pre-wrap; word-break: break-word;">-</p>
      </div>
    </div>
  `;

  console.log('Calling Modal.show...');
  try {
    reservationModalInstance = window.Modal.show({
      title: 'Reservation Details',
      content: modalContent,
      maxWidth: '600px',
      showCloseButton: true,
      closeOnOverlayClick: true,
      onClose: () => {
        reservationModalInstance = null;
      }
    });
    console.log('Modal.show returned:', reservationModalInstance);
  } catch (error) {
    console.error('Error calling Modal.show:', error);
    alert('Error opening modal: ' + error.message);
    return;
  }

  // Fetch additional data (email, notes, cancellation_reason, created_at) from server
  if (reservationId) {
    fetchReservationDetails(reservationId, reservationModalInstance);
  } else {
    console.warn('Reservation ID not found, using default values');
  }
}

/**
 * Fetch detailed reservation information from server
 * @param {string} reservationId - The reservation ID
 * @param {Object} modalInstance - The modal instance to update
 */
async function fetchReservationDetails(reservationId, modalInstance) {
  try {
    const apiUrl = window.getReservationApiUrl 
        ? window.getReservationApiUrl(reservationId)
        : `/reservations/api/get/${reservationId}/`;
    const response = await APIClient.get(apiUrl, {
      loadingText: 'Loading reservation details...'
    });

    const data = response.data;
    // Update modal with fetched data
    if (modalInstance) {
      const emailEl = modalInstance.getElement('#infoEmail');
      const notesEl = modalInstance.getElement('#infoNotes');
      const cancellationReasonEl = modalInstance.getElement('#infoCancellationReason');
      const createdAtEl = modalInstance.getElement('#infoCreatedAt');
      
      if (emailEl) emailEl.textContent = data.email || '-';
      if (notesEl) notesEl.textContent = data.notes || '-';
      if (cancellationReasonEl) cancellationReasonEl.textContent = data.cancellation_reason || '-';
      
      // Format created_at timestamp
      if (createdAtEl) {
        if (data.created_at) {
          const createdDate = new Date(data.created_at);
          createdAtEl.textContent = createdDate.toLocaleString();
        } else {
          createdAtEl.textContent = '-';
        }
      }
    }
  } catch (error) {
    console.warn('Could not fetch detailed reservation data:', error);
    // Set defaults if fetch fails
    if (modalInstance) {
      const emailEl = modalInstance.getElement('#infoEmail');
      const notesEl = modalInstance.getElement('#infoNotes');
      const cancellationReasonEl = modalInstance.getElement('#infoCancellationReason');
      const createdAtEl = modalInstance.getElement('#infoCreatedAt');
      
      if (emailEl) emailEl.textContent = '-';
      if (notesEl) notesEl.textContent = '-';
      if (cancellationReasonEl) cancellationReasonEl.textContent = '-';
      if (createdAtEl) createdAtEl.textContent = '-';
    }
  }
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
