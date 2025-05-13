// static/jitsi/js/jitsi.js

// Utility functions for Jitsi integration
const jitsiUtils = {
    // Toggle sidebar visibility
    toggleSidebar: function() {
        const sidebar = document.getElementById('meeting-sidebar');
        if (sidebar) {
            sidebar.classList.toggle('show');
        }
    },
    
    // Copy text to clipboard
    copyToClipboard: function(text) {
        const tempElement = document.createElement('textarea');
        tempElement.value = text;
        document.body.appendChild(tempElement);
        tempElement.select();
        document.execCommand('copy');
        document.body.removeChild(tempElement);
        
        // Show success message
        this.showToast('Copied to clipboard!');
    },
    
    // Show a toast notification
    showToast: function(message, type = 'success', duration = 3000) {
        let toastContainer = document.querySelector('.toast-container');
        
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container';
            document.body.appendChild(toastContainer);
        }
        
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        
        toastContainer.appendChild(toast);
        
        // Show the toast
        setTimeout(() => {
            toast.classList.add('show');
        }, 10);
        
        // Hide and remove after duration
        setTimeout(() => {
            toast.classList.remove('show');
            
            // Remove from DOM after fade out
            setTimeout(() => {
                toast.remove();
            }, 300);
        }, duration);
    },
    
    // End a meeting (for hosts)
    endMeeting: function(meetingId, redirectUrl) {
        if (confirm('Are you sure you want to end this meeting for all participants?')) {
            // Call the hangup method if Jitsi API is available
            if (window.jitsiApi) {
                window.jitsiApi.executeCommand('hangup');
            }
            
            // Make an AJAX call to end the meeting
            fetch(`/meetings/rooms/${meetingId}/end/`, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                if (response.ok) {
                    // Redirect to the specified URL
                    window.location.href = redirectUrl;
                } else {
                    console.error('Failed to end meeting');
                    this.showToast('Failed to end meeting', 'error');
                }
            })
            .catch(error => {
                console.error('Error ending meeting:', error);
                this.showToast('Error ending meeting', 'error');
            });
        }
    },
    
    // Confirm an action with a dialog
    confirmAction: function(message, callback) {
        if (confirm(message)) {
            callback();
        }
    },
    
    // Initialize common Jitsi elements
    initCommonElements: function() {
        // Set up copy buttons
        document.querySelectorAll('.copy-to-clipboard').forEach(button => {
            button.addEventListener('click', () => {
                const targetId = button.getAttribute('data-copy-target');
                const targetElement = document.getElementById(targetId);
                
                if (targetElement) {
                    this.copyToClipboard(targetElement.textContent);
                    
                    // Update button text temporarily
                    const originalHTML = button.innerHTML;
                    button.innerHTML = '<i class="fas fa-check"></i>';
                    
                    setTimeout(() => {
                        button.innerHTML = originalHTML;
                    }, 2000);
                }
            });
        });
        
        // Set up sidebar toggle
        const toggleButton = document.querySelector('.toggle-sidebar');
        if (toggleButton) {
            toggleButton.addEventListener('click', this.toggleSidebar);
        }
        
        // Close sidebar when clicking outside
        document.addEventListener('click', (e) => {
            const sidebar = document.getElementById('meeting-sidebar');
            if (sidebar && sidebar.classList.contains('show')) {
                if (!sidebar.contains(e.target) && !e.target.matches('.toggle-sidebar')) {
                    sidebar.classList.remove('show');
                }
            }
        });
    }
};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', function() {
    jitsiUtils.initCommonElements();
});