/**
 * Settings Page JavaScript
 * Handles navigation, form submissions, file uploads, and owner verification
 */

// ============================================================================
// SECTION NAVIGATION
// ============================================================================

document.addEventListener('DOMContentLoaded', function () {
    initializeSettings();
    initializeOwnerVerification();
    initializeFileUploads();
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

// ============================================================================
// FORM STEP NAVIGATION
// ============================================================================

function nextStep(stepNumber) {
    const currentStep = document.querySelector('.form-step.active');
    
    // Validate current step
    if (!validateStep(currentStep)) {
        showError('Please fill in all required fields');
        return;
    }

    // Save step data
    saveStepData();

    // Move to next step
    const steps = document.querySelectorAll('.form-step');
    const stepIndicators = document.querySelectorAll('.step');

    steps.forEach(step => step.classList.remove('active'));
    stepIndicators.forEach(indicator => indicator.classList.remove('active'));

    const nextStepElement = document.getElementById(`step-${stepNumber}`);
    if (nextStepElement) {
        nextStepElement.classList.add('active');
    }

    if (stepIndicators[stepNumber - 1]) {
        stepIndicators[stepNumber - 1].classList.add('active');
    }

    // Update review section if moving to step 3
    if (stepNumber === 3) {
        updateReviewSection();
    }
}

function previousStep(stepNumber) {
    const steps = document.querySelectorAll('.form-step');
    const stepIndicators = document.querySelectorAll('.step');

    steps.forEach(step => step.classList.remove('active'));
    stepIndicators.forEach(indicator => indicator.classList.remove('active'));

    const prevStepElement = document.getElementById(`step-${stepNumber}`);
    if (prevStepElement) {
        prevStepElement.classList.add('active');
    }

    if (stepIndicators[stepNumber - 1]) {
        stepIndicators[stepNumber - 1].classList.add('active');
    }
}

// ============================================================================
// FORM VALIDATION
// ============================================================================

function validateStep(stepElement) {
    const requiredInputs = stepElement.querySelectorAll('[required]');
    let isValid = true;

    requiredInputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('error');
            isValid = false;
        } else {
            input.classList.remove('error');
        }

        // Additional validation for specific fields
        if (input.type === 'email' && input.value && !isValidEmail(input.value)) {
            input.classList.add('error');
            isValid = false;
        }
    });

    return isValid;
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// ============================================================================
// STEP DATA MANAGEMENT
// ============================================================================

const stepData = {
    step1: {},
    step2: {},
};

function saveStepData() {
    const activeStep = document.querySelector('.form-step.active');
    const inputs = activeStep.querySelectorAll('input, select, textarea');
    const stepNumber = activeStep.id.replace('step-', '');

    inputs.forEach(input => {
        if (input.name && input.type !== 'file') {
            stepData[`step${stepNumber}`][input.name] = input.value;
        }
    });
}

// ============================================================================
// REVIEW SECTION
// ============================================================================

function updateReviewSection() {
    // Personal Information
    document.getElementById('review-name').textContent = stepData.step1.full_name || '-';
    document.getElementById('review-id-type').textContent = stepData.step1.id_type || '-';
    document.getElementById('review-id-number').textContent = stepData.step1.id_number || '-';
    document.getElementById('review-address').textContent = stepData.step1.business_address || '-';

    // Files
    const licenseFile = document.getElementById('business-license').files[0];
    const idFile = document.getElementById('government-id-doc').files[0];
    const ownershipFile = document.getElementById('proof-ownership').files[0];

    document.getElementById('review-license').textContent = licenseFile ? licenseFile.name : '-';
    document.getElementById('review-id-doc').textContent = idFile ? idFile.name : '-';
    document.getElementById('review-ownership').textContent = ownershipFile ? ownershipFile.name : '-';
}

// ============================================================================
// FILE UPLOAD HANDLING
// ============================================================================

function initializeFileUploads() {
    const uploadBoxes = document.querySelectorAll('.file-upload-box');

    uploadBoxes.forEach(box => {
        box.addEventListener('click', function () {
            const input = this.querySelector('input[type="file"]');
            if (input) {
                input.click();
            }
        });

        box.addEventListener('dragover', function (e) {
            e.preventDefault();
            this.classList.add('dragover');
        });

        box.addEventListener('dragleave', function () {
            this.classList.remove('dragover');
        });

        box.addEventListener('drop', function (e) {
            e.preventDefault();
            this.classList.remove('dragover');
            const input = this.querySelector('input[type="file"]');
            if (input && e.dataTransfer.files.length) {
                input.files = e.dataTransfer.files;
                handleFileSelect(input);
            }
        });

        const fileInput = box.querySelector('input[type="file"]');
        if (fileInput) {
            fileInput.addEventListener('change', function () {
                handleFileSelect(this);
            });
        }
    });
}

