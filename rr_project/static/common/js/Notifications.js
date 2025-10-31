class NotificationSystem {
    constructor() {
        this.notifications = [];
        this.maxNotifications = 4;
        this.defaultDuration = 5000; // 5 seconds
        this.initializeStyles();
    }

    initializeStyles() {
        // Check if notification styles are already loaded
        if (document.querySelector('#notification-styles')) {
            return;
        }

        // Create and append link to CSS file
        const link = document.createElement('link');
        link.id = 'notification-styles';
        link.rel = 'stylesheet';
        link.href = '/static/common/css/notifications.css';
        document.head.appendChild(link);
    }

    show(message, type = 'info', duration = null) {
        // Remove oldest notification if we've reached the limit
        if (this.notifications.length >= this.maxNotifications) {
            this.remove(this.notifications[0]);
        }

        // Remove existing notifications of the same message
        this.notifications.forEach(notification => {
            if (notification.message === message) {
                this.remove(notification);
            }
        });

        const notification = this.create(message, type);
        this.notifications.push({
            element: notification,
            message: message,
            type: type
        });

        // Auto remove after duration
        const timeoutDuration = duration || this.defaultDuration;
        setTimeout(() => {
            this.remove({ element: notification, message: message, type: type });
        }, timeoutDuration);

        return notification;
    }

    create(message, type) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <div class="notification-icon">
                    ${this.getIcon(type)}
                </div>
                <span class="notification-message">${message}</span>
                <button class="notification-close" aria-label="Close notification">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"/>
                    </svg>
                </button>
            </div>
        `;

        // Add close button functionality
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.addEventListener('click', () => {
            this.remove({ element: notification, message: message, type: type });
        });

        // Add to page
        document.body.appendChild(notification);

        return notification;
    }

    remove(notificationObj) {
        if (!notificationObj || !notificationObj.element) return;

        const notification = notificationObj.element;
        
        if (notification.parentElement) {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.remove();
                }
            }, 300);
        }

        // Remove from tracking array
        this.notifications = this.notifications.filter(n => n.element !== notification);
    }

    getIcon(type) {
        const icons = {
            success: '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M9,20.42L2.79,14.21L5.62,11.38L9,14.77L18.88,4.88L21.71,7.71L9,20.42Z"/></svg>',
            error: '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M13,13H11V7H13M13,17H11V15H13M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2Z"/></svg>',
            warning: '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M13,13H11V7H13M12,17.3A1.3,1.3 0 0,1 10.7,16A1.3,1.3 0 0,1 12,14.7A1.3,1.3 0 0,1 13.3,16A1.3,1.3 0 0,1 12,17.3M15.73,3H8.27L3,8.27V15.73L8.27,21H15.73L21,15.73V8.27L15.73,3Z"/></svg>',
            info: '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M13,9H11V7H13M13,17H11V11H13M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2Z"/></svg>'
        };
        return icons[type] || icons.info;
    }

    // Convenience methods
    success(message, duration = null) {
        return this.show(message, 'success', duration);
    }

    error(message, duration = null) {
        return this.show(message, 'error', duration);
    }

    warning(message, duration = null) {
        return this.show(message, 'warning', duration);
    }

    info(message, duration = null) {
        return this.show(message, 'info', duration);
    }

    // Clear all notifications
    clear() {
        this.notifications.forEach(notification => {
            this.remove(notification);
        });
        this.notifications = [];
    }
}

// Create global instance
window.Notifications = new NotificationSystem();


function showNotification(message, type = 'info', duration = null) {
    return window.Notifications.show(message, type, duration);
}