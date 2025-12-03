/**
 * Open Reservation Info Modal
 * @param {HTMLElement} button - The info button element
 */
function openReservationInfo(button) {
  const reservationId = button.getAttribute('data-reservation-id');
  
  if (!reservationId) {
    console.error('Reservation ID not found');
    return;
  }

  // Extract data from the table row
  const row = button.closest('tr');
  const cells = row.querySelectorAll('td');
  
  // Get text content from the row
  const name = cells[1]?.textContent.trim() || '-';
  const date = cells[2]?.textContent.trim() || '-';
  const time = cells[3]?.textContent.trim() || '-';
  const guestCount = cells[4]?.textContent.trim() || '-';
  const tables = cells[5]?.textContent.trim() || '-';
  const status = cells[6]?.querySelector('.status-badge')?.textContent.trim() || '-';

  // Populate modal with data from table
  document.getElementById('infoName').textContent = name;
  document.getElementById('infoDate').textContent = date;
  document.getElementById('infoTime').textContent = time;
  document.getElementById('infoGuestCount').textContent = guestCount;
  document.getElementById('infoTables').textContent = tables;
  document.getElementById('infoStatus').textContent = status;

  // Fetch additional data (email, notes, cancellation_reason, created_at) from server
  fetchReservationDetails(reservationId);

  // Show modal
  const modal = document.getElementById('reservationModal');
  modal.style.display = 'flex';

  // Close modal when clicking on the overlay (but not the modal content)
  modal.addEventListener('click', function(e) {
    if (e.target === modal) {
      closeReservationInfo();
    }
  });
}

/**
 * Fetch detailed reservation information from server
 * @param {string} reservationId - The reservation ID
 */
async function fetchReservationDetails(reservationId) {
  try {
    const apiUrl = window.getReservationApiUrl 
        ? window.getReservationApiUrl(reservationId)
        : `/reservations/api/get/${reservationId}/`;
    const response = await APIClient.get(apiUrl, {
      loadingText: 'Loading reservation details...'
    });

    const data = response.data;
    // Update modal with fetched data
    document.getElementById('infoEmail').textContent = data.email || '-';
    document.getElementById('infoNotes').textContent = data.notes || '-';
    document.getElementById('infoCancellationReason').textContent = data.cancellation_reason || '-';
    
    // Format created_at timestamp
    if (data.created_at) {
      const createdDate = new Date(data.created_at);
      document.getElementById('infoCreatedAt').textContent = createdDate.toLocaleString();
    } else {
      document.getElementById('infoCreatedAt').textContent = '-';
    }
  } catch (error) {
    console.warn('Could not fetch detailed reservation data:', error);
    // Set defaults if fetch fails
    document.getElementById('infoEmail').textContent = '-';
    document.getElementById('infoNotes').textContent = '-';
    document.getElementById('infoCancellationReason').textContent = '-';
    document.getElementById('infoCreatedAt').textContent = '-';
  }
}

/**
 * Close Reservation Info Modal
 */
function closeReservationInfo() {
  const modal = document.getElementById('reservationModal');
  modal.style.display = 'none';

  // Clear modal data
  document.getElementById('infoName').textContent = '-';
  document.getElementById('infoEmail').textContent = '-';
  document.getElementById('infoGuestCount').textContent = '-';
  document.getElementById('infoDate').textContent = '-';
  document.getElementById('infoTime').textContent = '-';
  document.getElementById('infoTables').textContent = '-';
  document.getElementById('infoStatus').textContent = '-';
  document.getElementById('infoNotes').textContent = '-';
  document.getElementById('infoCancellationReason').textContent = '-';
  document.getElementById('infoCreatedAt').textContent = '-';
}

document.addEventListener('DOMContentLoaded', function() {
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      const modal = document.getElementById('reservationModal');
      if (modal && modal.style.display !== 'none') {
        closeReservationInfo();
      }
    }
  });
});