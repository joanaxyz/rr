// Floor Plan Management System with Drag and Drop

class FloorPlanManager {
    constructor() {
        this.selectedItem = null;
        this.selectedType = null;
        this.draggedElement = null;
        this.dragOffset = { x: 0, y: 0 };
        this.snapGrid = 20;
        this.floorPlan = document.getElementById('floor-plan');
        this.tables = JSON.parse(this.floorPlan.dataset.tables || '[]');
        this.restaurant_id = this.floorPlan.dataset.restaurant_id;
        this.floorElements = JSON.parse(this.floorPlan.dataset.elements || '[]');
        this.nextTableNumber = Math.max(0, ...this.tables.map(t => t.number)) + 1;
        this.canvasWidth = 900;
        this.canvasHeight = 600;
        console.log(this.tables);
        console.log(this.floorElements);
        this.init();
    }

    init() {
        this.loadFloorplanDimensions();
        this.setupEventListeners();
        this.render();
    }

    loadFloorplanDimensions() {
        const data = JSON.parse(this.floorPlan.dataset.floorplan);
        console.log(data.width);
        this.canvasWidth = data.width || 900;
        this.canvasHeight = data.height || 600;
        document.getElementById('canvas-width').value = this.canvasWidth;
        document.getElementById('canvas-height').value = this.canvasHeight;
        this.applyCanvasDimensions();
    }

    applyCanvasDimensions() {
        this.floorPlan.style.width = this.canvasWidth + 'px';
        this.floorPlan.style.height = this.canvasHeight + 'px';
        this.floorPlan.style.minWidth = this.canvasWidth + 'px';
        this.floorPlan.style.minHeight = this.canvasHeight + 'px';
        
        const container = this.floorPlan.closest('.floor-plan-container');
        if (container) {
            container.style.height = (this.canvasHeight + 16) + 'px';
            container.style.maxHeight = (this.canvasHeight + 16) + 'px';
            container.style.minHeight = (this.canvasHeight + 16) + 'px';
        }
    }

