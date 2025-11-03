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
    };

    const handleLogout = () => {
        window.MessageBox.showConfirm('Are you sure you want to logout?', () => {
            window.location.href='/accounts/auth/logout';
        });
    };

    const handleSettings = () => {
        window.location.href='/settings/';
    }

    setupEventListeners();
});
