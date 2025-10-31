document.addEventListener('DOMContentLoaded', function() {
    const messagesElement = document.getElementById('djangoMessages');
    if (messagesElement) {
        try {
            const messages = JSON.parse(messagesElement.textContent);
            if (messages && messages.length > 0) {
                messages.forEach(msg => {
                    // Django message levels are numeric constants
                    // DEBUG = 10, INFO = 20, SUCCESS = 25, WARNING = 30, ERROR = 40
                    switch (msg.level) {
                        case 25: // SUCCESS
                            window.MessageBox.showSuccess(msg.text);
                            break;
                        case 40: // ERROR
                            window.MessageBox.showError(msg.text);
                            break;
                        case 30: // WARNING
                            window.MessageBox.showWarning(msg.text);
                            break;
                        case 20: // INFO
                        case 10: // DEBUG
                        default:
                            window.MessageBox.showInfo(msg.text);
                    }
                });
            }
        } catch (e) {
            console.error('Error parsing Django messages:', e);
        }
    }
});
