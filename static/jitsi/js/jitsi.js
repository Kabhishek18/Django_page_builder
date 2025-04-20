/**
 * jitsi.js - Base JavaScript functionality for Jitsi app
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize components
    initAlerts();
    initMobileNavToggle();
    initTooltips();
    setupCopyToClipboard();
    initAccordions();
    initTabs();
    initSwitches();
});

/**
 * Initialize dismissible alerts
 */
function initAlerts() {
    // Get all close buttons in alerts
    const closeButtons = document.querySelectorAll('.alert .close');
    
    // Add click event to each close button
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Get the parent alert element
            const alert = this.parentElement;
            
            // Add fade-out class for animation
            alert.classList.add('fade-out');
            
            // Remove alert after animation completes
            setTimeout(() => {
                alert.remove();
            }, 300);
        });
    });
}

/**
 * Initialize mobile navigation toggle
 */
function initMobileNavToggle() {
    // Check if we're on mobile view
    const mediaQuery = window.matchMedia('(max-width: 768px)');
    
    if (mediaQuery.matches) {
        // Add mobile-specific navigation behavior
        const sidebarHeader = document.querySelector('.sidebar-header');
        
        if (sidebarHeader) {
            // Create toggle button if it doesn't exist
            let toggleButton = document.querySelector('.mobile-nav-toggle');
            
            if (!toggleButton) {
                toggleButton = document.createElement('button');
                toggleButton.classList.add('mobile-nav-toggle');
                toggleButton.innerHTML = '<i class="fas fa-bars"></i>';
                sidebarHeader.appendChild(toggleButton);
            }
            
            // Get sidebar menu
            const sidebarMenu = document.querySelector('.sidebar-menu');
            
            // Initially hide menu on mobile
            if (sidebarMenu) {
                sidebarMenu.classList.add('mobile-hidden');
                
                // Toggle menu visibility on button click
                toggleButton.addEventListener('click', function() {
                    sidebarMenu.classList.toggle('mobile-hidden');
                    
                    // Toggle icon
                    const icon = this.querySelector('i');
                    if (icon.classList.contains('fa-bars')) {
                        icon.classList.remove('fa-bars');
                        icon.classList.add('fa-times');
                    } else {
                        icon.classList.remove('fa-times');
                        icon.classList.add('fa-bars');
                    }
                });
            }
        }
    }
}

/**
 * Initialize tooltips for buttons and icons
 */
function initTooltips() {
    // Get all elements with title attribute
    const tooltipElements = document.querySelectorAll('[title]');
    
    tooltipElements.forEach(element => {
        // Store the title text
        const tooltipText = element.getAttribute('title');
        
        // Remove title attribute to prevent default browser tooltip
        element.removeAttribute('title');
        
        // Add data attribute to store tooltip text
        element.setAttribute('data-tooltip', tooltipText);
        
        // Add tooltip class
        element.classList.add('has-tooltip');
        
        // Add event listeners for tooltip
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
}

/**
 * Show tooltip on hover
 */
function showTooltip(event) {
    const element = event.target.closest('.has-tooltip');
    if (!element) return;
    
    const tooltipText = element.getAttribute('data-tooltip');
    
    // Create tooltip element
    const tooltip = document.createElement('div');
    tooltip.classList.add('tooltip');
    tooltip.textContent = tooltipText;
    
    // Add tooltip to body
    document.body.appendChild(tooltip);
    
    // Position tooltip
    positionTooltip(tooltip, element);
    
    // Store tooltip reference on element
    element._tooltip = tooltip;
}

/**
 * Hide tooltip on mouse leave
 */
function hideTooltip(event) {
    const element = event.target.closest('.has-tooltip');
    if (!element) return;
    
    if (element._tooltip) {
        element._tooltip.remove();
        element._tooltip = null;
    }
}

/**
 * Position tooltip relative to element
 */
function positionTooltip(tooltip, element) {
    const rect = element.getBoundingClientRect();
    const tooltipRect = tooltip.getBoundingClientRect();
    
    // Position above the element
    let top = rect.top - tooltipRect.height - 5;
    let left = rect.left + (rect.width / 2) - (tooltipRect.width / 2);
    
    // If tooltip would go off the top, position it below
    if (top < 0) {
        top = rect.bottom + 5;
    }
    
    // Make sure tooltip doesn't go off left or right edge
    if (left < 5) left = 5;
    if (left + tooltipRect.width > window.innerWidth - 5) {
        left = window.innerWidth - tooltipRect.width - 5;
    }
    
    // Set position
    tooltip.style.top = `${top + window.scrollY}px`;
    tooltip.style.left = `${left}px`;
}

/**
 * Setup copy-to-clipboard functionality
 */
function setupCopyToClipboard() {
    const copyButtons = document.querySelectorAll('.copy-to-clipboard');
    
    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Get the element or value to copy
            const targetId = this.getAttribute('data-copy-target');
            const target = document.getElementById(targetId);
            
            if (!target) return;
            
            // Get the text to copy
            const textToCopy = target.value || target.textContent;
            
            // Copy to clipboard
            navigator.clipboard.writeText(textToCopy).then(() => {
                // Show success feedback
                const originalText = this.innerHTML;
                this.innerHTML = '<i class="fas fa-check"></i> Copied!';
                
                // Restore original text after 2 seconds
                setTimeout(() => {
                    this.innerHTML = originalText;
                }, 2000);
            }).catch(err => {
                console.error('Failed to copy text: ', err);
            });
        });
    });
}

