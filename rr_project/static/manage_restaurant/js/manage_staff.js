// Open/Close Invite Modal
const inviteModal = document.getElementById('inviteModal');
document.getElementById('inviteStaffBtn').addEventListener('click', () => {
    inviteModal.style.display = 'flex';
});
document.getElementById('closeInviteModal').addEventListener('click', () => {
    inviteModal.style.display = 'none';
});

// Send Invite
document.getElementById('sendInviteBtn').addEventListener('click', () => {
    const email = document.getElementById('inviteEmail').value;
    const role = document.getElementById('inviteRole').value;
    if (!email) {
        alert('Please enter an email');
        return;
    }
    alert(`Invite sent to ${email} as ${role}`);
    inviteModal.style.display = 'none';
    document.getElementById('inviteEmail').value = '';
});
