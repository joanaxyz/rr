class MessageBox {
    constructor() {
        this.overlay = document.querySelector('.messagebox-overlay');
        this.container = document.querySelector('.messagebox');
        this.title = document.getElementById('msgbx_title');
        this.body = document.getElementById('msgbx_body');
        this.btn = document.getElementById('msgbx_btn');
        this.btn_primary = document.getElementById('msgbx_btn_primary');
        this.inputContainer = null;
        this.input = null;
        this.currentThemeMode = null;
        this.setThemeMode('light');
        this.initEnter();
        this.initBtnOnCLick();
        this.createInputContainer();
    }

    initBtnOnCLick() {
        this.btn.onclick = () => {
            this.hide();
        };
    }

    createInputContainer() {
        // Create input container element
        this.inputContainer = document.createElement('div');
        this.inputContainer.className = 'msgbx-input-container';
        this.inputContainer.style.display = 'none';
        
        // Create input element
        this.input = document.createElement('input');
        this.input.type = 'text';
        this.input.className = 'msgbx-input';
        this.input.placeholder = 'Enter value...';
        
        this.inputContainer.appendChild(this.input);
        
        // Insert after body element
        this.body.parentNode.insertBefore(this.inputContainer, this.body.nextSibling);
    }

    initEnter() {
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && this.overlay.classList.contains('show')) {
                e.preventDefault();
                this.btn_primary.click();
            }
        });
    }

    setTitle(title) {
        this.title.textContent = title;
    }

    setBody(body) {
        this.body.textContent = body;
    }

    setBtn(text) {
        this.btn.textContent = text;
    }

    setBtnPrimary(text) {
        this.btn_primary.textContent = text;
    }

    show() {
        this.overlay.classList.add('show');
    }

    hide() {
        this.overlay.classList.remove('show');
        // Clear input when hiding
        if (this.input) {
            this.input.value = '';
        }
    }

    setTheme(theme) {
        this.container.classList.remove('theme-error', 'theme-warning', 'theme-success', 'theme-info');

        if (theme) {
            this.container.classList.add(`theme-${theme}`);
        }
    }

    // Set light or dark mode
    setThemeMode(mode) {
        this.currentThemeMode = mode;
        if (mode === 'light') {
            this.container.classList.add('light');
        } else {
            this.container.classList.remove('light');
        }
    }

    // Get current theme mode
    getThemeMode() {
        return this.currentThemeMode;
    }

    showInput(visible) {
        if (this.inputContainer) {
            this.inputContainer.style.display = visible ? 'block' : 'none';
        }
    }

    setInputPlaceholder(placeholder) {
        if (this.input) {
            this.input.placeholder = placeholder;
        }
    }

    setInputValue(value) {
        if (this.input) {
            this.input.value = value;
        }
    }

    getInputValue() {
        return this.input ? this.input.value.trim() : '';
    }

    focusInput() {
        if (this.input) {
            setTimeout(() => this.input.focus(), 100);
        }
    }

    showError(message, callback) {
        this.showInput(false);
        this.setTheme('error');
        this.setTitle('Error');
        this.setBody(message);
        this.setBtnPrimary('Close');
        this.btn.style.display = 'none';
        this.show();
        this.btn_primary.onclick = () => {
            this.hide();
            if (callback) callback();
        };
    }

    showWarning(message, callback) {
        this.showInput(false);
        this.setTheme('warning');
        this.setTitle('Warning');
        this.setBody(message);
        this.setBtnPrimary('OK');
        this.btn.style.display = 'none';
        this.show();
        this.btn_primary.onclick = () => {
            this.hide();
            if (callback) callback();
        };
    }

    showSuccess(message, callback) {
        this.showInput(false);
        this.setTheme('success');
        this.setTitle('Success');
        this.setBody(message);
        this.setBtnPrimary('OK');
        this.btn.style.display = 'none';
        this.show();
        this.btn_primary.onclick = () => {
            this.hide();
            if (callback) callback();
        };
    }

    showInfo(message, callback) {
        this.showInput(false);
        this.setTheme('info');
        this.setTitle('Info');
        this.setBody(message);
        this.setBtnPrimary('OK');
        this.btn.style.display = 'none';
        this.show();
        this.btn_primary.onclick = () => {
            this.hide();
            if (callback) callback();
        };
    }

    showConfirm(message, callback) {
        this.showInput(false);
        this.setTheme(null);
        this.setTitle(null);
        this.setBody(message);
        this.setBtn('Cancel');
        this.setBtnPrimary('Confirm');
        this.btn.style.display = 'inline-block';
        this.show();
        this.btn_primary.onclick = () => {
            this.hide();
            if (callback) callback();
            window.LoadingOverlay.show();
        };
        this.btn.onclick = () => {
            this.hide();
        };
    }

    showPrompt(message, options = {}) {
        const {
            title = 'Input Required',
            placeholder = 'Enter value...',
            defaultValue = '',
            validator = null
        } = options;

        return new Promise((resolve, reject) => {
            this.setTheme('info');
            this.setTitle(title);
            this.setBody(message);
            this.setBtn('Close');
            this.setBtnPrimary('OK');
            this.btn.style.display = 'inline-block';
            this.showInput(true);
            this.setInputPlaceholder(placeholder);
            this.setInputValue(defaultValue);
            this.show();
            this.focusInput();

            this.btn_primary.onclick = () => {
                const value = this.getInputValue();
                
                if (validator) {
                    const validationResult = validator(value);
                    if (validationResult !== true) {

                        this.input.classList.add('error');
                        const errorMsg = typeof validationResult === 'string' ? validationResult : 'Invalid input';
                        
                        this.input.placeholder = errorMsg;
                        this.input.value = '';
                        return;
                    }
                }
                
                this.hide();
                resolve(value);
                window.LoadingOverlay.show();
            };

            this.btn.onclick = () => {
                this.hide();
                reject(new Error('User cancelled'));
            };

            this.input.oninput = () => {
                this.input.classList.remove('error');
            };
        });
    }
}

window.MessageBox = new MessageBox();