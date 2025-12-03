// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function showError(message) {
    window.Notification.error(message);
}

// ============================================================================
// FORM STEP NAVIGATION
// ============================================================================

document.addEventListener('DOMContentLoaded', function () {
    initializeFileUploads();
});
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
    step3: {},
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
    document.getElementById('review-name').textContent = stepData.step1.govt_full_name || '-';
    document.getElementById('review-id-type').textContent = stepData.step1.government_id_type || '-';
    document.getElementById('review-id-number').textContent = stepData.step1.government_id_number || '-';
    document.getElementById('review-address').textContent = stepData.step1.business_address || '-';

    // Files
    const licenseFile = document.getElementById('business-license').files[0];
    const idFile = document.getElementById('government-id-front').files[0];
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