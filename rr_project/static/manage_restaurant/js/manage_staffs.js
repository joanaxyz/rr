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

function removeStaff(staff_name, staff_id, role){
    window.MessageBox.showConfirm(`Are you sure you want to delete, ${staff_name} (${formatRole (role)})?`, async ()=>{
        try {
            const response = await APIClient.post(`/manage-restaurant/api/remove_staff/${staff_id}/${role.toUpperCase()}/`,
                    options=
                    {
                        loadingText: 'Deleting Staff from records...'
                    }
                );

                if (response.success) {
                    window.MessageBox.showSuccess(response.message);
                } else {
                    window.MessageBox.showError(`Something went wrong ${response.message}`);
                }
            } catch (error) {
                console.log(error);
        }
    });
}

function formatRole(str) {
    return str.charAt(0) + str.slice(1).toLowerCase();
}

