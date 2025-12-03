class Modal {
    constructor() {
        this.modalContainer = null;
        this.activeModal = null;
        this.keydownHandler = null;
        this.init();
    }

    init() {
        this.modalContainer = document.getElementById('modal-container');
        if (!this.modalContainer) {
            this.modalContainer = document.createElement('div');
            this.modalContainer.id = 'modal-container';
            document.body.appendChild(this.modalContainer);
        }
    }

    createOverlay() {
        const overlay = document.createElement('div');
        overlay.className = 'modal-overlay';
        return overlay;
    }

    createDialog(title, content, type = 'dialog') {
        const dialog = document.createElement('div');
        dialog.className = `modal-dialog modal-${type}`;
        
        let html = '';
        
        if (title) {
            html += `<div class="modal-header"><h2 class="modal-title">${this.escapeHtml(title)}</h2></div>`;
        }
        
        html += `<div class="modal-body">${content}</div>`;
        html += `<div class="modal-footer"></div>`;
        
        dialog.innerHTML = html;
        return dialog;
    }

    createButton(text, className = '', onClick = null) {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = `modal-btn ${className}`;
        button.textContent = text;
        if (onClick) {
            button.addEventListener('click', onClick);
        }
        return button;
    }

    confirm(message, onConfirm, onCancel = null) {
        return new Promise((resolve) => {
            if (this.activeModal) {
                this.closeModal(this.activeModal);
            }

            const overlay = this.createOverlay();
            const dialog = this.createDialog('Confirm', `<p>${this.escapeHtml(message)}</p>`, 'confirm');
            const footer = dialog.querySelector('.modal-footer');

            const cancelBtn = this.createButton('Cancel', 'modal-btn-secondary', () => {
                this.closeModal(overlay);
                resolve(false);
                if (onCancel) onCancel();
            });

            const confirmBtn = this.createButton('Confirm', 'modal-btn-primary', () => {
                this.closeModal(overlay);
                resolve(true);
                if (onConfirm) onConfirm();
            });

            footer.appendChild(cancelBtn);
            footer.appendChild(confirmBtn);

            overlay.addEventListener('click', (e) => {
                if (e.target === overlay) {
                    this.closeModal(overlay);
                    resolve(false);
                }
            });

            this.keydownHandler = (e) => {
                if (e.key === 'Escape' && overlay.parentNode) {
                    this.closeModal(overlay);
                    resolve(false);
                }
            };

            document.addEventListener('keydown', this.keydownHandler);

            overlay.appendChild(dialog);
            this.modalContainer.appendChild(overlay);
            this.activeModal = overlay;
            setTimeout(() => overlay.classList.add('show'), 10);
            confirmBtn.focus();
        });
    }

    prompt(message, options = {}) {
        const {
            title = 'Input Required',
            placeholder = 'Enter value...',
            defaultValue = '',
            validator = null
        } = options;

        return new Promise((resolve, reject) => {
            if (this.activeModal) {
                this.closeModal(this.activeModal);
            }

            const overlay = this.createOverlay();
            
            let inputHtml = `
                <div class="modal-prompt-form">
                    <p>${this.escapeHtml(message)}</p>
                    <div class="modal-input-group">
                        <input 
                            type="text" 
                            class="modal-input" 
                            placeholder="${this.escapeHtml(placeholder)}" 
                            value="${this.escapeHtml(defaultValue)}"
                        />
                        <div class="modal-input-error" style="display: none;"></div>
                    </div>
                </div>
            `;
            
            const dialog = this.createDialog(title, inputHtml, 'prompt');
            const footer = dialog.querySelector('.modal-footer');
            const inputElement = dialog.querySelector('.modal-input');
            const errorElement = dialog.querySelector('.modal-input-error');

            const handleCancel = () => {
                this.closeModal(overlay);
                reject(new Error('User cancelled'));
            };

            const handleConfirm = () => {
                const value = inputElement.value.trim();

                if (validator) {
                    const validationResult = validator(value);
                    if (validationResult !== true) {
                        const errorMsg = typeof validationResult === 'string' ? validationResult : 'Invalid input';
                        errorElement.textContent = errorMsg;
                        errorElement.style.display = 'block';
                        inputElement.classList.add('error');
                        inputElement.focus();
                        return;
                    }
                }

                this.closeModal(overlay);
                resolve(value);
            };

            const cancelBtn = this.createButton('Cancel', 'modal-btn-secondary', handleCancel);
            const confirmBtn = this.createButton('OK', 'modal-btn-primary', handleConfirm);

            inputElement.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    handleConfirm();
                } else if (e.key === 'Escape') {
                    handleCancel();
                }
            });

            inputElement.addEventListener('input', () => {
                inputElement.classList.remove('error');
                errorElement.style.display = 'none';
            });

            overlay.addEventListener('click', (e) => {
                if (e.target === overlay) {
                    handleCancel();
                }
            });

            this.keydownHandler = (e) => {
                if (e.key === 'Escape' && overlay.parentNode) {
                    handleCancel();
                }
            };

            document.addEventListener('keydown', this.keydownHandler);

            footer.appendChild(cancelBtn);
            footer.appendChild(confirmBtn);
            overlay.appendChild(dialog);
            this.modalContainer.appendChild(overlay);
            this.activeModal = overlay;
            setTimeout(() => overlay.classList.add('show'), 10);
            inputElement.focus();
        });
    }

    closeModal(overlay) {
        overlay.classList.remove('show');
        if (this.activeModal === overlay) {
            this.activeModal = null;
        }
        if (this.keydownHandler) {
            document.removeEventListener('keydown', this.keydownHandler);
            this.keydownHandler = null;
        }
        setTimeout(() => {
            if (overlay.parentNode) {
                overlay.parentNode.removeChild(overlay);
            }
        }, 300);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

window.Modal = new Modal();
