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
                            window.Notification.success(msg.text);
                            break;
                        case 40: // ERROR
                            window.Notification.error(msg.text);
                            break;
                        case 30: // WARNING
                            window.Notification.warning(msg.text);
                            break;
                        case 20: // INFO
                        case 10: // DEBUG
                        default:
                            window.Notification.info(msg.text);
                    }
                });
            }
        } catch (e) {
            console.error('Error parsing Django messages:', e);
        }
    }
});
