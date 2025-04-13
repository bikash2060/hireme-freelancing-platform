document.addEventListener('DOMContentLoaded', function() {
    // Get the current language prefix from the URL
    const langPrefix = window.location.pathname.split('/')[1];
    const baseUrl = '/' + langPrefix;

    // Connect to WebSocket
    const notificationSocket = new WebSocket(
        'ws://' + window.location.host + '/ws/notifications/'
    );

    // Handle incoming notifications
    notificationSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        updateNotificationCount(data.unread_count);
        addNewNotification(data.notification);
        updateMarkAllReadButton(); // Update button state when new notification arrives
    };

    // Update notification count
    function updateNotificationCount(count) {
        const countElement = document.querySelector('.notification-count');
        if (countElement) {
            if (count > 0) {
                // For counts greater than 9, show "9+"
                if (count > 9) {
                    countElement.setAttribute('data-count', '9+');
                } else {
                    countElement.setAttribute('data-count', count.toString());
                }
                countElement.style.display = 'flex';
            } else {
                countElement.style.display = 'none';
            }
        }
        updateMarkAllReadButton(); // Update button state when count changes
    }

    // Add new notification to the list
    function addNewNotification(notification) {
        const notificationContent = document.querySelector('.notification-content');
        if (!notificationContent) return;

        const notificationItem = document.createElement('div');
        notificationItem.className = 'notification-item unread';
        notificationItem.setAttribute('data-notification-id', notification.id);
        
        // Add redirect URL if available
        if (notification.redirect_url) {
            notificationItem.setAttribute('data-redirect-url', notification.redirect_url);
        }

        // Format the date like "April 10, 2025 at 02:16 PM"
        const date = new Date(notification.created_at);
        const options = { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric', 
            hour: '2-digit', 
            minute: '2-digit',
            hour12: true 
        };
        const formattedDate = date.toLocaleDateString('en-US', options).replace(',', ' at');
        
        let iconClass = 'fas fa-bell';
        if (notification.notification_type === 'project') {
            iconClass = 'fas fa-briefcase';
        } else if (notification.notification_type === 'message') {
            iconClass = 'fas fa-envelope';
        }

        notificationItem.innerHTML = `
            <div class="notification-icon">
                <i class="fas fa-bell"></i>
            </div>
            <div class="notification-details">
                <p>${notification.message}</p>
                <small class="notification-time">${formattedDate}</small>
            </div>
        `;

        // Add click event to handle notification click
        notificationItem.addEventListener('click', function() {
            markNotificationAsRead(notification.id);
            // Redirect if URL is available
            if (notification.redirect_url) {
                window.location.href = notification.redirect_url;
            }
        });

        // Insert at the top of the list
        const firstItem = notificationContent.querySelector('.notification-item');
        if (firstItem) {
            notificationContent.insertBefore(notificationItem, firstItem);
        } else {
            notificationContent.appendChild(notificationItem);
        }

        // Remove "No notifications" message if it exists
        const noNotifications = notificationContent.querySelector('.notification-item.empty-state');
        if (noNotifications) {
            noNotifications.remove();
        }
        
        updateMarkAllReadButton(); // Update button state after adding notification
    }

    // Mark notification as read
    function markNotificationAsRead(notificationId) {
        fetch(`${baseUrl}/notification/mark-read/${notificationId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const notificationItem = document.querySelector(`[data-notification-id="${notificationId}"]`);
                if (notificationItem) {
                    notificationItem.classList.remove('unread');
                }
                updateNotificationCount(data.unread_count);
                updateMarkAllReadButton(); // Update button state after marking as read
            }
        })
        .catch(error => console.error('Error:', error));
    }

    // Mark all notifications as read
    function markAllNotificationsAsRead(e) {
        const hasNotifications = document.querySelectorAll('.notification-item:not(.empty-state)').length > 0;
        if (!hasNotifications) {
            e.preventDefault();
            return;
        }

        e.preventDefault();
        fetch(`${baseUrl}/notification/mark-all-read/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.querySelectorAll('.notification-item.unread').forEach(item => {
                    item.classList.remove('unread');
                });
                updateNotificationCount(0);
                updateMarkAllReadButton(); // Update button state after marking all as read
            }
        })
        .catch(error => console.error('Error:', error));
    }

    // Update "Mark all as read" button state
    function updateMarkAllReadButton() {
        const markAllReadBtn = document.querySelector('.mark-read');
        if (!markAllReadBtn) return;

        const notificationContent = document.querySelector('.notification-content');
        const hasUnreadNotifications = document.querySelectorAll('.notification-item.unread').length > 0;
        const hasEmptyState = notificationContent.querySelector('.notification-item.empty-state') !== null;
        
        if (hasUnreadNotifications && !hasEmptyState) {
            markAllReadBtn.classList.remove('disabled');
            markAllReadBtn.style.pointerEvents = 'auto';
            markAllReadBtn.style.cursor = 'pointer';
            markAllReadBtn.title = 'Mark all notifications as read';
        } else {
            markAllReadBtn.classList.add('disabled');
        }
    }

    // Helper function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Add click event to all notification items
    document.querySelectorAll('.notification-item').forEach(item => {
        item.addEventListener('click', function() {
            const notificationId = this.getAttribute('data-notification-id');
            const redirectUrl = this.getAttribute('data-redirect-url');
            if (notificationId) {
                markNotificationAsRead(notificationId);
                if (redirectUrl) {
                    window.location.href = redirectUrl;
                }
            }
        });
    });

    // Add click event to "Mark All as Read" button
    const markAllReadBtn = document.querySelector('.mark-read');
    if (markAllReadBtn) {
        markAllReadBtn.addEventListener('click', markAllNotificationsAsRead);
    }

    // Initialize button state
    updateMarkAllReadButton();
});