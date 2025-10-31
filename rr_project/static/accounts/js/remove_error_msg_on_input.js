function removeErrorMsgOnInput(inputs) {
    inputs.forEach((field) => {
        field.addEventListener('input', () => {
            window.ErrorMessage.hide();
        });
    });
}

document.addEventListener("DOMContentLoaded", () => {
    const inputs = document.querySelectorAll('input');
    
    // Only call the function if there are inputs to avoid errors
    if (inputs.length > 0) {
        removeErrorMsgOnInput(inputs);
    }
});