// Verify Account JavaScript functionality

function resendVerificationEmail(userId) {
    const button = document.getElementById('btn_resend');
    const messageContainer = document.getElementById('message-container');
    
    // Disable button during request
    button.disabled = true;
    button.textContent = 'Sending...';
    
    // Clear previous messages
    messageContainer.innerHTML = '';
    
    fetch(`/rr/auth/resend-verification/${userId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showMessage(data.message, 'success');
        } else {
            showMessage(data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showMessage('An error occurred while sending the verification email.', 'error');
    })
    .finally(() => {
        // Re-enable button
        button.disabled = false;
        button.textContent = 'Resend Verification Email';
    });
}

function showMessage(message, type) {
    const messageContainer = document.getElementById('message-container');
    const messageDiv = document.createElement('div');
    messageDiv.className = `alert alert-${type}`;
    messageDiv.style.cssText = `
        padding: 12px;
        margin: 10px 0;
        border-radius: 4px;
        ${type === 'success' ? 
            'background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb;' : 
            'background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb;'
        }
    `;
    messageDiv.textContent = message;
    messageContainer.appendChild(messageDiv);
    
    // Auto-remove message after 5 seconds
    setTimeout(() => {
        if (messageDiv.parentNode) {
            messageDiv.parentNode.removeChild(messageDiv);
        }
    }, 5000);
}

// Function to get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('Verify account page loaded');
});