/**
 * static/messaging/js/messaging.js
 * Main JavaScript for messaging system
 */

// Global variables
let lastNotificationCheckTime = new Date();
let unreadMessagesCount = 0;
let activeConversationId = null;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Get the active conversation ID if on conversation detail page
    const conversationContainer = document.getElementById('message-container');
    if (conversationContainer) {
        const urlParts = window.location.pathname.split('/');
        activeConversationId = urlParts[urlParts.length - 2];
    }

    // Initialize notification checking
    initializeNotifications();
    
    // Make conversation items clickable
    initializeConversationList();
    
    // Auto-resize text areas
    initializeAutoResize();
    
    // Update unread count in title
    updateUnreadCountInTitle();
});

/**
 * Initialize conversation list
 */
function initializeConversationList() {
    const conversationItems = document.querySelectorAll('.conversation-item');
    conversationItems.forEach(item => {
        item.addEventListener('click', function() {
            const conversationId = this.getAttribute('data-conversation-id');
            if (conversationId) {
                window.location.href = `/messaging/conversation/${conversationId}/`;
            }
        });
    });
}

/**
 * Initialize auto-resize for textareas
 */
function initializeAutoResize() {
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
        
        // Initial resize
        textarea.dispatchEvent(new Event('input'));
    });
}

/**
 * Initialize notification checking
 */
function initializeNotifications() {
    // Check for notifications every 30 seconds
    checkForNewMessages();
    setInterval(checkForNewMessages, 30000);
    
    // Update title when tab gets focus
    window.addEventListener('focus', function() {
        document.title = document.title.replace(/^\(\d+\) /, '');
    });
}

/**
 * Check for new messages
 */
function checkForNewMessages() {
    // Skip if user is on a conversation page
    if (activeConversationId !== null) {
        return;
    }
    
    fetch('/messaging/unread-count/', {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            unreadMessagesCount = data.total_unread;
            updateUnreadCountInTitle();
            
            // Check for new message notifications
            if (unreadMessagesCount > 0) {
                checkForNotifications();
            }
        }
    })
    .catch(error => {
        console.error('Error checking for new messages:', error);
    });
}

/**
 * Check for notification details
 */
function checkForNotifications() {
    fetch('/messaging/notifications/', {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success' && data.unread_conversations.length > 0) {
            // Show notifications for the most recent unread conversation
            const conversation = data.unread_conversations[0];
            
            // Only show notification if it's newer than the last check
            const messageTime = new Date(conversation.timestamp);
            if (messageTime > lastNotificationCheckTime) {
                showNotification(conversation);
                lastNotificationCheckTime = new Date();
            }
        }
    })
    .catch(error => {
        console.error('Error checking for notifications:', error);
    });
}

/**
 * Show a notification for a new message
 */
function showNotification(conversation) {
    // Check if browser supports notifications
    if (!("Notification" in window)) {
        return;
    }
    
    // Request permission if needed
    if (Notification.permission === "default") {
        Notification.requestPermission();
    }
    
    // Show browser notification if allowed
    if (Notification.permission === "granted") {
        const notification = new Notification("New Message", {
            body: `${conversation.sender_name}: ${conversation.last_message_preview}`,
            icon: "/static/messaging/img/message-icon.png"
        });
        
        notification.onclick = function() {
            window.focus();
            window.location.href = `/messaging/conversation/${conversation.id}/`;
        };
    }
    
    // Also show in-page notification
    showInPageNotification(conversation);
}

/**
 * Show in-page notification
 */
function showInPageNotification(conversation) {
    // Remove any existing notifications
    const existingNotification = document.querySelector('.message-notification');
    if (existingNotification) {
        existingNotification.remove();
    }
    
    // Create new notification
    const notification = document.createElement('div');
    notification.className = 'message-notification';
    notification.innerHTML = `
        <div class="notification-header">
            <h5 class="notification-title">${conversation.name}</h5>
            <button type="button" class="notification-close">&times;</button>
        </div>
        <div class="notification-body">
            <div class="notification-content">
                <strong>${conversation.sender_name}:</strong> ${conversation.last_message_preview}
            </div>
            <div class="notification-time">${conversation.timestamp}</div>
        </div>
        <div class="notification-actions">
            <a href="/messaging/conversation/${conversation.id}/" class="btn btn-sm btn-primary">View</a>
        </div>
    `;
    
    // Add to document
    document.body.appendChild(notification);
    
    // Show notification
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    // Set up close button
    const closeButton = notification.querySelector('.notification-close');
    closeButton.addEventListener('click', function() {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    });
    
    // Auto hide after 5 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 5000);
}

/**
 * Update unread count in title
 */
function updateUnreadCountInTitle() {
    const originalTitle = document.title.replace(/^\(\d+\) /, '');
    
    if (unreadMessagesCount > 0 && !document.hasFocus()) {
        document.title = `(${unreadMessagesCount}) ${originalTitle}`;
    } else {
        document.title = originalTitle;
    }
}

/**
 * Format relative time (e.g., "2 minutes ago")
 */
function formatRelativeTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    if (diffInSeconds < 60) {
        return "just now";
    }
    
    const diffInMinutes = Math.floor(diffInSeconds / 60);
    if (diffInMinutes < 60) {
        return `${diffInMinutes} ${diffInMinutes === 1 ? 'minute' : 'minutes'} ago`;
    }
    
    const diffInHours = Math.floor(diffInMinutes / 60);
    if (diffInHours < 24) {
        return `${diffInHours} ${diffInHours === 1 ? 'hour' : 'hours'} ago`;
    }
    
    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays < 7) {
        return `${diffInDays} ${diffInDays === 1 ? 'day' : 'days'} ago`;
    }
    
    // If more than a week, return the actual date
    return date.toLocaleDateString();
}

/**
 * Handle emoji picker
 */
function initializeEmojiPicker() {
    const emojiButton = document.querySelector('.emoji-button');
    if (!emojiButton) return;
    
    const picker = new EmojiButton({
        position: 'top-start'
    });
    
    picker.on('emoji', emoji => {
        const messageInput = document.getElementById('message-input');
        messageInput.value += emoji;
        messageInput.focus();
    });
    
    emojiButton.addEventListener('click', () => {
        picker.togglePicker(emojiButton);
    });
}

/**
 * Handle file uploads
 */
function handleFileSelect(event) {
    const files = event.target.files;
    if (!files || files.length === 0) return;
    
    const file = files[0];
    const maxSize = 10 * 1024 * 1024; // 10 MB
    
    if (file.size > maxSize) {
        alert('File is too large. Maximum file size is 10 MB.');
        event.target.value = ''; // Clear the input
        return;
    }
    
    // Update attachment preview
    const preview = document.getElementById('attachment-preview');
    const nameElement = document.getElementById('attachment-name');
    
    if (preview && nameElement) {
        nameElement.textContent = file.name;
        preview.style.display = 'block';
    }
}

/**
 * Utility function to get CSRF token
 */
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}