document.addEventListener('DOMContentLoaded', () => {
    // Handle all forms present at page load
    attachSubmitListeners(document);
});

// Also watch for dynamically added modals
document.addEventListener('DOMNodeInserted', (e) => {
    if (e.target.tagName === 'FORM' || e.target.querySelector?.('form')) {
        attachSubmitListeners(e.target);
    }
}, true);

function attachSubmitListeners(container) {
    const forms = container.querySelectorAll('form');
    forms.forEach(form => {
        const submitBtn = form.querySelector('button[type="submit"]');
        if (!submitBtn) return;

        form.addEventListener('submit', () => {
            submitBtn.disabled = true;
            submitBtn.style.opacity = '0.6';
            submitBtn.style.cursor = 'not-allowed';
            
            submitBtn.innerHTML = `
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" class="animate-spin">
                    <path d="M12,4V2A10,10 0 0,0 2,12H4A8,8 0 0,1 12,4Z"/>
                </svg>
                Processing...
            `;

            const style = document.createElement('style');
            style.textContent = `
                .animate-spin {
                    animation: spin 1s linear infinite;
                }
                @keyframes spin {
                    from { transform: rotate(0deg); }
                    to { transform: rotate(360deg); }
                }
            `;
            document.head.appendChild(style);
        });
    });
}
