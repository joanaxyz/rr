document.addEventListener('DOMContentLoaded', function () {
    initializeSettings();
    initializeFormHandlers();
});

function initializeSettings() {
    const navItems = document.querySelectorAll('.nav-item');

    navItems.forEach(item => {
        item.addEventListener('click', function (e) {
            e.preventDefault();
            const section = this.getAttribute('data-section');
            switchSection(section);

            // Update active nav item
            navItems.forEach(nav => nav.classList.remove('active'));
            this.classList.add('active');
        });
    });
}

function switchSection(section) {
    const sections = document.querySelectorAll('.settings-section');
    sections.forEach(sec => sec.classList.remove('active'));

    const sectionId = `${section}-section`;
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.classList.add('active');
        targetSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// ============================================================================
// MODAL MANAGEMENT
// ============================================================================

function openOwnerVerificationModal() {
    const modal = document.getElementById('owner-verification-modal');
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
}

function openPasswordModal() {
    const modal = document.getElementById('password-modal');
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = 'auto';
    }
}

// Close modal on background click
document.addEventListener('click', function (e) {
    if (e.target.classList.contains('modal')) {
        closeModal(e.target.id);
    }
});

// Close modal on Escape key
document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
        const activeModal = document.querySelector('.modal.active');
        if (activeModal) {
            closeModal(activeModal.id);
        }
    }
});


function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-error';
    errorDiv.innerHTML = `
        <i class="fas fa-exclamation-circle"></i>
        <span>${message}</span>
        <button onclick="this.parentElement.remove()" class="alert-close">&times;</button>
    `;

    const container = document.querySelector('.settings-section.active') || document.querySelector('.modal-body');
    if (container) {
        container.insertAdjacentElement('afterbegin', errorDiv);
        errorDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }
}

function showSuccess(message) {
    window.Notification.success(message);
}

