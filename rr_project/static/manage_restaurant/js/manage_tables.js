// Floor Plan Management System with Drag and Drop

class FloorPlanManager {
    constructor() {
        this.tables = [];
        this.floorElements = [];
        this.selectedItem = null;
        this.selectedType = null; // 'table' or 'element'
        this.draggedElement = null;
        this.dragOffset = { x: 0, y: 0 };
        this.snapGrid = 20;
        this.nextTableId = 1;
        this.elementTypeCounts = {}; // Track count per element type
        this.floorPlan = document.getElementById('floor-plan');
        this.zoom = 1;
        this.minZoom = 0.5;
        this.maxZoom = 3;
        this.zoomStep = 0.1;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadLayout();
        this.render();
    }

    setupEventListeners() {
        // Buttons
        document.getElementById('add-table-btn').addEventListener('click', () => this.openAddTableModal());
        const addElementBtn = document.getElementById('add-element-btn');
        if (addElementBtn) {
            addElementBtn.addEventListener('click', () => this.openAddElementModal());
        }
        
        document.getElementById('save-layout-btn').addEventListener('click', () => this.saveLayout());
        document.getElementById('reset-btn').addEventListener('click', () => this.resetLayout());
        document.getElementById('snap-grid').addEventListener('change', (e) => {
            this.snapGrid = e.target.checked ? 20 : 1;
        });

        // Zoom controls
        const zoomInBtn = document.getElementById('zoom-in-btn');
        const zoomOutBtn = document.getElementById('zoom-out-btn');
        const zoomResetBtn = document.getElementById('zoom-reset-btn');
        if (zoomInBtn) zoomInBtn.addEventListener('click', () => this.zoomIn());
        if (zoomOutBtn) zoomOutBtn.addEventListener('click', () => this.zoomOut());
        if (zoomResetBtn) zoomResetBtn.addEventListener('click', () => this.resetZoom());

        // Mouse wheel zoom
        this.floorPlan.addEventListener('wheel', (e) => this.handleMouseWheel(e), { passive: false });

        // Table Modal
        document.querySelector('.modal-close-btn').addEventListener('click', () => this.closeAddTableModal());
        document.querySelector('.modal-cancel').addEventListener('click', () => this.closeAddTableModal());
        document.getElementById('add-table-form').addEventListener('submit', (e) => this.submitAddTable(e));

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

        // Floor element sidebar items
        document.querySelectorAll('.element-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const elementType = e.currentTarget.dataset.type;
                this.openAddElementModalWithType(elementType);
            });
        });
    }

    updateMousePosition(e) {
        const rect = this.floorPlan.getBoundingClientRect();
        const x = Math.round(((e.clientX - rect.left) / this.zoom) / this.snapGrid) * this.snapGrid;
        const y = Math.round(((e.clientY - rect.top) / this.zoom) / this.snapGrid) * this.snapGrid;
        document.getElementById('cursor-pos').textContent = `${x}, ${y}`;
    }

    setupElementListeners() {
        this.floorPlan.addEventListener('dragstart', (e) => this.startDrag(e));
        this.floorPlan.addEventListener('dragover', (e) => this.dragOver(e));
        this.floorPlan.addEventListener('drop', (e) => this.drop(e));
        this.floorPlan.addEventListener('dragend', (e) => this.dragEnd(e));
    }

    startDrag(e) {
        if (!e.target.classList.contains('floor-item')) return;
        
        this.draggedElement = e.target;
        const rect = e.target.getBoundingClientRect();
        const floorRect = this.floorPlan.getBoundingClientRect();
        
        // Calculate offset between mouse and element position
        this.dragOffset.x = e.clientX - rect.left;
        this.dragOffset.y = e.clientY - rect.top;
        
        // Apply visual feedback
        e.target.classList.add('dragging');
        this.floorPlan.classList.add('dragging-element');
        
        const itemId = e.target.dataset.id;
        const itemType = e.target.dataset.type;
        
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('itemId', itemId);
        e.dataTransfer.setData('itemType', itemType);
        
        // Create custom drag image
        const dragImage = e.target.cloneNode(true);
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
        const item = collection.find(el => el.id === itemId);
        
        if (item) {
            const rect = this.floorPlan.getBoundingClientRect();
            let x = (e.clientX - rect.left) / this.zoom - this.dragOffset.x;
            let y = (e.clientY - rect.top) / this.zoom - this.dragOffset.y;
            
            // Snap to grid
            x = Math.round(x / this.snapGrid) * this.snapGrid;
            y = Math.round(y / this.snapGrid) * this.snapGrid;
            
            // Get element dimensions for boundary checking
            const draggedRect = this.draggedElement.getBoundingClientRect();
            const elementWidth = draggedRect.width / this.zoom;
            const elementHeight = draggedRect.height / this.zoom;
            
            // Keep items within bounds with proper padding
            x = Math.max(0, Math.min(x, this.floorPlan.offsetWidth / this.zoom - elementWidth));
            y = Math.max(0, Math.min(y, this.floorPlan.offsetHeight / this.zoom - elementHeight));
            
            item.x = x;
            item.y = y;
            
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
            id: `table-${Date.now()}`,
            name: `Table ${this.nextTableId++}`,
            capacity: parseInt(capacity),
            x: x || 100,
            y: y || 100
        };
        
        this.tables.push(table);
        this.render();
        this.updateItemsList();
    }

    openAddTableModal() {
        document.getElementById('add-table-modal').style.display = 'flex';
        document.getElementById('table-name').focus();
    }

    closeAddTableModal() {
        document.getElementById('add-table-modal').style.display = 'none';
        document.getElementById('add-table-form').reset();
    }

    submitAddTable(e) {
        e.preventDefault();
        
        const name = document.getElementById('table-name').value.trim();
        
        if (!name) {
            alert('Please enter a table name');
            return;
        }
        
        // Determine capacity based on table count to show progression
        const defaultCapacities = [2, 4, 6, 8];
        const capacity = defaultCapacities[(this.tables.length % defaultCapacities.length)];
        
        // Position tables in a grid
        const col = this.tables.length % 5;
        const row = Math.floor(this.tables.length / 5);
        const x = 120 + (col * 100);
        const y = 100 + (row * 150);
        
        const table = {
            id: `table-${Date.now()}`,
            name,
            capacity: capacity,
            x,
            y
        };
        
        this.tables.push(table);
        this.render();
        this.updateItemsList();
        this.closeAddTableModal();
        this.showNotification(`Table "${name}" added successfully!`, 'success');
    }

    openAddElementModal() {
        const modal = document.getElementById('add-element-modal');
        if (modal) {
            modal.style.display = 'flex';
            document.getElementById('element-name')?.focus();
        }
    }

    openAddElementModalWithType(elementType) {
        const modal = document.getElementById('add-element-modal');
        if (modal) {
            document.getElementById('element-type').value = elementType;
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
        
        const elementType = document.getElementById('element-type').value;
        const width = parseInt(document.getElementById('element-width').value) || 80;
        const height = parseInt(document.getElementById('element-height').value) || 80;
        
        // Auto-generate name based on element type
        const name = this.getNextElementName(elementType);
        
        // Default position (center-right of canvas)
        const x = 300;
        const y = 250;
        
        const element = {
            id: `element-${Date.now()}`,
            name,
            elementType,
            width,
            height,
            x,
            y
        };
        
        this.floorElements.push(element);
        this.render();
        this.updateItemsList();
        this.closeAddElementModal();
        this.showNotification(`${name} added successfully!`, 'success');
    }
    
    getNextElementName(elementType) {
        // Count existing elements of this type
        const count = this.floorElements.filter(el => el.elementType === elementType).length + 1;
        const typeLabel = elementType.charAt(0).toUpperCase() + elementType.slice(1);
        return `${typeLabel} ${count}`;
    }

    selectItem(itemId, itemType) {
        // Deselect previous
        if (this.selectedItem) {
            const prevElement = this.floorPlan.querySelector(`[data-id="${this.selectedItem.id}"]`);
            if (prevElement) prevElement.classList.remove('selected');
        }
        
        const collection = itemType === 'table' ? this.tables : this.floorElements;
        this.selectedItem = collection.find(el => el.id === itemId);
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
        
        if (confirm(`Are you sure you want to delete "${this.selectedItem.name}"?`)) {
            if (this.selectedType === 'table') {
                this.tables = this.tables.filter(el => el.id !== this.selectedItem.id);
            } else {
                this.floorElements = this.floorElements.filter(el => el.id !== this.selectedItem.id);
            }
            this.selectedItem = null;
            this.selectedType = null;
            this.render();
            this.updatePropertiesPanel();
            this.updateItemsList();
        }
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
        const nameDisplayGroup = document.getElementById('name-display-group');
        const capacityGroup = document.getElementById('capacity-group');
        const sizeGroup = document.getElementById('size-group');
        const widthGroup = document.getElementById('width-group');
        const heightGroup = document.getElementById('height-group');
        
        document.getElementById('prop-x').value = this.selectedItem.x;
        document.getElementById('prop-y').value = this.selectedItem.y;
        
        // Handle table-specific properties
        if (this.selectedType === 'table') {
            // Show editable name for tables
            nameGroup.style.display = 'block';
            nameDisplayGroup.style.display = 'none';
            document.getElementById('prop-name').value = this.selectedItem.name;
            document.getElementById('prop-name').onchange = (e) => {
                this.selectedItem.name = e.target.value;
                this.render();
                this.updateItemsList();
            };
            
            capacityGroup.style.display = 'block';
            if (sizeGroup) sizeGroup.style.display = 'none';
            if (widthGroup) widthGroup.style.display = 'none';
            if (heightGroup) heightGroup.style.display = 'none';
            document.getElementById('prop-capacity').value = this.selectedItem.capacity;
            
            document.getElementById('prop-capacity').onchange = (e) => {
                this.selectedItem.capacity = parseInt(e.target.value);
                this.render();
            };
        } else {
            // Show read-only name display for floor elements
            nameGroup.style.display = 'none';
            nameDisplayGroup.style.display = 'block';
            document.getElementById('prop-name-display').textContent = this.selectedItem.name;
            
            capacityGroup.style.display = 'none';
            if (sizeGroup) sizeGroup.style.display = 'block';
            if (widthGroup) widthGroup.style.display = 'block';
            if (heightGroup) heightGroup.style.display = 'block';
            
            document.getElementById('prop-type').value = this.selectedItem.elementType;
            document.getElementById('prop-width').value = this.selectedItem.width;
            document.getElementById('prop-height').value = this.selectedItem.height;
            
            document.getElementById('prop-element-type').onchange = (e) => {
                this.selectedItem.elementType = e.target.value;
                this.render();
            };
            
            document.getElementById('prop-width').onchange = (e) => {
                this.selectedItem.width = parseInt(e.target.value);
                this.render();
            };
            
            document.getElementById('prop-height').onchange = (e) => {
                this.selectedItem.height = parseInt(e.target.value);
                this.render();
            };
        }
        
        // Update common position handlers
        document.getElementById('prop-x').onchange = (e) => {
            this.selectedItem.x = parseInt(e.target.value);
            this.render();
        };
        
        document.getElementById('prop-y').onchange = (e) => {
            this.selectedItem.y = parseInt(e.target.value);
            this.render();
        };
    }

    render() {
        this.floorPlan.innerHTML = '';
        
        // Render all tables
        this.tables.forEach(table => {
            const div = this.createTableDiv(table);
            this.floorPlan.appendChild(div);
            
            div.addEventListener('click', (e) => {
                e.stopPropagation();
                this.selectItem(table.id, 'table');
            });
        });
        
        // Render all floor elements
        this.floorElements.forEach(element => {
            const div = this.createFloorElementDiv(element);
            this.floorPlan.appendChild(div);
            
            div.addEventListener('click', (e) => {
                e.stopPropagation();
                this.selectItem(element.id, 'element');
            });
        });
    }

    createTableDiv(table) {
        const div = document.createElement('div');
        div.className = `floor-item table table-${table.capacity}`;
        
        // Generate SVG based on capacity
        const svgContent = this.getTableSVG(table.capacity);
        
        div.innerHTML = `
            <div class="floor-item-content">
                ${svgContent}
                <span class="floor-item-label">${table.name}</span>
            </div>
        `;
        
        div.style.left = table.x + 'px';
        div.style.top = table.y + 'px';
        div.dataset.id = table.id;
        div.dataset.type = 'table';
        div.draggable = true;
        
        return div;
    }

    getTableSVG(capacity) {
        const designs = {
            2: {
                width: 40,
                height: 60,
                rect: { x: 10, y: 20, w: 20, h: 20, r: 4 },
                seats: [
                    { cx: 15, cy: 15, r: 3 },
                    { cx: 25, cy: 15, r: 3 }
                ]
            },
            4: {
                width: 60,
                height: 80,
                rect: { x: 15, y: 25, w: 30, h: 30, r: 6 },
                seats: [
                    { cx: 20, cy: 15, r: 4 },
                    { cx: 40, cy: 15, r: 4 },
                    { cx: 20, cy: 65, r: 4 },
                    { cx: 40, cy: 65, r: 4 }
                ]
            },
            6: {
                width: 80,
                height: 100,
                rect: { x: 20, y: 30, w: 40, h: 40, r: 8 },
                seats: [
                    { cx: 25, cy: 15, r: 5 },
                    { cx: 55, cy: 15, r: 5 },
                    { cx: 15, cy: 50, r: 5 },
                    { cx: 65, cy: 50, r: 5 },
                    { cx: 25, cy: 85, r: 5 },
                    { cx: 55, cy: 85, r: 5 }
                ]
            },
            8: {
                width: 100,
                height: 120,
                rect: { x: 25, y: 35, w: 50, h: 50, r: 10 },
                seats: [
                    { cx: 30, cy: 15, r: 6 },
                    { cx: 50, cy: 15, r: 6 },
                    { cx: 70, cy: 15, r: 6 },
                    { cx: 15, cy: 40, r: 6 },
                    { cx: 85, cy: 40, r: 6 },
                    { cx: 15, cy: 80, r: 6 },
                    { cx: 85, cy: 80, r: 6 },
                    { cx: 50, cy: 105, r: 6 }
                ]
            }
        };

        const design = designs[capacity] || designs[2];
        const rect = design.rect;
        
        let svg = `<svg width="${design.width}" height="${design.height}" viewBox="0 0 ${design.width} ${design.height}">`;
        svg += `<rect x="${rect.x}" y="${rect.y}" width="${rect.w}" height="${rect.h}" rx="${rect.r}" fill="currentColor"/>`;
        
        design.seats.forEach(seat => {
            svg += `<circle cx="${seat.cx}" cy="${seat.cy}" r="${seat.r}" fill="currentColor"/>`;
        });
        
        svg += '</svg>';
        return svg;
    }

    createFloorElementDiv(element) {
        const div = document.createElement('div');
        div.className = `floor-item element ${element.elementType}`;
        
        // Create icon based on element type
        const iconSvg = this.getElementIcon(element.elementType);
        
        div.innerHTML = `
            <div class="floor-item-content">
                ${iconSvg}
                <span class="floor-item-label">${element.name}</span>
            </div>
        `;
        
        div.style.left = element.x + 'px';
        div.style.top = element.y + 'px';
        div.style.width = element.width + 'px';
        div.style.height = element.height + 'px';
        div.dataset.id = element.id;
        div.dataset.type = 'element';
        div.draggable = true;
        
        return div;
    }

    getElementIcon(elementType) {
        const icons = {
            'entrance': '<svg width="30" height="30" viewBox="0 0 30 30" fill="currentColor"><path d="M5,8h20v14H5z"/><path d="M14,14h2v8h-2z"/></svg>',
            'bar': '<svg width="30" height="30" viewBox="0 0 30 30" fill="currentColor"><rect x="8" y="6" width="14" height="18" rx="2"/><circle cx="15" cy="10" r="2"/></svg>',
            'kitchen': '<svg width="30" height="30" viewBox="0 0 30 30" fill="currentColor"><rect x="5" y="8" width="20" height="16" rx="2"/><rect x="8" y="12" width="4" height="4"/><rect x="14" y="12" width="4" height="4"/><rect x="20" y="12" width="4" height="4"/></svg>',
            'restroom': '<svg width="30" height="30" viewBox="0 0 30 30" fill="currentColor"><circle cx="15" cy="8" r="3"/><path d="M10,14h10v10H10z"/></svg>',
            'window': '<svg width="30" height="30" viewBox="0 0 30 30" fill="none" stroke="currentColor" stroke-width="2"><rect x="5" y="5" width="20" height="20" rx="3"/><line x1="15" y1="5" x2="15" y2="25"/><line x1="5" y1="15" x2="25" y2="15"/></svg>',
            'storage': '<svg width="30" height="30" viewBox="0 0 30 30" fill="currentColor"><rect x="5" y="8" width="20" height="16" rx="1"/><line x1="5" y1="12" x2="25" y2="12" stroke="currentColor" stroke-width="1.5"/><line x1="5" y1="16" x2="25" y2="16" stroke="currentColor" stroke-width="1.5"/><line x1="5" y1="20" x2="25" y2="20" stroke="currentColor" stroke-width="1.5"/></svg>',
            'decoration': '<svg width="30" height="30" viewBox="0 0 30 30" fill="currentColor"><path d="M15,5 L18,12 L25,12 L19,17 L21,24 L15,20 L9,24 L11,17 L5,12 L12,12 Z"/></svg>',
            'wall': '<svg width="30" height="30" viewBox="0 0 30 30" fill="none" stroke="currentColor" stroke-width="3"><rect x="2" y="8" width="26" height="14"/></svg>'
        };
        return icons[elementType] || icons['decoration'];
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
                        <span class="element-card-name">${item.name}</span>
                        <span class="element-card-type">Table</span>
                    </div>
                    <div class="element-card-info">Capacity: ${item.capacity} persons</div>
                    <div class="element-card-info">Position: ${item.x}px, ${item.y}px</div>
                `;
            } else {
                const typeLabel = item.elementType.charAt(0).toUpperCase() + item.elementType.slice(1);
                cardContent = `
                    <div class="element-card-header">
                        <span class="element-card-name">${item.name}</span>
                        <span class="element-card-type">${typeLabel}</span>
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

    saveLayout() {
        const layoutData = JSON.stringify({
            tables: this.tables,
            floorElements: this.floorElements
        });
        localStorage.setItem('floorPlanLayout', layoutData);
        
        // Show notification
        this.showNotification('Layout saved successfully!', 'success');
    }

    loadLayout() {
        const layoutData = localStorage.getItem('floorPlanLayout');
        if (layoutData) {
            try {
                const data = JSON.parse(layoutData);
                this.tables = data.tables || [];
                this.floorElements = data.floorElements || [];
                
                // Update nextTableId
                const tableIds = this.tables
                    .map(t => parseInt(t.name.match(/\d+/)?.[0] || 0));
                this.nextTableId = Math.max(...tableIds, 0) + 1;
                
                // Update nextElementId
                const elementIds = this.floorElements
                    .map(e => parseInt(e.name.match(/\d+/)?.[0] || 0));
                this.nextElementId = Math.max(...elementIds, 0) + 1;
            } catch (e) {
                console.error('Error loading layout:', e);
                this.initializeDefaultLayout();
            }
        } else {
            this.initializeDefaultLayout();
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
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            background: ${type === 'success' ? '#10b981' : '#3b82f6'};
            color: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            z-index: 2000;
            animation: slideIn 0.3s ease-out;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    zoomIn() {
        this.zoom = Math.min(this.zoom + this.zoomStep, this.maxZoom);
        this.applyZoom();
    }

    zoomOut() {
        this.zoom = Math.max(this.zoom - this.zoomStep, this.minZoom);
        this.applyZoom();
    }

    resetZoom() {
        this.zoom = 1;
        this.applyZoom();
    }

    handleMouseWheel(e) {
        if (e.ctrlKey || e.metaKey) {
            e.preventDefault();
            const direction = e.deltaY > 0 ? -1 : 1;
            this.zoom = Math.max(this.minZoom, Math.min(this.maxZoom, this.zoom + (direction * this.zoomStep)));
            this.applyZoom();
        }
    }

    applyZoom() {
        this.floorPlan.style.transform = `scale(${this.zoom})`;
        this.floorPlan.style.transformOrigin = 'top left';
        const zoomPercentage = document.getElementById('zoom-percentage');
        if (zoomPercentage) {
            zoomPercentage.textContent = `${Math.round(this.zoom * 100)}%`;
        }
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    window.floorPlanManager = new FloorPlanManager();
});