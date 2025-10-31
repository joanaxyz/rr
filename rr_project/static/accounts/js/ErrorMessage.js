class ErrorMessage {
    constructor() {
        this.error_element = document.querySelector('.error-msg');
    }
    show(msg) {
        if (this.error_element) {
            this.error_element.classList.add('show');
            this.error_element.textContent = msg;
        }else{
            console.log("no error element");
        }
    }
    hide() {
        if (this.error_element) {
            this.error_element.classList.remove('show');
        }else{
             console.log("no error element");
        }
    }
}

window.ErrorMessage = new ErrorMessage();