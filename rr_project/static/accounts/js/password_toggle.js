document.addEventListener('DOMContentLoaded', () => {
    const wrappers = document.querySelectorAll('.password-wrapper');

    wrappers.forEach(wrapper => {
        const input = wrapper.querySelector('input[type="password"], input[data-password-field]');
        const toggle = wrapper.querySelector('.toggle-password');
        if (!input || !toggle) return;

        const stopBlur = (e) => e.preventDefault();
        toggle.addEventListener('pointerdown', stopBlur);
        toggle.addEventListener('mousedown', stopBlur);

        const updateToggleVisibility = () => {
            toggle.style.display = (document.activeElement === input && input.value.trim() !== '') 
                ? 'inline' 
                : 'none';
        };

        input.addEventListener('input', updateToggleVisibility);
        input.addEventListener('focus', updateToggleVisibility);
        input.addEventListener('blur', () => {
            toggle.style.display = 'none';
            input.type = 'password';
            toggle.classList.remove('fa-eye-slash');
            toggle.classList.add('fa-eye');
        });

        toggle.addEventListener('click', () => {
            const start = input.selectionStart;
            const end = input.selectionEnd;
            input.type = input.type === 'password' ? 'text' : 'password';
            toggle.classList.toggle('fa-eye');
            toggle.classList.toggle('fa-eye-slash');
            setTimeout(() => input.setSelectionRange(start, end), 0);
        });
    });
});
