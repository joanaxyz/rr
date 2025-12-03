// Restaurant Reservation System - Table Selection

document.addEventListener('DOMContentLoaded', function () {
    const floorPlan = document.querySelector('.floor-plan');
    if (floorPlan) {
        loadFloorplanDimensions(floorPlan);
        FloorPlanUtils.initializeFloorPlan(floorPlan);
        initializeTableSelection();
        initializeFloorPlanDrag();
    }
    
    // Initialize date and time validation with restaurant operating hours
    initializeDateTimeValidation();
});

function loadFloorplanDimensions(floorPlanElement) {
    const data = JSON.parse(floorPlanElement.dataset.floorplan);
    const width = data.width || 900;
    const height = data.height || 600;
    console.log(width);
    floorPlanElement.style.width = width + 'px';
    floorPlanElement.style.height = height + 'px';
    floorPlanElement.style.minWidth = width + 'px';
    floorPlanElement.style.minHeight = height + 'px';
    
    const container = floorPlanElement.parentElement;
    if (container) {
        // Set container to accommodate the floor plan with padding
        const containerHeight = height + 40; // 20px padding top and bottom
        container.style.minHeight = Math.max(containerHeight, 540) + 'px'; // At least 540px (500px + 40px padding)
        container.style.height = 'auto';
        container.style.maxHeight = 'none';
    }
}

// Table Selection System
function updateTableStates(tables, selectedTables, guestCount) {
    const totalSelectedCapacity = selectedTables.reduce((sum, t) => sum + t.capacity, 0);
    const remainingGuests = guestCount - totalSelectedCapacity;

    tables.forEach(table => {
        const tableCapacity = parseInt(table.dataset.capacity);
        const isSelected = table.classList.contains('selected');
        const isReserved = table.classList.contains('reserved');

        // Reset previous styles and classes
        table.style.filter = '';
        table.style.pointerEvents = ''; // enable by default
        table.classList.remove('deactivated');

        if (isReserved) {
            // Reserved tables stay red, but dimmed
            table.style.filter = 'brightness(0.6)';
            table.style.pointerEvents = 'none'; // cannot click reserved table
        } else if (isSelected) {
            // Selected tables stay blue, no filter needed
            table.style.filter = '';
        } else if (remainingGuests > 0) {
            if (tableCapacity <= remainingGuests + 1) {
                // Suitable table - keep normal appearance
                table.style.filter = '';
            } else {
                // Too large to be useful alone - make it greyish/deactivated
                table.classList.add('deactivated');
                table.style.pointerEvents = 'none';
            }
        } else {
            // No more guests needed - make it greyish/deactivated
            table.classList.add('deactivated');
            table.style.pointerEvents = 'none';
        }
    });
}

