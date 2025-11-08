document.addEventListener('DOMContentLoaded', () => {
    // Handle all forms present at page load
    attachSubmitListeners(document);
});

// Also watch for dynamically added modals
document.addEventListener('DOMNodeInserted', (e) => {
    if (e.target.tagName === 'FORM' || e.target.querySelector?.('form')) {
        attachSubmitListeners(e.target);
    }
    if (e.target.classList?.contains('messagebox') || e.target.querySelector?.('.messagebox')) {
        attachMessageboxPrimaryButtonListeners(e.target);
    }
}, true);

function attachSubmitListeners(container) {
    const forms = container.querySelectorAll('form');
    forms.forEach(form => {
        const submitBtn = form.querySelector('button[type="submit"]');
        if (!submitBtn) return;

        form.addEventListener('submit', () => {
            window.LoadingOverlay.show();
        });
    });
}

