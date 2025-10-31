class LoadingOverlay{
    constructor(){
        this.overlay = document.getElementById('loadingOverlay');
        this.loadingText = document.getElementById('loadingText');
    }
    show(text='Loading...'){
        this.loadingText.textContent = text;
        this.overlay.classList.add('active');
    }
    hide(){
        this.overlay.classList.remove('active');
    }
}

window.LoadingOverlay = new LoadingOverlay();