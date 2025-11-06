// Restaurant Reservation System - Table Selection

document.addEventListener('DOMContentLoaded', function () {
    initializeTableSelection();
});

// Table Selection System
function updateTableStates(tables, selectedTables, guestCount) {
    const totalSelectedCapacity = selectedTables.reduce((sum, t) => sum + t.capacity, 0);
    const remainingGuests = guestCount - totalSelectedCapacity;

    tables.forEach(table => {
        const tableCapacity = parseInt(table.dataset.capacity);
        const isSelected = table.classList.contains('selected');
        const isReserved = table.classList.contains('reserved');

        // Reset previous styles
        table.style.filter = '';
        table.style.pointerEvents = ''; // enable by default

        if (isReserved) {
            table.style.filter = 'brightness(0.5)';
            table.style.pointerEvents = 'none'; // cannot click reserved table
        } else if (isSelected) {
            table.style.filter = 'brightness(1.2)'; // highlight selected
        } else if (remainingGuests > 0) {
            if (tableCapacity <= remainingGuests + 1) {
                table.style.filter = 'brightness(1.1)'; // suitable
            } else {
                table.style.filter = 'brightness(0.7)'; // too large to be useful alone
                table.style.pointerEvents = 'none';
            }
        } else {
            table.style.filter = 'brightness(0.7)'; // no more guests needed
            table.style.pointerEvents = 'none';
        }
    });
}

// Hook into click and guest count change
function initializeTableSelection() {
    const tables = document.querySelectorAll('.table.available');
    const selectedTableInput = document.getElementById('selected-table');
    const tableStatusElement = document.getElementById('table-status');
    const reserveBtn = document.getElementById('reserve-btn');
    const guestCountSelect = document.querySelector('[name="guest_count"]');
    const tableSelectionInfo = document.getElementById('selected-table-info');
    const tableNum = document.getElementById('table_num');

    let selectedTables = [];

    function refreshUI() {
        const totalCapacity = selectedTables.reduce((sum, t) => sum + t.capacity, 0);
        const tableCount = selectedTables.length;
        const guestCount = guestCountSelect ? parseInt(guestCountSelect.value) : 0;

        // Update input
        if (selectedTableInput) selectedTableInput.value = selectedTables.map(t => t.number).join(',');
        if (tableNum){
            tableNum.value = selectedTables.map(t => t.number).join(',');
            console.log("table numbers", tableNum.value);
        }
        // Update table status
        if (tableStatusElement) {
            if (tableCount > 0) {
                tableStatusElement.innerHTML = `${tableCount} table${tableCount > 1 ? 's' : ''} selected (${totalCapacity} seats)`;
            } else {
                tableStatusElement.innerHTML = 'No tables selected';
            }
        }

        // Update table info
        if (tableSelectionInfo) {
            if (tableCount > 0) {
                const tableList = selectedTables.map(t => `Table ${t.number} (${t.capacity} seats)`).join(', ');
                tableSelectionInfo.innerHTML = `<p style="color: var(--table-selected); font-weight: 600;">✓ Selected: ${tableList}<br>Total capacity: ${totalCapacity} guests</p>`;
            } else {
                tableSelectionInfo.innerHTML = `<p style="color: #666;">Click on tables to select them</p>`;
            }
        }

        // Enable/disable reserve button
        if (reserveBtn) {
            reserveBtn.disabled = tableCount === 0 || totalCapacity < guestCount;
            reserveBtn.style.opacity = reserveBtn.disabled ? '0.5' : '1';
        }

        // Update table highlighting
        if (guestCountSelect) updateTableStates(tables, selectedTables, guestCount);
    }

    tables.forEach(table => {
        table.addEventListener('click', function () {
            const tableNumber = this.dataset.table;
            const tableCapacity = parseInt(this.dataset.capacity);
            const tableIndex = selectedTables.findIndex(t => t.element === this);

            if (tableIndex > -1) {
                selectedTables.splice(tableIndex, 1);
                this.classList.remove('selected');
            } else {
                selectedTables.push({ element: this, number: tableNumber, capacity: tableCapacity });
                this.classList.add('selected');
            }

            refreshUI();
        });

        table.addEventListener('mouseenter', function () {
            if (tableSelectionInfo && !this.classList.contains('reserved')) {
                const isSelected = this.classList.contains('selected');
                tableSelectionInfo.dataset.originalContent = tableSelectionInfo.innerHTML;
                tableSelectionInfo.innerHTML = `<p style="color: var(--table-hover); font-weight: 600;">Table ${this.dataset.table} - Capacity: ${this.dataset.capacity} guests (Click to ${isSelected ? 'deselect' : 'select'})</p>`;
            }
        });

        table.addEventListener('mouseleave', function () {
            if (tableSelectionInfo && tableSelectionInfo.dataset.originalContent) {
                setTimeout(() => {
                    tableSelectionInfo.innerHTML = tableSelectionInfo.dataset.originalContent;
                }, 100);
            }
        });
    });

    if (guestCountSelect) {
        guestCountSelect.addEventListener('change', refreshUI);
    }

    // Initial UI refresh
    refreshUI();
}