function initializeOwnerVerification() {
    // Mark step 1 as active initially
    const firstStep = document.getElementById('step-1');
    if (firstStep && !firstStep.classList.contains('active')) {
        firstStep.classList.add('active');
        const firstStepIndicator = document.querySelector('.step');
        if (firstStepIndicator) {
            firstStepIndicator.classList.add('active');
        }
    }
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// ============================================================================

function formatPhoneNumber(input) {
    let value = input.value.replace(/\D/g, '');
    if (value.length >= 10) {
        value = value.slice(0, 10);
    }
    input.value = value;
}

// ============================================================================
// FORM HANDLERS - PROFILE AND PASSWORD
// ============================================================================

function initializeFormHandlers() {
    // Profile form handler
    const profileForm = document.getElementById('profile-form');
    if (profileForm) {
        profileForm.addEventListener('submit', handleProfileFormSubmit);
    }

    // Password form handler
    const passwordForm = document.getElementById('password-form');
    if (passwordForm) {
        passwordForm.addEventListener('submit', handlePasswordFormSubmit);
    }
}

function handleProfileFormSubmit(e) {
    e.preventDefault();
    
    const form = e.target;
    
    // Client-side validation first
    const validationErrors = validateProfileForm(form);
    if (validationErrors.length > 0) {
        displayFormErrors('profile-form-errors', validationErrors);
        clearAllFieldErrors(form);
        window.LoadingOverlay.hide();
        return;
    }
    
    // Clear previous errors
    clearFormErrors('profile-form-errors');

    
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);

    APIClient.post('/settings/update-profile/', data, { showOverlay: true })
        .then(responseData => {
            if (responseData.success) {
                showSuccess(responseData.message);
                clearAllFieldErrors(form);
            } else {
                // Handle backend errors
                if (responseData.errors && typeof responseData.errors === 'object') {
                    displayFieldErrors('profile-form-errors', responseData.errors);
                } else {
                    displayFormErrors('profile-form-errors', [responseData.message || 'Error updating profile']);
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            displayFormErrors('profile-form-errors', ['An error occurred. Please try again.']);
        })
}

/**
 * Validate profile form fields (client-side)
 */
function validateProfileForm(form) {
    const errors = [];
    
    const firstNameField = form.querySelector('#first-name');
    const lastNameField = form.querySelector('#last-name');
    const emailField = form.querySelector('#email');
    const phoneField = form.querySelector('#phone');
    
    console.log('Form fields:', { firstNameField, lastNameField, emailField, phoneField });
    
    const firstName = firstNameField?.value.trim() || '';
    const lastName = lastNameField?.value.trim() || '';
    const email = emailField?.value.trim() || '';
    const phone = phoneField?.value.trim() || '';
    
    console.log('fields: ', {firstName, lastName, email, phone});
    // Validate required fields
    if (!firstName) {
        errors.push('First name is required');
    }
    
    if (!lastName) {
        errors.push('Last name is required');
    }
    
    if (!email) {
        errors.push('Email is required');
    } else if (!isValidEmail(email)) {
        errors.push('Please enter a valid email address');
    }
    
    // Validate phone if provided
    if (phone && !/^\d{10}$/.test(phone.replace(/\D/g, ''))) {
        errors.push('Phone number must be 10 digits');
    }
    
    return errors;
}

function handlePasswordFormSubmit(e) {
    e.preventDefault();
    
    const form = e.target;
    
    // Client-side validation first
    const validationErrors = validatePasswordForm(form);
    if (validationErrors.length > 0) {
        displayFormErrors('password-form-errors', validationErrors);
        clearAllFieldErrors(form);
        window.LoadingOverlay.hide();
        return;
    }
    
    // Clear previous errors
    clearFormErrors('password-form-errors');
    ;
    
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);

    APIClient.post('/settings/change-password/', data, { showOverlay: true })
        .then(responseData => {
            if (responseData.success) {
                showSuccess(responseData.message);
                form.reset();
                clearAllFieldErrors(form);
                setTimeout(() => {
                    closeModal('password-modal');
                }, 1500);
            } else {
                // Handle backend errors
                if (responseData.errors && typeof responseData.errors === 'object') {
                    displayFieldErrors('password-form-errors', responseData.errors);
                } else {
                    displayFormErrors('password-form-errors', [responseData.message || 'Error updating password']);
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            displayFormErrors('password-form-errors', ['An error occurred. Please try again.']);
        })
}

/**
 * Validate password form fields (client-side)
 * Returns array of error messages
 */
function validatePasswordForm(form) {
    const errors = [];
    const currentPassword = form.querySelector('#current-password').value.trim();
    const newPassword = form.querySelector('#new-password').value.trim();
    const confirmPassword = form.querySelector('#confirm-password').value.trim();
    
    // Clear previous field errors
    clearAllFieldErrors(form);
    
    // Validate required fields
    if (!currentPassword) {
        errors.push('Current password is required');
    }
    
    if (!newPassword) {
        errors.push('New password is required');
    }
    
    if (!confirmPassword) {
        errors.push('Confirm password is required');
    }
    
    // Validate password match
    if (newPassword && confirmPassword && newPassword !== confirmPassword) {
        errors.push('New passwords do not match');
    }
    
    // Validate password length
    if (newPassword && newPassword.length < 8) {
        errors.push('New password must be at least 8 characters');
    }
    
    return errors;
}

/**
 * Display form-level errors in the error container
 */
function displayFormErrors(containerId, errorMessages) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    if (errorMessages.length === 0) {
        container.classList.remove('active');
        return;
    }
    
    // Create error list
    let html = '<ul class="form-errors-list">';
    errorMessages.forEach(msg => {
        html += `<li>${escapeHtml(msg)}</li>`;
    });
    html += '</ul>';
    
    container.innerHTML = html;
    container.classList.add('active');
    
    // Scroll error into view
    container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

/**
 * Display field-level errors from backend response
 * (Inline field errors have been removed - only form-level errors are displayed)
 */
function displayFieldErrors(containerId, fieldErrors) {
    const formErrors = [];
    
    for (const [fieldName, messages] of Object.entries(fieldErrors)) {
        const errorMessages = Array.isArray(messages) ? messages : [messages];
        formErrors.push(...errorMessages);
    }
    
    // Display form-level errors if any
    if (formErrors.length > 0) {
        displayFormErrors(containerId, formErrors);
    }
}

/**
 * Set error state on a specific field
 * (Inline field errors have been removed - this function is kept for backward compatibility)
 */
function setFieldError(fieldId, errorMessage) {
    // Inline field errors are no longer used
    // Error messages are displayed in the form-level error container instead
}

/**
 * Clear all field errors in a form
 */
function clearAllFieldErrors(form) {
    const fields = form.querySelectorAll('input, textarea, select');
    fields.forEach(field => {
        field.classList.remove('error');
    });
}

/**
 * Clear the form-level error container
 */
function clearFormErrors(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
        container.classList.remove('active');
        container.innerHTML = '';
    }
}

/**
 * Utility: Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}
