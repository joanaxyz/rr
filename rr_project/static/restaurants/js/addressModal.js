
document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('addressModal');
    const addressEditTrigger = document.getElementById('addressEditTrigger');
    const modalClose = document.getElementById('modalClose');
    const modalCancel = document.getElementById('modalCancel');
    const modalOverlay = document.querySelector('.modal-overlay');
    const addressForm = document.getElementById('addressForm');

    // Open modal
    addressEditTrigger.addEventListener('click', () => {
        modal.classList.add('active');
    });

    // Close modal functions
    const closeModal = () => {
        modal.classList.remove('active');
    };

    modalClose.addEventListener('click', closeModal);
    modalCancel.addEventListener('click', closeModal);
    modalOverlay.addEventListener('click', closeModal);

    // Handle form submission
    addressForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = new FormData(addressForm);
        const data = {
            street_number: formData.get('street_number'),
            street_name: formData.get('street_name'),
            street_block: formData.get('street_block'),
            city: formData.get('city'),
            postal_code: formData.get('postal_code'),
        };
        
        // Close modal after submission
        closeModal();
        
        // Update the address display
        const addressElement = document.getElementById('address');
        const fullAddress = [
            data.street_number,
            data.street_name,
            data.street_block,
            data.city,
            data.postal_code
        ].filter(Boolean).join(', ');
        
        if (fullAddress) {
            addressElement.textContent = fullAddress;
        }

        applyFiltersAndSort();
    });

    // Close modal when pressing Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeModal();
        }
    });
});