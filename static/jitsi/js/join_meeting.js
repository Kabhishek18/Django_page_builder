/**
 * Enhanced Join Meeting JavaScript
 * Provides Google Meet-like functionality for the Jitsi integration
 */

let jitsiApi;
let meetingStartTime;
let timerInterval;
let activeSidebar = false;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Nothing here yet - main initialization happens in the template
    // This file is for supporting functions
});

/**
 * Initializes Google Meet-like controls for Jitsi
 * @param {Object} api - The Jitsi Meet API instance
 * @param {Object} featureConfig - Feature configuration from the server
 */
function initGoogleMeetControls(api, featureConfig) {
    const controlsContainer = document.querySelector('.control-buttons');
    
    // Clear any existing buttons
    controlsContainer.innerHTML = '';
    
    // Add microphone button if enabled
    if (featureConfig.enable_audio !== false) {
        addControlButton(controlsContainer, 'microphone', 'fa-microphone', 'Toggle microphone', function() {
            api.executeCommand('toggleAudio');
        });
    }
    
    // Add camera button if enabled
    if (featureConfig.enable_video !== false) {
        addControlButton(controlsContainer, 'camera', 'fa-video', 'Toggle camera', function() {
            api.executeCommand('toggleVideo');
        });
    }
    
    // Add screen sharing button if enabled
    if (featureConfig.enable_screen_sharing !== false) {
        addControlButton(controlsContainer, 'screen-share', 'fa-desktop', 'Share screen', function() {
            api.executeCommand('toggleShareScreen');
        });
    }
    
    // Add raise hand button if enabled
    if (featureConfig.enable_raise_hand !== false) {
        addControlButton(controlsContainer, 'raise-hand', 'fa-hand', 'Raise hand', function() {
            api.executeCommand('toggleRaiseHand');
        });
    }
    
    // Add button to toggle chat if enabled
    if (featureConfig.enable_chat !== false) {
        addControlButton(controlsContainer, 'chat', 'fa-comment', 'Toggle chat', function() {
            api.executeCommand('toggleChat');
        });
    }
    
    // Add tile view button if enabled
    if (featureConfig.enable_tile_view !== false) {
        addControlButton(controlsContainer, 'tile-view', 'fa-th-large', 'Toggle tile view', function() {
            api.executeCommand('toggleTileView');
        });
    }
    
    // Add button for participants list
    addControlButton(controlsContainer, 'participants', 'fa-users', 'Participants', function() {
        api.executeCommand('toggleParticipantsPane');
    });
    
    // Add button for meeting info sidebar
    addControlButton(controlsContainer, 'info', 'fa-info-circle', 'Meeting info', function() {
        toggleSidebar();
    });
    
    // Add end call button
    addControlButton(controlsContainer, 'end-call', 'fa-phone-slash', 'Leave meeting', function() {
        api.executeCommand('hangup');
    }, 'end-call');
}

/**
 * Adds a control button to the container
 * @param {HTMLElement} container - The container to add the button to
 * @param {string} id - Button ID
 * @param {string} iconClass - Font Awesome icon class
 * @param {string} tooltip - Button tooltip
 * @param {Function} clickHandler - Click event handler
 * @param {string} extraClass - Additional CSS class
 */
function addControlButton(container, id, iconClass, tooltip, clickHandler, extraClass = '') {
    const button = document.createElement('button');
    button.id = `control-button-${id}`;
    button.className = `control-button ${extraClass}`;
    button.setAttribute('title', tooltip);
    button.innerHTML = `<i class="fas ${iconClass}"></i>`;
    button.addEventListener('click', clickHandler);
    container.appendChild(button);
}

/**
 * Updates a control button state
 * @param {string} type - Button type (microphone, camera, etc.)
 * @param {boolean} disabled - Whether the feature is disabled
 */
function updateControlButton(type, disabled) {
    let buttonId;
    let iconClass;
    
    if (type === 'microphone') {
        buttonId = 'control-button-microphone';
        iconClass = disabled ? 'fa-microphone-slash' : 'fa-microphone';
    } else if (type === 'camera') {
        buttonId = 'control-button-camera';
        iconClass = disabled ? 'fa-video-slash' : 'fa-video';
    } else if (type === 'screen-share') {
        buttonId = 'control-button-screen-share';
        // No icon change, but we'll update the color
    }
    
    const button = document.getElementById(buttonId);
    if (button) {
        const icon = button.querySelector('i');
        if (icon && iconClass) {
            icon.className = `fas ${iconClass}`;
        }
        
        if (disabled) {
            button.classList.add('off');
            button.classList.remove('active');
        } else {
            button.classList.remove('off');
            button.classList.add('active');
        }
    }
}

/**
 * Starts the meeting timer
 */
function startMeetingTimer() {
    meetingStartTime = new Date();
    const timerElement = document.getElementById('meeting-time');
    
    timerInterval = setInterval(function() {
        const now = new Date();
        const diff = now - meetingStartTime;
        
        const hours = Math.floor(diff / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((diff % (1000 * 60)) / 1000);
        
        const formattedTime = 
            String(hours).padStart(2, '0') + ':' + 
            String(minutes).padStart(2, '0') + ':' + 
            String(seconds).padStart(2, '0');
        
        if (timerElement) {
            timerElement.textContent = formattedTime;
        }
    }, 1000);
}

/**
 * Toggles the sidebar visibility
 */
function toggleSidebar() {
    const sidebar = document.getElementById('meeting-sidebar');
    if (sidebar) {
        activeSidebar = !activeSidebar;
        sidebar.classList.toggle('show', activeSidebar);
    }
}

/**
 * Copies the meeting link to clipboard
 */
function copyMeetingLink() {
    const meetingLink = document.getElementById('meeting-link').textContent;
    navigator.clipboard.writeText(meetingLink).then(function() {
        // Show a success message
        const copyButton = document.querySelector('.copy-to-clipboard');
        const originalIcon = copyButton.innerHTML;
        copyButton.innerHTML = '<i class="fas fa-check"></i>';
        
        setTimeout(function() {
            copyButton.innerHTML = originalIcon;
        }, 2000);
    }).catch(function(err) {
        console.error('Could not copy text: ', err);
    });
}

/**
 * Ends the meeting (host function)
 */
function endMeeting() {
    if (confirm('Are you sure you want to end this meeting for all participants?')) {
        // Call the hangup method from the Jitsi API
        if (window.jitsiApi) {
            window.jitsiApi.executeCommand('hangup');
            
            // Make an AJAX call to end the meeting
            const endMeetingUrl = document.querySelector('[data-end-meeting-url]')?.getAttribute('data-end-meeting-url');
            
            if (endMeetingUrl) {
                fetch(endMeetingUrl, {
                    method: 'GET',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    }
                }).then(response => {
                    if (response.ok) {
                        // Redirect is handled by the server response
                    } else {
                        console.error('Failed to end meeting');
                    }
                }).catch(error => {
                    console.error('Error ending meeting:', error);
                });
            }
        }
    }
}

// Clean up when page is unloaded
window.addEventListener('beforeunload', function() {
    if (timerInterval) {
        clearInterval(timerInterval);
    }
});