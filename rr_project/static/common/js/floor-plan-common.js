/* Shared Floor Plan Utilities */

window.FloorPlanUtils = window.FloorPlanUtils || {};

FloorPlanUtils.getTableSVG = function(capacity) {
    const designs = {
        2: {
            width: 45,
            height: 55,
            rect: { x: 12, y: 18, w: 21, h: 19, r: 4 },
            seats: [
                { cx: 22, cy: 10, r: 3 },
                { cx: 22, cy: 45, r: 3 }  
            ]
        },
        4: {
            width: 55,
            height: 65,
            rect: { x: 14, y: 22, w: 27, h: 21, r: 5 },
            seats: [
                { cx: 19, cy: 15, r: 3 },
                { cx: 36, cy: 15, r: 3 },
                { cx: 19, cy: 52, r: 3 },
                { cx: 36, cy: 52, r: 3 }
            ]
        },
        6: {
            width: 65,
            height: 75,
            rect: { x: 16, y: 26, w: 33, h: 23, r: 6 },
            seats: [
                { cx: 21, cy: 21, r: 3 },
                { cx: 44, cy: 21, r: 3 },
                { cx: 12, cy: 42, r: 3 },
                { cx: 53, cy: 42, r: 3 },
                { cx: 21, cy: 56, r: 3 },
                { cx: 44, cy: 56, r: 3 }
            ]
        },
        8: {
            width: 75,
            height: 85,
            rect: { x: 18, y: 30, w: 39, h: 25, r: 7 },
            seats: [
                { cx: 21, cy: 22, r: 3 },
                { cx: 37, cy: 22, r: 3 },
                { cx: 53, cy: 22, r: 3 },
                { cx: 10, cy: 42, r: 3 },
                { cx: 65, cy: 42, r: 3 },
                { cx: 21, cy: 63, r: 3 },
                { cx: 37, cy: 63, r: 3 },
                { cx: 53, cy: 63, r: 3 }
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
};

FloorPlanUtils.createTableDiv = function(table) {
    const div = document.createElement('div');
    const status = table.status || 'available';
    console.log('status', status);
    div.className = `floor-item table table-${table.capacity} ${status.toLowerCase()}`;
    
    const svgContent = FloorPlanUtils.getTableSVG(table.capacity);
    div.innerHTML = `
        <div class="floor-item-content">
            ${svgContent}
            <span class="floor-item-label">${table.number}</span>
        </div>
    `;
    
    div.style.left = table.x + 'px';
    div.style.top = table.y + 'px';
    div.dataset.id = table.id;
    div.dataset.type = 'table';
    div.dataset.table = table.number;
    div.dataset.capacity = table.capacity;
    div.draggable = true;
    
    return div;
};

FloorPlanUtils.createFloorElementDiv = function(element) {
    const div = document.createElement('div');
    div.className = 'floor-item element';
    
    div.innerHTML = `
        <div class="floor-item-content">
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
};

FloorPlanUtils.initializeFloorPlan = function(floorPlanElement) {
    const tables = JSON.parse(floorPlanElement.dataset.tables || '[]');
    const floorElements = JSON.parse(floorPlanElement.dataset.elements || '[]');
    
    floorPlanElement.innerHTML = '';
    
    tables.forEach(table => {
        console.log('Processing table:', table);
        const div = FloorPlanUtils.createTableDiv(table);
        floorPlanElement.appendChild(div);
    });
    
    floorElements.forEach(element => {
        const div = FloorPlanUtils.createFloorElementDiv(element);
        floorPlanElement.appendChild(div);
    });
};
