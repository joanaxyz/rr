// ===== Invite Modal =====
document.addEventListener('DOMContentLoaded', () => {
    const inviteStaffBtn = document.getElementById('inviteStaffBtn');
    let inviteModalInstance = null;

    if (inviteStaffBtn) {
        inviteStaffBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();

            // Get CSRF token from the page
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
            
            const modalContent = `
                <form method="post" id="inviteStaffForm">
                    <input type="hidden" name="modalOpened">
                    <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
                    <div style="display: flex; flex-direction: column; gap: 1rem;">
                        <div>
                            <label for="inviteEmail" style="display: block; margin-bottom: 0.5rem; font-weight: 600;">Staff Email</label>
                            <input type="email" name="email" id="inviteEmail" placeholder="Enter staff email" required 
                                style="width: 100%; padding: 0.75rem; border: 1px solid var(--gray-300); border-radius: 0.5rem; font-size: 1rem;">
                        </div>
                        <div>
                            <label for="inviteRole" style="display: block; margin-bottom: 0.5rem; font-weight: 600;">Role</label>
                            <select id="inviteRole" name="role" required
                                style="width: 100%; padding: 0.75rem; border: 1px solid var(--gray-300); border-radius: 0.5rem; font-size: 1rem;">
                                <option value="HOST">Host</option>
                                <option value="MANAGER">Manager</option>
                            </select>
                        </div>
                        <div style="margin-top: 1rem;">
                            <button type="submit" class="btn btn-primary" style="width: 100%;">Send Invite</button>
                        </div>
                    </div>
                </form>
            `;

            inviteModalInstance = window.Modal.show({
                title: 'Invite Staff',
                content: modalContent,
                maxWidth: '500px',
                showCloseButton: true,
                closeOnOverlayClick: true,
                onClose: () => {
                    inviteModalInstance = null;
                }
            });

            // Handle form submission
            const form = inviteModalInstance.getElement('#inviteStaffForm');
            if (form) {
                form.addEventListener('submit', (e) => {
                    e.preventDefault();
                    const email = inviteModalInstance.getElement('#inviteEmail')?.value;
                    
                    if (!email) {
                        if (window.Notification) {
                            window.Notification.warning('Please enter an email');
                        }
                        return;
                    }
                    
                    inviteModalInstance.close();
                    form.submit();
                });
            }
        });
    }
});

// ===== Remove Staff =====
function removeStaff(staff_name, staff_id, role){
    window.Modal.confirm(`Are you sure you want to delete, ${staff_name} (${formatRole(role)})?`, async ()=>{
        try {
            const response = await APIClient.post(`/rr-manage/api/remove_staff/${staff_id}/${role.toUpperCase()}/`,
                { loadingText: 'Deleting Staff from records...' }
            );

            if (response.success) {
                window.Notification.success(response.message);
                // Reload page to reflect changes
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                window.Notification.error(`Something went wrong ${response.message}`);
            }
        } catch (error) {
            console.error('Error removing staff:', error);
            window.Notification.error('An error occurred while removing staff member');
        }
    });
}

function formatRole(str) {
    return str.charAt(0) + str.slice(1).toLowerCase();
}

// ===== Staff Filters =====
document.addEventListener('DOMContentLoaded', () => {
    const filterName = document.getElementById('filterName');
    const filterEmail = document.getElementById('filterEmail');
    const filterRole = document.getElementById('filterRole');
    const resetStaffFilters = document.getElementById('resetStaffFilters');
    const staffRows = document.querySelectorAll('.staff-table tbody tr');

    if (!filterName || !filterEmail || !filterRole || !resetStaffFilters) {
        // Filters not available, skip initialization
        return;
    }

    const applyStaffFilters = () => {
        const nameVal = (filterName.value || '').toLowerCase();
        const emailVal = (filterEmail.value || '').toLowerCase();
        const roleVal = (filterRole.value || '').toLowerCase();

        staffRows.forEach(row => {
            if (row.cells.length < 4) return; // Ensure row has enough cells
            
            const name = (row.cells[1]?.textContent || '').toLowerCase();
            const email = (row.cells[2]?.textContent || '').toLowerCase();
            const role = (row.cells[3]?.textContent || '').toLowerCase();

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
});