// Hook into click and guest count change
function initializeTableSelection() {
    const tables = document.querySelectorAll('.table');
    const selectedTableInput = document.getElementById('selected-table');
    const tableStatusElement = document.getElementById('table-status');
    const reserveBtn = document.getElementById('reserve-btn');
    const guestCountSelect = document.querySelector('[name="guest_count"]');
    const tableSelectionInfo = document.getElementById('selected-table-info');
    const tableNum = document.getElementById('table_num');

    let selectedTables = [];
    
    // Initialize with pre-selected tables if in edit mode
    if (window.editMode && window.selectedTableNumbers && window.selectedTableNumbers.length > 0) {
        tables.forEach(table => {
            const tableNumber = table.dataset.table;
            const tableCapacity = parseInt(table.dataset.capacity);
            if (window.selectedTableNumbers.includes(tableNumber)) {
                selectedTables.push({ element: table, number: tableNumber, capacity: tableCapacity });
                table.classList.add('selected');
            }
        });
    }

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

// Date and Time Validation with Restaurant Operating Hours
function initializeDateTimeValidation() {
    const dateInput = document.querySelector('input[name="date"]');
    const timeInput = document.querySelector('input[name="time"]');
    const reservationForm = document.getElementById('reservation-form');
    
    if (!dateInput || !timeInput || !reservationForm) {
        return;
    }
    
    // Get restaurant data from the page (if available)
    const restaurantData = getRestaurantData();
    
    // Set minimum date to today
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const todayStr = today.toISOString().split('T')[0];
    dateInput.setAttribute('min', todayStr);
    
    // Validate date and time on change
    function validateDateTime() {
        const selectedDate = new Date(dateInput.value);
        const selectedTime = timeInput.value;
        
        // Clear previous errors
        dateInput.setCustomValidity('');
        timeInput.setCustomValidity('');
        
        if (!dateInput.value) {
            return;
        }
        
        // Check if date is in the past
        if (selectedDate < today) {
            dateInput.setCustomValidity('Reservation date cannot be in the past. Please select today or a future date.');
            return;
        }
        
        // Check if date is too far in the future (1 year)
        const maxDate = new Date(today);
        maxDate.setFullYear(maxDate.getFullYear() + 1);
        if (selectedDate > maxDate) {
            dateInput.setCustomValidity('Reservations can only be made up to 1 year in advance.');
            return;
        }
        
        // Validate operating days if restaurant data is available
        if (restaurantData && restaurantData.operating_days) {
            const weekdayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
            // JavaScript getDay(): 0=Sunday, 1=Monday, ..., 6=Saturday
            // Convert to Mon=0, Tue=1, ..., Sun=6 format
            const jsDay = selectedDate.getDay();
            const dayIndex = jsDay === 0 ? 6 : jsDay - 1; // Sunday becomes 6, Monday becomes 0
            const selectedDay = weekdayNames[dayIndex];
            const operatingDays = restaurantData.operating_days.split(',').map(d => d.trim());
            
            if (!operatingDays.includes(selectedDay)) {
                const fullDayNames = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
                const fullDayName = fullDayNames[dayIndex];
                dateInput.setCustomValidity(
                    `The restaurant is closed on ${fullDayName}. ` +
                    `Please select a date when the restaurant is open. Operating days: ${restaurantData.operating_days}`
                );
                return;
            }
        }
        
        // If date is today, validate time
        if (selectedDate.toDateString() === today.toDateString() && selectedTime) {
            const [hours, minutes] = selectedTime.split(':').map(Number);
            const selectedDateTime = new Date(today);
            selectedDateTime.setHours(hours, minutes, 0, 0);
            
            const now = new Date();
            if (selectedDateTime < now) {
                timeInput.setCustomValidity('Reservation time cannot be in the past. Please select a future time.');
                return;
            }
        }
        
        // Validate operating hours if restaurant data is available
        if (restaurantData && selectedTime && restaurantData.opening_time && restaurantData.closing_time) {
            const [openingHours, openingMinutes] = restaurantData.opening_time.split(':').map(Number);
            const [closingHours, closingMinutes] = restaurantData.closing_time.split(':').map(Number);
            const [selectedHours, selectedMinutes] = selectedTime.split(':').map(Number);
            
            const openingTime = openingHours * 60 + openingMinutes; // Convert to minutes
            const closingTime = closingHours * 60 + closingMinutes;
            const selectedTimeMinutes = selectedHours * 60 + selectedMinutes;
            
            let isWithinHours = false;
            
            // Handle case where restaurant closes after midnight
            if (closingTime < openingTime) {
                // Restaurant closes after midnight (e.g., opens 18:00, closes 02:00)
                isWithinHours = selectedTimeMinutes >= openingTime || selectedTimeMinutes <= closingTime;
            } else {
                // Normal case: opens and closes on same day
                isWithinHours = selectedTimeMinutes >= openingTime && selectedTimeMinutes <= closingTime;
            }
            
            if (!isWithinHours) {
                const openingStr = formatTime(openingHours, openingMinutes);
                const closingStr = formatTime(closingHours, closingMinutes);
                timeInput.setCustomValidity(
                    `Reservation time must be within operating hours (${openingStr} - ${closingStr}). ` +
                    `Please select a time when the restaurant is open.`
                );
                return;
            }
        }
    }
    
    // Format time to 12-hour format
    function formatTime(hours, minutes) {
        const period = hours >= 12 ? 'PM' : 'AM';
        const displayHours = hours % 12 || 12;
        const displayMinutes = minutes.toString().padStart(2, '0');
        return `${displayHours}:${displayMinutes} ${period}`;
    }
    
    // Get restaurant data from the page
    function getRestaurantData() {
        // Try to get from a data attribute or script tag
        const restaurantScript = document.querySelector('script[data-restaurant]');
        if (restaurantScript) {
            try {
                return JSON.parse(restaurantScript.dataset.restaurant);
            } catch (e) {
                console.error('Error parsing restaurant data:', e);
            }
        }
        
        // Try to get from window object (if set by template)
        if (window.restaurantData) {
            return window.restaurantData;
        }
        
        return null;
    }
    
    // Validate on input change
    dateInput.addEventListener('change', validateDateTime);
    timeInput.addEventListener('change', validateDateTime);
    
    // Validate on form submit
    reservationForm.addEventListener('submit', function(e) {
        validateDateTime();
        
        if (!dateInput.validity.valid || !timeInput.validity.valid) {
            e.preventDefault();
            // Show validation messages
            if (!dateInput.validity.valid) {
                dateInput.reportValidity();
            } else if (!timeInput.validity.valid) {
                timeInput.reportValidity();
            }
            return false;
        }
    });
}

// Floor Plan Drag Functionality (removed expand feature)
function initializeFloorPlanDrag() {
    const floorPlanContainer = document.querySelector('.table-map-container > .floor-plan');
    
    if (!floorPlanContainer) {
        return;
    }
    let isDragging = false;
    let dragStartX = 0;
    let dragStartY = 0;
    let currentTranslateX = 0;
    let currentTranslateY = 0;

    // Get or create inner wrapper for dragging
    function getOrCreateWrapper() {
        let innerWrapper = floorPlanContainer.querySelector('.floor-plan-inner-wrapper');
        if (!innerWrapper) {
            // Only create wrapper if there's actual content (tables/elements)
            const hasContent = floorPlanContainer.querySelector('.table, .floor-item');
            if (!hasContent) {
                return null;
            }
            
            // Create wrapper
            innerWrapper = document.createElement('div');
            innerWrapper.className = 'floor-plan-inner-wrapper';
            innerWrapper.style.position = 'relative';
            
            // Get floor plan dimensions from the container's computed style
            const floorPlanWidth = floorPlanContainer.style.width || 
                                   window.getComputedStyle(floorPlanContainer).width || 
                                   '800px';
            const floorPlanHeight = floorPlanContainer.style.height || 
                                    window.getComputedStyle(floorPlanContainer).height || 
                                    '500px';
            
            innerWrapper.style.width = floorPlanWidth;
            innerWrapper.style.height = floorPlanHeight;
            innerWrapper.style.minWidth = floorPlanWidth;
            innerWrapper.style.minHeight = floorPlanHeight;
            
            // Copy background styles from container to wrapper
            const containerStyle = window.getComputedStyle(floorPlanContainer);
            innerWrapper.style.backgroundImage = containerStyle.backgroundImage;
            innerWrapper.style.backgroundSize = containerStyle.backgroundSize;
            innerWrapper.style.backgroundColor = containerStyle.backgroundColor;
            
            // Move all children to wrapper (tables, elements, etc.)
            // Use a snapshot to avoid issues with live NodeList
            const children = Array.from(floorPlanContainer.childNodes);
            children.forEach(child => {
                if (child.nodeType === Node.ELEMENT_NODE && 
                    !child.classList.contains('floor-plan-inner-wrapper') &&
                    (child.classList.contains('table') || 
                     child.classList.contains('floor-item') ||
                     child.classList.contains('entrance') ||
                     child.classList.contains('bar-area') ||
                     child.classList.contains('kitchen') ||
                     child.classList.contains('restroom') ||
                     child.classList.contains('window'))) {
                    innerWrapper.appendChild(child);
                }
            });
            
            // Only add wrapper if it has content
            if (innerWrapper.children.length > 0) {
                floorPlanContainer.appendChild(innerWrapper);
            } else {
                return null;
            }
        }
        return innerWrapper;
    }

    // Update floor plan position
    function updateFloorPlanPosition() {
        const innerWrapper = floorPlanContainer.querySelector('.floor-plan-inner-wrapper');
        if (innerWrapper) {
            innerWrapper.style.transform = `translate(${currentTranslateX}px, ${currentTranslateY}px)`;
        }
    }

    // Check if floor plan overflows container
    function checkOverflow() {
        const containerRect = floorPlanContainer.getBoundingClientRect();
        const innerWrapper = floorPlanContainer.querySelector('.floor-plan-inner-wrapper');
        
        if (!innerWrapper) {
            // If no wrapper, check if content would overflow
            const computedStyle = window.getComputedStyle(floorPlanContainer);
            const contentWidth = parseInt(floorPlanContainer.style.width) || 
                               parseInt(floorPlanContainer.dataset.width) || 
                               800;
            const contentHeight = parseInt(floorPlanContainer.style.height) || 
                                 parseInt(floorPlanContainer.dataset.height) || 
                                 500;
            
            // Account for padding (30px on each side = 60px total)
            const padding = 60;
            const availableWidth = containerRect.width - padding;
            const availableHeight = containerRect.height - padding;
            
            return contentWidth > availableWidth || contentHeight > availableHeight;
        }
        
        const contentRect = innerWrapper.getBoundingClientRect();
        const padding = 60;
        const availableWidth = containerRect.width - padding;
        const availableHeight = containerRect.height - padding;
        
        return contentRect.width > availableWidth || contentRect.height > availableHeight;
    }

    // Update cursor based on overflow
    function updateCursor() {
        const hasOverflow = checkOverflow();
        if (hasOverflow) {
            floorPlanContainer.style.cursor = isDragging ? 'grabbing' : 'grab';
        } else {
            floorPlanContainer.style.cursor = 'default';
        }
    }
    
    // Initialize wrapper and cursor on load - wait for content to be rendered
    setTimeout(() => {
        // Wait for floor plan to be fully initialized
        const hasContent = floorPlanContainer.querySelector('.table, .floor-item');
        if (hasContent && checkOverflow()) {
            getOrCreateWrapper();
            updateCursor();
        }
    }, 1000);

    // Handle mouse down for dragging
    function handleMouseDown(e) {
        // Don't start drag if clicking on a table or floor item
        if (e.target.closest('.table, .floor-item')) {
            return;
        }

        const hasOverflow = checkOverflow();
        if (!hasOverflow) {
            updateCursor();
            return;
        }

        isDragging = true;
        floorPlanContainer.classList.add('dragging');
        floorPlanContainer.style.cursor = 'grabbing';
        
        dragStartX = e.clientX - currentTranslateX;
        dragStartY = e.clientY - currentTranslateY;
        
        e.preventDefault();
    }

    // Handle mouse move for dragging
    function handleMouseMove(e) {
        if (!isDragging) return;

        const hasOverflow = checkOverflow();
        if (!hasOverflow) {
            isDragging = false;
            floorPlanContainer.classList.remove('dragging');
            return;
        }

        currentTranslateX = e.clientX - dragStartX;
        currentTranslateY = e.clientY - dragStartY;

        // Constrain dragging to prevent dragging too far
        const containerRect = floorPlanContainer.getBoundingClientRect();
        const innerWrapper = floorPlanContainer.querySelector('.floor-plan-inner-wrapper');
        const padding = 60;
        const availableWidth = containerRect.width - padding;
        const availableHeight = containerRect.height - padding;
        
        let contentWidth, contentHeight;
        if (innerWrapper) {
            const contentRect = innerWrapper.getBoundingClientRect();
            contentWidth = contentRect.width;
            contentHeight = contentRect.height;
        } else {
            contentWidth = parseInt(floorPlanContainer.style.width) || 
                          parseInt(floorPlanContainer.dataset.width) || 
                          800;
            contentHeight = parseInt(floorPlanContainer.style.height) || 
                           parseInt(floorPlanContainer.dataset.height) || 
                           500;
        }
        
        const maxX = Math.max(0, (contentWidth - availableWidth) / 2);
        const maxY = Math.max(0, (contentHeight - availableHeight) / 2);
        
        currentTranslateX = Math.max(-maxX, Math.min(maxX, currentTranslateX));
        currentTranslateY = Math.max(-maxY, Math.min(maxY, currentTranslateY));

        updateFloorPlanPosition();
        e.preventDefault();
    }

    // Handle mouse up
    function handleMouseUp(e) {
        if (isDragging) {
            isDragging = false;
            floorPlanContainer.classList.remove('dragging');
            updateCursor();
        }
    }

    // Handle touch events for mobile
    function handleTouchStart(e) {
        if (e.target.closest('.table, .floor-item')) {
            return;
        }

        const hasOverflow = checkOverflow();
        if (!hasOverflow) return;

        if (e.touches.length === 1) {
            isDragging = true;
            floorPlanContainer.classList.add('dragging');
            
            const touch = e.touches[0];
            dragStartX = touch.clientX - currentTranslateX;
            dragStartY = touch.clientY - currentTranslateY;
            
            e.preventDefault();
        }
    }

    function handleTouchMove(e) {
        if (!isDragging) return;

        const hasOverflow = checkOverflow();
        if (!hasOverflow) {
            isDragging = false;
            floorPlanContainer.classList.remove('dragging');
            return;
        }

        if (e.touches.length === 1) {
            const touch = e.touches[0];
            currentTranslateX = touch.clientX - dragStartX;
            currentTranslateY = touch.clientY - dragStartY;

            // Constrain dragging
            const containerRect = floorPlanContainer.getBoundingClientRect();
            const innerWrapper = floorPlanContainer.querySelector('.floor-plan-inner-wrapper');
            const padding = isExpanded ? 40 : 60;
            const availableWidth = containerRect.width - padding;
            const availableHeight = containerRect.height - padding;
            
            let contentWidth, contentHeight;
            if (innerWrapper) {
                const contentRect = innerWrapper.getBoundingClientRect();
                contentWidth = contentRect.width;
                contentHeight = contentRect.height;
            } else {
                contentWidth = parseInt(floorPlanContainer.style.width) || 
                              parseInt(floorPlanContainer.dataset.width) || 
                              800;
                contentHeight = parseInt(floorPlanContainer.style.height) || 
                               parseInt(floorPlanContainer.dataset.height) || 
                               500;
            }
            
            const maxX = Math.max(0, (contentWidth - availableWidth) / 2);
            const maxY = Math.max(0, (contentHeight - availableHeight) / 2);
            
            currentTranslateX = Math.max(-maxX, Math.min(maxX, currentTranslateX));
            currentTranslateY = Math.max(-maxY, Math.min(maxY, currentTranslateY));

            updateFloorPlanPosition();
            e.preventDefault();
        }
    }

    function handleTouchEnd(e) {
        if (isDragging) {
            isDragging = false;
            floorPlanContainer.classList.remove('dragging');
            updateCursor();
        }
    }

    // Mouse events for dragging
    floorPlanContainer.addEventListener('mousedown', handleMouseDown);
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);

    // Touch events for mobile dragging
    floorPlanContainer.addEventListener('touchstart', handleTouchStart, { passive: false });
    document.addEventListener('touchmove', handleTouchMove, { passive: false });
    document.addEventListener('touchend', handleTouchEnd);
    document.addEventListener('touchcancel', handleTouchEnd);

    // Prevent default scroll/wheel behavior
    floorPlanContainer.addEventListener('wheel', function(e) {
        const hasOverflow = checkOverflow();
        if (hasOverflow) {
            e.preventDefault();
        }
    }, { passive: false });

    // Update cursor on window resize
    window.addEventListener('resize', function() {
        updateCursor();
    });
}