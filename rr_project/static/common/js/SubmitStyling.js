document.addEventListener('DOMContentLoaded',()=>{
    const form = document.querySelector('form');
    const submitBtn = document.querySelector('button[type="submit"]');

    if (!form || !submitBtn) return;

    form.addEventListener('submit', ()=>{
        submitBtn.disabled = true;
       
        submitBtn.style.opacity = '0.6';
        submitBtn.style.cursor = 'not-allowed';
        
        submitBtn.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" class="animate-spin">
                <path d="M12,4V2A10,10 0 0,0 2,12H4A8,8 0 0,1 12,4Z"/>
            </svg>
            Processing...
        `;

        // Add loading animation
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