/**
 * Initialize accordion components
 */
function initAccordions() {
    const accordionHeaders = document.querySelectorAll('.accordion-header');
    
    accordionHeaders.forEach(header => {
        header.addEventListener('click', function() {
            // Toggle active class on parent accordion
            const accordion = this.parentElement;
            accordion.classList.toggle('active');
            
            // Close other accordions if needed (for single open accordion behavior)
            if (accordion.classList.contains('accordion-single') && accordion.classList.contains('active')) {
                const siblings = document.querySelectorAll('.accordion.accordion-single');
                siblings.forEach(sibling => {
                    if (sibling !== accordion && sibling.classList.contains('active')) {
                        sibling.classList.remove('active');
                    }
                });
            }
        });
    });
}

/**
 * Initialize tabs
 */
function initTabs() {
    const tabs = document.querySelectorAll('.tab');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            // Get tab container
            const tabContainer = this.closest('.tabs-container');
            if (!tabContainer) return;
            
            // Get tab id
            const tabId = this.getAttribute('data-tab');
            if (!tabId) return;
            
            // Deactivate all tabs
            tabContainer.querySelectorAll('.tab').forEach(t => {
                t.classList.remove('active');
            });
            
            // Deactivate all tab contents
            tabContainer.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            
            // Activate clicked tab
            this.classList.add('active');
            
            // Activate corresponding tab content
            const tabContent = tabContainer.querySelector(`.tab-content[data-tab="${tabId}"]`);
            if (tabContent) {
                tabContent.classList.add('active');
            }
        });
    });
}

/**
 * Initialize toggle switches
 */
function initSwitches() {
    const switches = document.querySelectorAll('.switch input[type="checkbox"]');
    
    switches.forEach(switchInput => {
        switchInput.addEventListener('change', function() {
            const formId = this.getAttribute('data-form');
            if (formId) {
                // If switch is associated with a form, submit the form
                const form = document.getElementById(formId);
                if (form) {
                    form.submit();
                }
            }
            
            // Handle any custom callback
            const callback = this.getAttribute('data-callback');
            if (callback && typeof window[callback] === 'function') {
                window[callback](this.checked);
            }
        });
    });
}

/**
 * Format time in "X days/hours/minutes ago" format
 */
function timeAgo(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.round((now - date) / 1000);
    const minutes = Math.round(seconds / 60);
    const hours = Math.round(minutes / 60);
    const days = Math.round(hours / 24);
    
    if (seconds < 60) {
        return "just now";
    } else if (minutes < 60) {
        return `${minutes} minute${minutes !== 1 ? 's' : ''} ago`;
    } else if (hours < 24) {
        return `${hours} hour${hours !== 1 ? 's' : ''} ago`;
    } else if (days < 30) {
        return `${days} day${days !== 1 ? 's' : ''} ago`;
    } else {
        // Format as regular date for older dates
        const options = { year: 'numeric', month: 'short', day: 'numeric' };
        return date.toLocaleDateString(undefined, options);
    }
}

/**
 * Handle confirmation dialogs
 */
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

/**
 * Format duration in minutes to hours and minutes
 */
function formatDuration(minutes) {
    if (!minutes) return 'N/A';
    
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    
    if (hours === 0) {
        return `${mins} min`;
    } else if (mins === 0) {
        return `${hours} hr`;
    } else {
        return `${hours} hr ${mins} min`;
    }
}

/**
 * Format date and time
 */
function formatDateTime(dateString, format = 'default') {
    if (!dateString) return 'N/A';
    
    const date = new Date(dateString);
    
    switch (format) {
        case 'time':
            return date.toLocaleTimeString(undefined, {
                hour: '2-digit',
                minute: '2-digit'
            });
        case 'date':
            return date.toLocaleDateString(undefined, {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        case 'short':
            return date.toLocaleDateString(undefined, {
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        case 'full':
            return date.toLocaleDateString(undefined, {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        default:
            return date.toLocaleDateString(undefined, {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
    }
}

/**
 * Generate a random ID
 */
function generateId(length = 8) {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
        result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
}