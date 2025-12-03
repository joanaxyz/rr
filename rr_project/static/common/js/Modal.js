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
            this.modalContainer.style.position = 'fixed';
            this.modalContainer.style.top = '0';
            this.modalContainer.style.left = '0';
            this.modalContainer.style.width = '100%';
            this.modalContainer.style.height = '100%';
            this.modalContainer.style.pointerEvents = 'none';
            this.modalContainer.style.zIndex = '2147483647';
            document.body.appendChild(this.modalContainer);
        }
    }

    createOverlay() {
        const overlay = document.createElement('div');
        overlay.className = 'modal-overlay';
        // Ensure it's positioned correctly from the start
        overlay.style.position = 'fixed';
        overlay.style.top = '0';
        overlay.style.left = '0';
        overlay.style.right = '0';
        overlay.style.bottom = '0';
        overlay.style.display = 'flex';
        overlay.style.justifyContent = 'center';
        overlay.style.alignItems = 'center';
        overlay.style.background = 'rgba(0, 0, 0, 0.5)';
        overlay.style.zIndex = '2147483647';
        overlay.style.opacity = '0';
        overlay.style.visibility = 'hidden';
        overlay.style.pointerEvents = 'none';
        overlay.style.transition = 'opacity 0.3s ease, visibility 0.3s ease';
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

    alert(message, onClose = null) {
        return new Promise((resolve) => {
            if (this.activeModal) {
                this.closeModal(this.activeModal);
            }

            const overlay = this.createOverlay();
            const dialog = this.createDialog('Alert', `<p>${this.escapeHtml(message)}</p>`, 'alert');
            const footer = dialog.querySelector('.modal-footer');

            const okBtn = this.createButton('OK', 'modal-btn-primary', () => {
                this.closeModal(overlay);
                resolve(true);
                if (onClose) onClose();
            });

            footer.appendChild(okBtn);

            overlay.addEventListener('click', (e) => {
                if (e.target === overlay) {
                    this.closeModal(overlay);
                    resolve(true);
                }
            });

            this.keydownHandler = (e) => {
                if (e.key === 'Escape' && overlay.parentNode) {
                    this.closeModal(overlay);
                    resolve(true);
                } else if (e.key === 'Enter' && overlay.parentNode) {
                    this.closeModal(overlay);
                    resolve(true);
                    if (onClose) onClose();
                }
            };

            document.addEventListener('keydown', this.keydownHandler);

            overlay.appendChild(dialog);
            this.modalContainer.appendChild(overlay);
            this.activeModal = overlay;
            overlay.style.display = 'flex';
            overlay.style.opacity = '1';
            overlay.style.visibility = 'visible';
            overlay.style.pointerEvents = 'all';
            overlay.classList.add('show');
            okBtn.focus();
        });
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
            overlay.style.display = 'flex';
            overlay.style.opacity = '1';
            overlay.style.visibility = 'visible';
            overlay.style.pointerEvents = 'all';
            overlay.classList.add('show');
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
            overlay.style.display = 'flex';
            overlay.style.opacity = '1';
            overlay.style.visibility = 'visible';
            overlay.style.pointerEvents = 'all';
            overlay.classList.add('show');
            inputElement.focus();
        });
    }

    show(options = {}) {
        const {
            title = '',
            content = '',
            maxWidth = '500px',
            onClose = null,
            showCloseButton = true,
            closeOnOverlayClick = true
        } = options;

        if (this.activeModal) {
            this.closeModal(this.activeModal);
        }

        const overlay = this.createOverlay();
        const dialog = document.createElement('div');
        dialog.className = 'modal-dialog';
        dialog.style.maxWidth = maxWidth;
        
        let html = '';
        
            if (title || showCloseButton) {
                html += '<div class="modal-header" style="display: flex; justify-content: space-between; align-items: center; gap: 1rem;">';
                if (title) {
                    html += `<h2 class="modal-title" style="flex: 1; margin: 0;">${title}</h2>`;
                }
                if (showCloseButton) {
                    html += '<button type="button" class="modal-close-btn" style="background: none; border: none; font-size: 1.5rem; cursor: pointer; color: var(--gray-600); padding: 0.25rem; display: flex; align-items: center; justify-content: center; width: 32px; height: 32px; border-radius: 0.375rem; transition: all 0.2s ease;">&times;</button>';
                }
                html += '</div>';
            }
        
        html += `<div class="modal-body">${content}</div>`;
        
        dialog.innerHTML = html;

        const closeModalHandler = () => {
            this.closeModal(overlay);
            if (onClose) onClose();
        };

        // Handle close button click and hover
        const closeBtn = dialog.querySelector('.modal-close-btn');
        if (closeBtn) {
            closeBtn.addEventListener('click', closeModalHandler);
            closeBtn.addEventListener('mouseenter', () => {
                closeBtn.style.backgroundColor = 'var(--gray-100, #f3f4f6)';
                closeBtn.style.color = 'var(--gray-900, #111827)';
            });
            closeBtn.addEventListener('mouseleave', () => {
                closeBtn.style.backgroundColor = 'transparent';
                closeBtn.style.color = 'var(--gray-600, #4b5563)';
            });
        }

        // Handle overlay click
        if (closeOnOverlayClick) {
            overlay.addEventListener('click', (e) => {
                if (e.target === overlay) {
                    closeModalHandler();
                }
            });
        }

        // Prevent clicks inside dialog from closing modal
        dialog.addEventListener('click', (e) => {
            e.stopPropagation();
        });

        // Handle Escape key
        this.keydownHandler = (e) => {
            if (e.key === 'Escape' && overlay.parentNode && this.activeModal === overlay) {
                closeModalHandler();
            }
        };

        document.addEventListener('keydown', this.keydownHandler);

        overlay.appendChild(dialog);
        this.modalContainer.appendChild(overlay);
        this.activeModal = overlay;
        
        // Force display immediately
        overlay.style.display = 'flex';
        overlay.style.opacity = '1';
        overlay.style.visibility = 'visible';
        overlay.style.pointerEvents = 'all';
        overlay.classList.add('show');
        
        console.log('Modal created:', {
            overlay: overlay,
            container: this.modalContainer,
            hasShow: overlay.classList.contains('show'),
            styles: {
                display: overlay.style.display,
                opacity: overlay.style.opacity,
                visibility: overlay.style.visibility
            }
        });

        // Return an object with methods to interact with the modal
        return {
            overlay,
            dialog,
            close: closeModalHandler,
            getElement: (selector) => dialog.querySelector(selector),
            getElements: (selector) => dialog.querySelectorAll(selector)
        };
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
