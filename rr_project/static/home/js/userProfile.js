document.addEventListener('DOMContentLoaded', () => {
    const elements = {
        userProfile: document.getElementById('userProfile'),
        dropdown: document.getElementById('profileDropdown'),
        logoutBtn: document.getElementById('btnLogout'),
        settings: document.getElementById('btnSettings'),
    };

    const setupEventListeners = () => {

        elements.userProfile.addEventListener('click', (e) => {
            e.stopPropagation();
            elements.dropdown.classList.toggle('show');
        });

        document.addEventListener('click', (e) => {
            if (!elements.dropdown.contains(e.target) && 
                !elements.userProfile.contains(e.target)) {
                elements.dropdown.classList.remove('show');
            }
        });

        elements.dropdown.addEventListener('click', (e) => e.stopPropagation());

        elements.logoutBtn.addEventListener('click', handleLogout);
        elements.settings.addEventListener('click', handleSettings);
        
        // Handle My Profile link
        const profileLink = elements.dropdown.querySelector('a[href*="profile"]');
        if (profileLink) {
            profileLink.addEventListener('click', function(e) {
                // Let the link navigate naturally
                elements.dropdown.classList.remove('show');
            });
        }
    };

    const handleLogout = () => {
        window.MessageBox.showConfirm('Are you sure you want to logout?', () => {
            window.location.href = window.logoutUrl || '/accounts/auth/logout/';
        });
    };

    const handleSettings = () => {
        window.location.href='/settings/';
    }

    setupEventListeners();
});