    setupEventListeners() {
        // Buttons
        document.getElementById('add-table-btn').addEventListener('click', (e) => this.submitAddTable(e));
        const addElementBtn = document.getElementById('add-element-btn');
        if (addElementBtn) {
            addElementBtn.addEventListener('click', () => this.openAddElementModal());
        }

        document.getElementById('save-layout-btn').addEventListener('click', () => this.saveLayout());
        document.getElementById('reset-btn').addEventListener('click', () => this.resetLayout());
        document.getElementById('snap-grid').addEventListener('change', (e) => {
            this.snapGrid = e.target.checked ? 20 : 1;
        });

        // Dimension controls
        const canvasWidthInput = document.getElementById('canvas-width');
        const canvasHeightInput = document.getElementById('canvas-height');
        const applyDimensionsBtn = document.getElementById('apply-dimensions-btn');
        
        if (canvasWidthInput) {
            canvasWidthInput.addEventListener('input', (e) => this.validateDimension(e, 500, 2000));
        }
        if (canvasHeightInput) {
            canvasHeightInput.addEventListener('input', (e) => this.validateDimension(e, 300, 1500));
        }
        if (applyDimensionsBtn) {
            applyDimensionsBtn.addEventListener('click', () => this.updateCanvasDimensions());
        }

        // Element Modal
        const elementCloseBtn = document.querySelector('.element-modal-close-btn');
        const elementCancelBtn = document.querySelector('.element-modal-cancel');
        const elementForm = document.getElementById('add-element-form');
        if (elementCloseBtn) elementCloseBtn.addEventListener('click', () => this.closeAddElementModal());
        if (elementCancelBtn) elementCancelBtn.addEventListener('click', () => this.closeAddElementModal());
        if (elementForm) elementForm.addEventListener('submit', (e) => this.submitAddElement(e));

        // Floor plan mouse tracking
        this.floorPlan.addEventListener('mousemove', (e) => this.updateMousePosition(e));
        this.floorPlan.addEventListener('mouseleave', () => {
            document.getElementById('cursor-pos').textContent = '0, 0';
        });

        // Tab filtering
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.filterElements(e.target.dataset.filter));
        });

        // Properties panel
        document.getElementById('prop-close-btn').addEventListener('click', () => this.deselectItem());
        document.getElementById('prop-delete-btn').addEventListener('click', () => this.deleteSelectedItem());

        // Drag and drop listeners
        this.setupElementListeners();

        // Size buttons (for tables)
        document.querySelectorAll('.size-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const capacity = e.currentTarget.dataset.capacity;
                this.addTableAtPosition(capacity);
            });
        });
    }

    updateMousePosition(e) {
        const rect = this.floorPlan.getBoundingClientRect();
        let x = (e.clientX - rect.left) / this.snapGrid * this.snapGrid;
        let y = (e.clientY - rect.top) / this.snapGrid * this.snapGrid;
        
        if (this.snapGrid > 1) {
            x = Math.round(x);
            y = Math.round(y);
        } else {
            x = Math.round(x * 100) / 100;
            y = Math.round(y * 100) / 100;
        }
        
        document.getElementById('cursor-pos').textContent = `${x}, ${y}`;
    }

    validateDimension(e, min, max) {
        let value = parseInt(e.target.value);
        
        if (isNaN(value) || value < min) {
            e.target.value = min;
        } else if (value > max) {
            e.target.value = max;
        }
    }

    updateCanvasDimensions() {
        const newWidth = parseInt(document.getElementById('canvas-width').value);
        const newHeight = parseInt(document.getElementById('canvas-height').value);

        if (isNaN(newWidth) || isNaN(newHeight) || newWidth < 500 || newHeight < 300) {
            window.MessageBox.showWarning('Please enter valid dimensions (Width: 500-2000px, Height: 300-1500px)');
            return;
        }

        this.canvasWidth = newWidth;
        this.canvasHeight = newHeight;
        this.applyCanvasDimensions();
        this.showNotification('Canvas dimensions updated!', 'success');
    }

    setupElementListeners() {
        this.floorPlan.addEventListener('dragover', (e) => this.dragOver(e));
        this.floorPlan.addEventListener('drop', (e) => this.drop(e));
        this.floorPlan.addEventListener('click', (e) => this.handleFloorItemClick(e));
    }

    handleFloorItemClick(e) {
        const item = e.target.closest('[data-id][data-type]');
        if (item) {
            e.stopPropagation();
            this.selectItem(item.dataset.id, item.dataset.type);
        }
    }

    startDrag(e) {
        const target = e.currentTarget;

        this.draggedElement = target;
        const rect = target.getBoundingClientRect();

        // Calculate offset between mouse and element position
        this.dragOffset.x = e.clientX - rect.left;
        this.dragOffset.y = e.clientY - rect.top;

        // Apply visual feedback
        target.classList.add('dragging');
        this.floorPlan.classList.add('dragging-element');

        const itemId = target.dataset.id;
        const itemType = target.dataset.type;

        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('itemId', itemId);
        e.dataTransfer.setData('itemType', itemType);

        // Create custom drag image
        const dragImage = target.cloneNode(true);
        dragImage.style.opacity = '0.8';
        dragImage.style.position = 'absolute';
        dragImage.style.left = '-9999px';
        document.body.appendChild(dragImage);
        e.dataTransfer.setDragImage(dragImage, this.dragOffset.x, this.dragOffset.y);

        setTimeout(() => document.body.removeChild(dragImage), 0);
    }

    dragOver(e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
    }

    drop(e) {
        e.preventDefault();

        if (!this.draggedElement) return;

        const itemId = e.dataTransfer.getData('itemId');
        const itemType = e.dataTransfer.getData('itemType');

        const collection = itemType === 'table' ? this.tables : this.floorElements;
        const item = collection.find(el => String(el.id) === itemId);

        if (item) {
            const rect = this.floorPlan.getBoundingClientRect();
            let x = (e.clientX - rect.left) - this.dragOffset.x;
            let y = (e.clientY - rect.top) - this.dragOffset.y;

            // Snap to grid if enabled
            if (this.snapGrid > 1) {
                x = Math.round(x / this.snapGrid) * this.snapGrid;
                y = Math.round(y / this.snapGrid) * this.snapGrid;
            }

            // Get element dimensions for boundary checking
            const draggedRect = this.draggedElement.getBoundingClientRect();
            const elementWidth = draggedRect.width;
            const elementHeight = draggedRect.height;

            // Keep items within bounds with proper padding
            x = Math.max(0, Math.min(x, this.canvasWidth - elementWidth));
            y = Math.max(0, Math.min(y, this.canvasHeight - elementHeight));

            item.x = Math.round(x * 100) / 100;
            item.y = Math.round(y * 100) / 100;

            this.render();
            this.selectItem(itemId, itemType);
        }
    }

    dragEnd(e) {
        if (this.draggedElement) {
            this.draggedElement.classList.remove('dragging');
        }
        this.draggedElement = null;
        this.floorPlan.classList.remove('dragging-element');
        this.dragOffset = { x: 0, y: 0 };
    }

    addTableAtPosition(capacity, x = null, y = null) {
        const table = {
            id: Date.now(),
            number: this.nextTableNumber++,
            capacity: parseInt(capacity),
            x: x !== null ? Math.round(x * 100) / 100 : 100,
            y: y !== null ? Math.round(y * 100) / 100 : 100,
            new: true
        };

        this.tables.push(table);
        this.render();
        this.updateItemsList();
    }

    submitAddTable(e) {
        e.preventDefault();

        // Determine capacity based on table count to show progression
        const defaultCapacities = [2, 4, 6, 8];
        const capacity = defaultCapacities[(this.tables.length % defaultCapacities.length)];

        // Position tables in a grid
        const col = this.tables.length % 5;
        const row = Math.floor(this.tables.length / 5);
        const x = 120 + (col * 100);
        const y = 100 + (row * 150);

        const table = {
            id: Date.now(),
            number: this.nextTableNumber++,
            capacity: capacity,
            x,
            y,
            new: true
        };

        this.tables.push(table);
        this.render();
        this.updateItemsList();
    }

    openAddElementModal() {
        const modal = document.getElementById('add-element-modal');
        if (modal) {
            modal.style.display = 'flex';
            document.getElementById('element-name')?.focus();
        }
    }



    closeAddElementModal() {
        const modal = document.getElementById('add-element-modal');
        if (modal) {
            modal.style.display = 'none';
            document.getElementById('add-element-form')?.reset();
        }
    }

    submitAddElement(e) {
        e.preventDefault();

        const name = document.getElementById('element-name').value.trim();
        if (!name) {
            window.MessageBox.showWarning('Please enter an element name');
            return;
        }

        const width = parseFloat(document.getElementById('element-width').value) || 100;
        const height = parseFloat(document.getElementById('element-height').value) || 100;

        const x = 300;
        const y = 250;

        const element = {
            id: Date.now(),
            name,
            width: Math.round(width * 100) / 100,
            height: Math.round(height * 100) / 100,
            x,
            y,
            new: true
        };

        this.floorElements.push(element);
        this.render();
        this.updateItemsList();
        this.closeAddElementModal();
    }

    selectItem(itemId, itemType) {
        // Deselect previous
        if (this.selectedItem) {
            const prevElement = this.floorPlan.querySelector(`[data-id="${this.selectedItem.id}"]`);
            if (prevElement) prevElement.classList.remove('selected');
        }

        const collection = itemType === 'table' ? this.tables : this.floorElements;
        this.selectedItem = collection.find(el => String(el.id) === itemId);
        this.selectedType = itemType;

        if (this.selectedItem) {
            const element = this.floorPlan.querySelector(`[data-id="${itemId}"]`);
            if (element) element.classList.add('selected');

            // Update properties panel
            this.updatePropertiesPanel();
        }
    }

    deselectItem() {
        if (this.selectedItem) {
            const element = this.floorPlan.querySelector(`[data-id="${this.selectedItem.id}"]`);
            if (element) element.classList.remove('selected');
        }
        this.selectedItem = null;
        this.selectedType = null;
        this.updatePropertiesPanel();
    }

    deleteSelectedItem() {
        if (!this.selectedItem) return;
        const name = this.selectedItem.name ? this.selectedItem.name : "Table " + this.selectedItem.number;
        window.MessageBox.showConfirm(`Are you sure you want to delete "${name}"?`,()=>{
            if (this.selectedType === 'table') {
                this.tables = this.tables.filter(el => el.id !== this.selectedItem.id);
                this.renumberTables();
            } else {
                this.floorElements = this.floorElements.filter(el => el.id !== this.selectedItem.id);
            }
            this.selectedItem = null;
            this.selectedType = null;
            this.render();
            this.updatePropertiesPanel();
            this.updateItemsList();
        });
    }

    renumberTables() {
        this.tables.sort((a, b) => a.number - b.number);
        this.tables.forEach((table, index) => {
            table.number = index + 1;
        });
        this.nextTableNumber = this.tables.length + 1;
    }

    updatePropertiesPanel() {
        const form = document.getElementById('properties-form');
        const noSelection = document.getElementById('no-selection');

        if (!this.selectedItem) {
            form.style.display = 'none';
            noSelection.style.display = 'block';
            return;
        }

        form.style.display = 'block';
        noSelection.style.display = 'none';

        const nameGroup = document.getElementById('name-group');
        const capacityGroup = document.getElementById('capacity-group');
        const widthGroup = document.getElementById('width-group');
        const heightGroup = document.getElementById('height-group');

        document.getElementById('prop-x').value = this.selectedItem.x;
        document.getElementById('prop-y').value = this.selectedItem.y;

        // Handle table-specific properties
        if (this.selectedType === 'table') {
            nameGroup.style.display = 'block';
            document.getElementById('prop-name').value = this.selectedItem.number;
            document.getElementById('prop-name').onchange = (e) => {
                this.selectedItem.number = e.target.value;
                this.render();
                this.updateItemsList();
            };

            capacityGroup.style.display = 'block';
            if (widthGroup) widthGroup.style.display = 'none';
            if (heightGroup) heightGroup.style.display = 'none';
            document.getElementById('prop-capacity').value = this.selectedItem.capacity;

            document.getElementById('prop-capacity').onchange = (e) => {
                this.selectedItem.capacity = parseInt(e.target.value);
                this.render();
            };
        } else {
            nameGroup.style.display = 'block';
            document.getElementById('prop-name').value = this.selectedItem.name;
            document.getElementById('prop-name').onchange = (e) => {
                this.selectedItem.name = e.target.value;
                this.render();
                this.updateItemsList();
            };

            capacityGroup.style.display = 'none';
            if (widthGroup) widthGroup.style.display = 'block';
            if (heightGroup) heightGroup.style.display = 'block';

            document.getElementById('prop-width').value = this.selectedItem.width;
            document.getElementById('prop-height').value = this.selectedItem.height;

            document.getElementById('prop-width').onchange = (e) => {
                const value = parseFloat(e.target.value);
                this.selectedItem.width = isNaN(value) ? this.selectedItem.width : Math.round(value * 100) / 100;
                this.render();
            };

            document.getElementById('prop-height').onchange = (e) => {
                const value = parseFloat(e.target.value);
                this.selectedItem.height = isNaN(value) ? this.selectedItem.height : Math.round(value * 100) / 100;
                this.render();
            };
        }

        document.getElementById('prop-x').onchange = (e) => {
            const value = parseFloat(e.target.value);
            this.selectedItem.x = isNaN(value) ? this.selectedItem.x : Math.round(value * 100) / 100;
            this.render();
        };

        document.getElementById('prop-y').onchange = (e) => {
            const value = parseFloat(e.target.value);
            this.selectedItem.y = isNaN(value) ? this.selectedItem.y : Math.round(value * 100) / 100;
            this.render();
        };
    }

    render() {
        this.floorPlan.innerHTML = '';

        this.tables.forEach(table => {
            const div = FloorPlanUtils.createTableDiv(table);
            this.floorPlan.appendChild(div);

            div.addEventListener('dragstart', (e) => this.startDrag(e));
            div.addEventListener('dragend', (e) => this.dragEnd(e));
        });

        this.floorElements.forEach(element => {
            const div = FloorPlanUtils.createFloorElementDiv(element);
            this.floorPlan.appendChild(div);

            div.addEventListener('dragstart', (e) => this.startDrag(e));
            div.addEventListener('dragend', (e) => this.dragEnd(e));
        });
    }

    updateItemsList() {
        const list = document.getElementById('elements-list');
        const activeTab = document.querySelector('.tab-btn.active').dataset.filter;

        list.innerHTML = '';

        let itemsToDisplay = [];
        if (activeTab === 'table') {
            itemsToDisplay = this.tables.map(t => ({ ...t, _type: 'table' }));
        } else if (activeTab === 'element') {
            itemsToDisplay = this.floorElements.map(e => ({ ...e, _type: 'element' }));
        } else { // 'all'
            itemsToDisplay = [
                ...this.tables.map(t => ({ ...t, _type: 'table' })),
                ...this.floorElements.map(e => ({ ...e, _type: 'element' }))
            ];
        }

        if (itemsToDisplay.length === 0) {
            list.innerHTML = '<p style="text-align: center; color: var(--text-secondary); padding: 2rem;">No items to display</p>';
            return;
        }

        itemsToDisplay.forEach(item => {
            const card = document.createElement('div');
            card.className = 'element-card';
            if (this.selectedItem?.id === item.id) {
                card.classList.add('selected');
            }

            let cardContent = '';
            if (item._type === 'table') {
                cardContent = `
                    <div class="element-card-header">
                        <span class="element-card-name">${item.number}</span>
                        <span class="element-card-type">Table</span>
                    </div>
                    <div class="element-card-info">Capacity: ${item.capacity} persons</div>
                    <div class="element-card-info">Position: ${item.x}px, ${item.y}px</div>
                `;
            } else {
                cardContent = `
                    <div class="element-card-header">
                        <span class="element-card-name">${item.name}</span>
                        <span class="element-card-type">Rectangle</span>
                    </div>
                    <div class="element-card-info">Size: ${item.width}px × ${item.height}px</div>
                    <div class="element-card-info">Position: ${item.x}px, ${item.y}px</div>
                `;
            }

            card.innerHTML = `
                ${cardContent}
                <div class="element-card-actions">
                    <button class="btn-edit" data-id="${item.id}">Select</button>
                </div>
            `;

            card.querySelector('.btn-edit').addEventListener('click', () => {
                this.selectItem(item.id, item._type);
                this.updateItemsList();
            });

            list.appendChild(card);
        });
    }

    filterElements(filter) {
        // Update active tab
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-filter="${filter}"]`).classList.add('active');

        this.updateItemsList();
    }

    async saveLayout() {
        try {
            const response = await APIClient.post('/manage-restaurant/api/save_floor_plan/',
                {
                    restaurant_id: this.restaurant_id,
                    tables: this.tables,
                    elements: this.floorElements,
                    floorplan: {
                        width: this.canvasWidth,
                        height: this.canvasHeight
                    }
                },
                {
                    loadingText: 'Saving layout...'
                }
            );

            if (response.success) {
                this.showNotification('Layout saved successfully!', 'success');
            } else {
                this.showNotification(`Something went wrong ${response.message}`, 'error');
            }
        } catch (error) {
            console.log(error);
        }
    }


    initializeDefaultLayout() {
        this.tables = [];
        this.floorElements = [];
    }

    resetLayout() {
        if (confirm('Are you sure you want to reset the layout to default?')) {
            this.tables = [];
            this.floorElements = [];
            this.selectedItem = null;
            this.selectedType = null;
            this.initializeDefaultLayout();
            this.render();
            this.updateItemsList();
            this.updatePropertiesPanel();
        }
    }

    showNotification(message, type = 'info') {
        if (window.MessageBox) {
            switch (type) {
                case 'success':
                    window.MessageBox.showSuccess(message);
                    break;
                case 'error':
                    window.MessageBox.showError(message);
                    break;
                case 'warning':
                    window.MessageBox.showWarning(message);
                    break;
                default:
                    window.MessageBox.showInfo(message);
            }
        }
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    window.floorPlanManager = new FloorPlanManager();
});