function handleDrop(e, type) {
    e.preventDefault();
    const fileInput = document.getElementById(
        type === 'license'
            ? 'business-license'
            : type === 'id'
            ? 'government-id-doc'
            : 'proof-ownership'
    );
    if (fileInput && e.dataTransfer.files.length) {
        fileInput.files = e.dataTransfer.files;
        handleFileSelect(fileInput);
    }
}

function handleDragOver(e) {
    e.preventDefault();
    e.target.closest('.file-upload-box')?.classList.add('dragover');
}

function handleDragLeave(e) {
    e.target.closest('.file-upload-box')?.classList.remove('dragover');
}

function handleFileSelect(fileInput) {
    const file = fileInput.files[0];
    if (!file) return;

    // Validation
    const validTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/gif'];
    const maxSize = 10 * 1024 * 1024; // 10MB

    if (!validTypes.includes(file.type)) {
        showError(`Invalid file type. Only PDF, JPG, PNG, and GIF are allowed.`);
        fileInput.value = '';
        return;
    }

    if (file.size > maxSize) {
        showError(`File size exceeds 10MB limit.`);
        fileInput.value = '';
        return;
    }

    // Show preview
    const previewId = fileInput.id + '-preview';
    const preview = document.getElementById(previewId) || document.createElement('div');
    preview.id = previewId;
    preview.className = 'file-preview active';
    preview.innerHTML = `
        <div class="file-preview-icon"><i class="fas fa-check-circle"></i></div>
        <div class="file-preview-info">
            <div class="file-preview-name">${file.name}</div>
            <div class="file-preview-size">${formatFileSize(file.size)}</div>
        </div>
        <div class="file-preview-remove" onclick="removeFile('${fileInput.id}')">
            <i class="fas fa-times"></i>
        </div>
    `;

    const uploadBox = fileInput.closest('.file-upload-box');
    if (uploadBox && !uploadBox.nextElementSibling?.id.includes('preview')) {
        uploadBox.insertAdjacentElement('afterend', preview);
    } else if (uploadBox) {
        uploadBox.nextElementSibling.replaceWith(preview);
    }
}

function removeFile(inputId) {
    const input = document.getElementById(inputId);
    if (input) {
        input.value = '';
        const preview = document.getElementById(inputId + '-preview');
        if (preview) {
            preview.classList.remove('active');
            preview.innerHTML = '';
        }
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// ============================================================================
// OWNER VERIFICATION FORM SUBMISSION
// ============================================================================

const verificationForm = document.getElementById('owner-verification-form');
if (verificationForm) {
    verificationForm.addEventListener('submit', function (e) {
        e.preventDefault();

        // Final validation
        if (!document.getElementById('agree-terms').checked) {
            showError('You must agree to the terms before submitting');
            return;
        }

        // Collect form data including files
        const formData = new FormData(this);

        // Submit
        submitOwnerVerification(formData);
    });
}

function submitOwnerVerification(formData) {
    fetch('/accounts/apply-owner/', {
        method: 'POST',
        body: formData,
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showSuccess('Application submitted successfully! We will review your documents within 1-2 business days.');
                setTimeout(() => {
                    location.reload();
                }, 2000);
            } else {
                showError(data.message || 'Error submitting application');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showError('An error occurred. Please try again.');
        });
}

// ============================================================================
// ERROR/SUCCESS MESSAGES
// ============================================================================

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
    window.MessageBox.showSuccess(message);
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
        return;
    }
    
    // Clear previous errors
    clearFormErrors('profile-form-errors');

    
    const formData = new FormData(form);

    fetch('/settings/update-profile/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showSuccess(data.message);
                clearAllFieldErrors(form);
            } else {
                // Handle backend errors
                if (data.errors && typeof data.errors === 'object') {
                    displayFieldErrors('profile-form-errors', data.errors);
                } else {
                    displayFormErrors('profile-form-errors', [data.message || 'Error updating profile']);
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
    
    // Clear previous field errors
    clearAllFieldErrors(form);
    
    const firstName = form.querySelector('#first-name').value.trim();
    const lastName = form.querySelector('#last-name').value.trim();
    const email = form.querySelector('#email').value.trim();
    const phone = form.querySelector('#phone').value.trim();
    
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
        return;
    }
    
    // Clear previous errors
    clearFormErrors('password-form-errors');
    ;
    
    const formData = new FormData(form);

    fetch('/settings/change-password/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showSuccess(data.message);
                form.reset();
                clearAllFieldErrors(form);
                setTimeout(() => {
                    closeModal('password-modal');
                }, 1500);
            } else {
                // Handle backend errors
                if (data.errors && typeof data.errors === 'object') {
                    displayFieldErrors('password-form-errors', data.errors);
                } else {
                    displayFormErrors('password-form-errors', [data.message || 'Error updating password']);
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
