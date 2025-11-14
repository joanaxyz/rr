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
        window.MessageBox.showWarning('Please enter an email');
        return;
    }
    inviteModal.style.display = 'none';
    form.submit();
});

