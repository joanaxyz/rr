// ===== Invite Modal =====
const inviteModal = document.getElementById('inviteModal');
const form = document.querySelector('#inviteModal form');

document.getElementById('inviteStaffBtn').addEventListener('click', () => {
    inviteModal.style.display = 'flex';
});
document.getElementById('closeInviteModal').addEventListener('click', () => {
    inviteModal.style.display = 'none';
});

document.getElementById('sendInviteBtn').addEventListener('click', () => {
    const email = document.getElementById('inviteEmail').value;

    if (!email) {
        window.MessageBox.showWarning('Please enter an email');
        return;
    }
    inviteModal.style.display = 'none';
    form.submit();
});

// ===== Remove Staff =====
function removeStaff(staff_name, staff_id, role){
    window.MessageBox.showConfirm(`Are you sure you want to delete, ${staff_name} (${formatRole (role)})?`, async ()=>{
        try {
            const response = await APIClient.post(`/manage-restaurant/api/remove_staff/${staff_id}/${role.toUpperCase()}/`,
                options = { loadingText: 'Deleting Staff from records...' }
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

// ===== Staff Filters =====
const filterName = document.getElementById('filterName');
const filterEmail = document.getElementById('filterEmail');
const filterRole = document.getElementById('filterRole');
const resetStaffFilters = document.getElementById('resetStaffFilters');
const staffRows = document.querySelectorAll('.staff-table tbody tr');

const applyStaffFilters = () => {
    const nameVal = filterName.value.toLowerCase();
    const emailVal = filterEmail.value.toLowerCase();
    const roleVal = filterRole.value.toLowerCase();

    staffRows.forEach(row => {
        const name = row.cells[1].textContent.toLowerCase();
        const email = row.cells[2].textContent.toLowerCase();
        const role = row.cells[3].textContent.toLowerCase();

        if (
            (name.includes(nameVal)) &&
            (email.includes(emailVal)) &&
            (roleVal === "" || role.includes(roleVal))
        ) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
};

filterName.addEventListener('keyup', applyStaffFilters);
filterEmail.addEventListener('keyup', applyStaffFilters);
filterRole.addEventListener('change', applyStaffFilters);

resetStaffFilters.addEventListener('click', () => {
    filterName.value = '';
    filterEmail.value = '';
    filterRole.value = '';
    applyStaffFilters();
});
