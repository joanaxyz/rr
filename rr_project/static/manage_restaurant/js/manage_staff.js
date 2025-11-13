// Open/Close Invite Modal
const inviteModal = document.getElementById('inviteModal');
const form = document.querySelector('#inviteModal form');

document.getElementById('inviteStaffBtn').addEventListener('click', () => {
    inviteModal.style.display = 'flex';
});
document.getElementById('closeInviteModal').addEventListener('click', () => {
    inviteModal.style.display = 'none';
});

// Send Invite
document.getElementById('sendInviteBtn').addEventListener('click', () => {
    const email = document.getElementById('inviteEmail').value;
    if (!email) {
        alert('Please enter an email');
        return;
    }
    inviteModal.style.display = 'none';
    document.getElementById('inviteEmail').value = '';
    form.submit();
});

// Update hidden action input based on selected role
document.getElementById('inviteRole').addEventListener('change', (event) => {
    const selectedRole = event.target.value;
    const actionInput = inviteModal.querySelector('input[name="action"]');
    actionInput.value = selectedRole;
});

