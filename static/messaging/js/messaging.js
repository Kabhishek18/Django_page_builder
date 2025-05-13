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

/**
 * messaging-utils.js - Utility functions for the messaging system
 */

const MessagingUtils = {
    /**
     * Format a timestamp as a relative time string (e.g., "2 hours ago")
     * @param {string|Date} timestamp - The timestamp to format
     * @returns {string} Formatted relative time
     */
    timeAgo: function(timestamp) {
        if (!timestamp) return '';
        
        const now = new Date();
        let date = timestamp;
        
        if (typeof timestamp === 'string') {
            date = new Date(timestamp);
        }
        
        const seconds = Math.floor((now - date) / 1000);
        
        // Less than a minute
        if (seconds < 60) {
            return 'Just now';
        }
        
        // Minutes
        const minutes = Math.floor(seconds / 60);
        if (minutes < 60) {
            return `${minutes}m ago`;
        }
        
        // Hours
        const hours = Math.floor(minutes / 60);
        if (hours < 24) {
            return `${hours}h ago`;
        }
        
        // Days
        const days = Math.floor(hours / 24);
        if (days < 7) {
            return `${days}d ago`;
        }
        
        // Weeks
        if (days < 30) {
            const weeks = Math.floor(days / 7);
            return `${weeks}w ago`;
        }
        
        // Months
        const months = Math.floor(days / 30);
        if (months < 12) {
            return `${months}mo ago`;
        }
        
        // Years
        const years = Math.floor(days / 365);
        return `${years}y ago`;
    },
    
    /**
     * Format a date based on how recent it is
     * @param {string|Date} date - The date to format
     * @returns {string} Formatted date
     */
    smartDate: function(date) {
        if (!date) return '';
        
        const now = new Date();
        let dateObj = date;
        
        if (typeof date === 'string') {
            dateObj = new Date(date);
        }
        
        // Today
        if (dateObj.toDateString() === now.toDateString()) {
            return 'Today';
        }
        
        // Yesterday
        const yesterday = new Date(now);
        yesterday.setDate(now.getDate() - 1);
        if (dateObj.toDateString() === yesterday.toDateString()) {
            return 'Yesterday';
        }
        
        // Within the last week
        const daysDiff = Math.floor((now - dateObj) / (1000 * 60 * 60 * 24));
        if (daysDiff < 7) {
            return dateObj.toLocaleDateString('en-US', { weekday: 'long' });
        }
        
        // Older
        return dateObj.toLocaleDateString('en-US', { 
            year: 'numeric', 
            month: 'short', 
            day: 'numeric' 
        });
    },
    
    /**
     * Format a time in a human-readable way
     * @param {string|Date} time - The time to format
     * @returns {string} Formatted time
     */
    formatTime: function(time) {
        if (!time) return '';
        
        let timeObj = time;
        
        if (typeof time === 'string') {
            timeObj = new Date(time);
        }
        
        return timeObj.toLocaleTimeString('en-US', { 
            hour: 'numeric', 
            minute: '2-digit',
            hour12: true 
        });
    },
    
    /**
     * Get user initials from name
     * @param {string} name - User name
     * @returns {string} Initials (1-2 characters)
     */
    getInitials: function(name) {
        if (!name) return '';
        
        // If name contains space, use first letter of first and last name
        if (name.includes(' ')) {
            const nameParts = name.split(' ');
            return (nameParts[0][0] + nameParts[nameParts.length - 1][0]).toUpperCase();
        }
        
        // Otherwise use first two letters of name
        return name.substring(0, 2).toUpperCase();
    },
    
    /**
     * Replace text emoticons with emoji
     * @param {string} text - Text containing emoticons
     * @returns {string} Text with emoticons replaced by emoji
     */
    replaceEmoticons: function(text) {
        if (!text) return '';
        
        const emoticons = {
            ':)': '😊',
            ':-)': '😊',
            ':(': '😞',
            ':-(': '😞',
            ':D': '😃',
            ':-D': '😃',
            ';)': '😉',
            ';-)': '😉',
            ':P': '😋',
            ':-P': '😋',
            ':p': '😋',
            ':-p': '😋',
            '<3': '❤️',
            ':O': '😮',
            ':-O': '😮',
            ':o': '😮',
            ':-o': '😮',
            '>:(': '😠',
            '>:-(': '😠',
            'XD': '😆',
            'xD': '😆',
            ':|': '😐',
            ':-|': '😐',
            ':/': '😕',
            ':-/': '😕',
            ':*': '😘',
            ':-*': '😘',
            '8)': '😎',
            '8-)': '😎',
            ':S': '😕',
            ':-S': '😕',
            ':s': '😕',
            ':-s': '😕'
        };
        
        let result = text;
        for (const [emoticon, emoji] of Object.entries(emoticons)) {
            result = result.replace(new RegExp(emoticon.replace(/([.*+?^=!:${}()|\[\]\/\\])/g, '\\$1'), 'g'), emoji);
        }
        
        return result;
    },
    
    /**
     * Detect and format URLs in text as HTML links
     * @param {string} text - Text content
     * @returns {string} HTML with links
     */
    linkify: function(text) {
        if (!text) return '';
        
        // URL pattern
        const urlPattern = /https?:\/\/[^\s]+/g;
        
        // Replace URLs with HTML links
        return text.replace(urlPattern, url => {
            return `<a href="${url}" target="_blank" rel="noopener noreferrer">${url}</a>`;
        });
    },
    
    /**
     * Detect and highlight @mentions in text
     * @param {string} text - Text content 
     * @param {string|number} currentUserId - Current user ID to highlight self-mentions
     * @returns {string} HTML with mentions highlighted
     */
    highlightMentions: function(text, currentUserId) {
        if (!text) return '';
        
        // Mention pattern (@username)
        const mentionPattern = /@([a-zA-Z0-9_]+)/g;
        
        // Replace mentions with highlighted spans
        return text.replace(mentionPattern, (match, username) => {
            const isSelfMention = currentUserId && username === String(currentUserId);
            const className = isSelfMention ? 'mention mention-self' : 'mention';
            return `<span class="${className}">${match}</span>`;
        });
    },
    
    /**
     * Get appropriate icon class for attachment type
     * @param {string} type - Attachment type
     * @returns {string} Font Awesome icon class
     */
    getAttachmentIcon: function(type) {
        switch (type) {
            case 'image':
                return 'fa-image';
            case 'document':
                return 'fa-file-alt';
            case 'video':
                return 'fa-video';
            case 'audio':
                return 'fa-volume-up';
            default:
                return 'fa-paperclip';
        }
    },
    
    /**
     * Format file size in human-readable format (e.g., "2.5 MB")
     * @param {number} bytes - File size in bytes
     * @returns {string} Formatted file size
     */
    formatFileSize: function(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    
    /**
     * Format a filename for display (truncate if too long)
     * @param {string} filename - Full filename
     * @param {number} maxLength - Maximum length before truncation
     * @returns {string} Formatted filename
     */
    formatFilename: function(filename, maxLength = 20) {
        if (!filename) return '';
        
        // Extract just the filename from the path
        const name = filename.split('/').pop();
        
        // If the filename is too long, truncate it
        if (name.length > maxLength) {
            const extension = name.lastIndexOf('.') !== -1 ? 
                name.substring(name.lastIndexOf('.')) : '';
            const baseName = name.substring(0, name.length - extension.length);
            
            return baseName.substring(0, maxLength - 3) + '...' + extension;
        }
        
        return name;
    },
    
    /**
     * Play notification sound
     */
    playNotificationSound: function() {
        // Create audio element if it doesn't exist
        let audioElement = document.getElementById('notification-sound');
        
        if (!audioElement) {
            audioElement = document.createElement('audio');
            audioElement.id = 'notification-sound';
            audioElement.src = '/static/messaging/sounds/notification.mp3';
            audioElement.style.display = 'none';
            document.body.appendChild(audioElement);
        }
        
        // Play sound
        audioElement.play().catch(error => {
            console.log('Auto-play prevented by browser. User interaction required.');
        });
    },
    
    /**
     * Show a toast notification
     * @param {string} message - Notification message
     * @param {string} type - Notification type (success, error, warning, info)
     * @param {number} duration - Duration in milliseconds
     */
    showToast: function(message, type = 'info', duration = 3000) {
        // Create toast container if it doesn't exist
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container';
            document.body.appendChild(toastContainer);
        }
        
        // Create toast element
        const toast = document.createElement('div');
        toast.className = 'toast';
        
        // Add background color based on type
        if (type === 'success') {
            toast.style.backgroundColor = '#28a745';
        } else if (type === 'error') {
            toast.style.backgroundColor = '#dc3545';
        } else if (type === 'warning') {
            toast.style.backgroundColor = '#ffc107';
            toast.style.color = '#212529';
        }
        
        // Set content
        toast.innerHTML = `
            <div class="toast-content">
                ${message}
            </div>
        `;
        
        // Add to container
        toastContainer.appendChild(toast);
        
        // Show toast
        setTimeout(() => {
            toast.classList.add('show');
        }, 10);
        
        // Hide and remove after duration
        setTimeout(() => {
            toast.classList.remove('show');
            
            // Remove from DOM after animation
            setTimeout(() => {
                toast.remove();
            }, 300);
        }, duration);
    },
    
    /**
     * Copy text to clipboard
     * @param {string} text - Text to copy
     * @returns {Promise<boolean>} Success state
     */
    copyToClipboard: function(text) {
        return navigator.clipboard.writeText(text)
            .then(() => {
                this.showToast('Copied to clipboard', 'success');
                return true;
            })
            .catch(err => {
                console.error('Could not copy text: ', err);
                this.showToast('Failed to copy to clipboard', 'error');
                return false;
            });
    },
    
    /**
     * Check if a date is today
     * @param {Date} date - Date to check
     * @returns {boolean} True if date is today
     */
    isToday: function(date) {
        const today = new Date();
        return date.getDate() === today.getDate() &&
            date.getMonth() === today.getMonth() &&
            date.getFullYear() === today.getFullYear();
    },
    
    /**
     * Check if a date is yesterday
     * @param {Date} date - Date to check
     * @returns {boolean} True if date is yesterday
     */
    isYesterday: function(date) {
        const yesterday = new Date();
        yesterday.setDate(yesterday.getDate() - 1);
        
        return date.getDate() === yesterday.getDate() &&
            date.getMonth() === yesterday.getMonth() &&
            date.getFullYear() === yesterday.getFullYear();
    }
};

// Make available globally
window.MessagingUtils = MessagingUtils;