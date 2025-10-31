document.addEventListener('DOMContentLoaded', function() {
    // Get all necessary elements
    const emailInput = document.getElementById('email');
    const submitBtn = document.querySelector('.btn_submit');
    const emailStep = document.getElementById('email-step');
    const verificationStep = document.getElementById('verification-step');
    const passwordStep = document.getElementById('password-step');
    const emailInstructions = document.getElementById('email-instructions');
    const resendCode = document.getElementById('resend_code');
    const resendLink = document.getElementById('resend_link');
    const passwordInstructions = document.getElementById('password-instructions');
    const newPasswordInput = document.getElementById('new_password');
    const confirmPasswordInput = document.getElementById('confirm_password');
    
    // Get code input boxes
    const codeBoxes = document.querySelectorAll('.code-box');
    
    // State management
    let currentStep = 1;
    let userId = null;
    let verifiedCode = null;
    
    // Update button text and page title based on step
    function updateUI() {
        const pageTitle = document.querySelector('.content_title');
        
        switch(currentStep) {
            case 1:
                submitBtn.textContent = 'Send Code';
                pageTitle.textContent = 'Forgot Password';
                emailStep.style.display = 'block';
                verificationStep.style.display = 'none';
                passwordStep.style.display = 'none';
                emailInstructions.style.display = 'block';
                resendCode.style.display = 'none';
                passwordInstructions.style.display = 'none';
                break;
            case 2:
                submitBtn.textContent = 'Verify Code';
                pageTitle.textContent = 'Enter Verification Code';
                emailStep.style.display = 'none';
                verificationStep.style.display = 'block';
                passwordStep.style.display = 'none';
                emailInstructions.style.display = 'none';
                resendCode.style.display = 'block';
                passwordInstructions.style.display = 'none';
                codeBoxes[0].focus();
                break;
            case 3:
                submitBtn.textContent = 'Reset Password';
                pageTitle.textContent = 'Set New Password';
                emailStep.style.display = 'none';
                verificationStep.style.display = 'none';
                passwordStep.style.display = 'block';
                emailInstructions.style.display = 'none';
                resendCode.style.display = 'none';
                passwordInstructions.style.display = 'block';
                newPasswordInput.focus();
                break;
        }
    }
    
    // Code input functionality
    function setupCodeInputs() {
        codeBoxes.forEach((box, index) => {
            box.addEventListener('input', function(e) {
                // Allow only digits
                this.value = this.value.replace(/[^0-9]/g, '');
                
                // Move to next box if digit entered
                if (this.value && index < codeBoxes.length - 1) {
                    codeBoxes[index + 1].focus();
                }
                
                // Auto-submit if all boxes filled
                if (index === codeBoxes.length - 1 && this.value) {
                    const code = Array.from(codeBoxes).map(box => box.value).join('');
                    if (code.length === 6) {
                        setTimeout(() => submitBtn.click(), 100);
                    }
                }
            });
            
            box.addEventListener('keydown', function(e) {
                // Handle backspace
                if (e.key === 'Backspace' && !this.value && index > 0) {
                    codeBoxes[index - 1].focus();
                }
                
                // Handle paste
                if (e.key === 'v' && (e.ctrlKey || e.metaKey)) {
                    e.preventDefault();
                    navigator.clipboard.readText().then(text => {
                        const digits = text.replace(/[^0-9]/g, '').slice(0, 6);
                        digits.split('').forEach((digit, i) => {
                            if (codeBoxes[i]) {
                                codeBoxes[i].value = digit;
                            }
                        });
                        if (digits.length === 6) {
                            setTimeout(() => submitBtn.click(), 100);
                        }
                    });
                }
            });
        });
    }
    
    // Get code from input boxes
    function getVerificationCode() {
        return Array.from(codeBoxes).map(box => box.value).join('');
    }
    
    // Clear code input boxes
    function clearCodeBoxes() {
        codeBoxes.forEach(box => box.value = '');
        codeBoxes[0].focus();
    }
    
    // Show error message
    function showError(message) {
        window.ErrorMessage.show(message);
    }
    
    // Show success message
    function showSuccess(message) {
        window.MessageBox.showSuccess(message);
    }
    
    // Handle form submission
    function handleSubmit() {
        // Disable submit button to prevent double submission
        submitBtn.disabled = true;
        submitBtn.style.opacity = '0.6';
        
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Processing...';
        
        function resetButton() {
            submitBtn.disabled = false;
            submitBtn.style.opacity = '1';
            submitBtn.textContent = originalText;
        }
        
        if (currentStep === 1) {
            // Step 1: Email submission
            const email = emailInput.value.trim();
            
            if (!email) {
                showError('Please enter your email address.');
                resetButton();
                return;
            }
            
            if (!email.includes('@')) {
                showError('Please enter a valid email address.');
                resetButton();
                return;
            }
            
            // Send email request
            fetch('/rr/auth/forgot-password/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: `email=${encodeURIComponent(email)}`
            })
            .then(response => response.json())
            .then(data => {
                resetButton();
                
                if (data.success) {
                    userId = data.user_id;
                    currentStep = 2;
                    updateUI();
                    showSuccess(data.message);
                } else {
                    showError(data.message);
                }
            })
            .catch(error => {
                resetButton();
                showError('An error occurred. Please try again.');
                console.error('Error:', error);
            });
            
        } else if (currentStep === 2) {
            // Step 2: Code verification
            const code = getVerificationCode();
            
            if (code.length !== 6) {
                showError('Please enter the complete 6-digit verification code.');
                resetButton();
                return;
            }
            
            // Verify code
            fetch('/rr/auth/verify-reset-code/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: `user_id=${userId}&code=${code}`
            })
            .then(response => response.json())
            .then(data => {
                resetButton();
                
                if (data.success) {
                    verifiedCode = data.verified_code;
                    currentStep = 3;
                    updateUI();
                    showSuccess(data.message);
                } else {
                    showError(data.message);
                    clearCodeBoxes();
                }
            })
            .catch(error => {
                resetButton();
                showError('An error occurred. Please try again.');
                clearCodeBoxes();
                console.error('Error:', error);
            });
            
        } else if (currentStep === 3) {
            // Step 3: Password reset
            const newPassword = newPasswordInput.value;
            const confirmPassword = confirmPasswordInput.value;
            
            if (!newPassword || !confirmPassword) {
                showError('Please fill in both password fields.');
                resetButton();
                return;
            }
            
            if (newPassword !== confirmPassword) {
                showError('Passwords do not match.');
                resetButton();
                return;
            }
            
            if (newPassword.length < 8) {
                showError('Password must be at least 8 characters long.');
                resetButton();
                return;
            }
            
            // Reset password
            fetch('/rr/auth/reset-password/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: `user_id=${userId}&code=${verifiedCode}&new_password=${encodeURIComponent(newPassword)}&confirm_password=${encodeURIComponent(confirmPassword)}`
            })
            .then(response => response.json())
            .then(data => {
                resetButton();
                
                if (data.success) {
                    showSuccess(data.message);
                    // Redirect after 2 seconds
                    setTimeout(() => {
                        window.location.href = data.redirect_url || '/rr/auth/login/';
                    }, 2000);
                } else {
                    showError(data.message);
                }
            })
            .catch(error => {
                resetButton();
                showError('An error occurred. Please try again.');
                console.error('Error:', error);
            });
        }
    }
    
    // Handle resend code
    function handleResendCode() {
        if (!userId) return;
        
        resendLink.style.opacity = '0.6';
        resendLink.style.pointerEvents = 'none';
        
        const originalText = resendLink.textContent;
        resendLink.textContent = 'Sending...';
        
        fetch('/rr/auth/resend-reset-code/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: `user_id=${userId}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showSuccess(data.message);
                clearCodeBoxes();
            } else {
                showError(data.message);
            }
        })
        .catch(error => {
            showError('Failed to resend code. Please try again.');
            console.error('Error:', error);
        })
        .finally(() => {
            resendLink.style.opacity = '1';
            resendLink.style.pointerEvents = 'auto';
            resendLink.textContent = originalText;
        });
    }
    
    // Initialize
    updateUI();
    setupCodeInputs();
    
    // Event listeners
    submitBtn.addEventListener('click', function(e) {
        e.preventDefault();
        handleSubmit();
    });
    
    resendLink.addEventListener('click', function(e) {
        e.preventDefault();
        handleResendCode();
    });
    
    // Handle Enter key
    document.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            submitBtn.click();
        }
    });
    
    // Handle input validation
    emailInput.addEventListener('input', function() {
        // Remove error messages when user starts typing
        const errorMessage = document.querySelector('.error-message');
        if (errorMessage) {
            errorMessage.remove();
        }
    });
    
    newPasswordInput.addEventListener('input', function() {
        const errorMessage = document.querySelector('.error-message');
        if (errorMessage) {
            errorMessage.remove();
        }
    });
    
    confirmPasswordInput.addEventListener('input', function() {
        const errorMessage = document.querySelector('.error-message');
        if (errorMessage) {
            errorMessage.remove();
        }
    });
});