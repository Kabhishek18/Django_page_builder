/**
 * dashboard.js - Specific JavaScript for the Jitsi dashboard
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize dashboard-specific components
    formatTimeElements();
    formatDurationElements();
    initDeleteConfirmations();
    setupTableFilters();
    setupAutoRefresh();
    initStatusIndicators();
    setupDashboardCharts();
});

/**
 * Format relative time elements
 */
function formatTimeElements() {
    // Find all elements with data-timestamp attribute
    const timeElements = document.querySelectorAll('[data-timestamp]');
    
    timeElements.forEach(element => {
        const timestamp = element.getAttribute('data-timestamp');
        if (timestamp) {
            // Use the timeAgo utility function from base JS
            element.textContent = window.jitsiUtils.timeAgo(timestamp);
        }
    });
}

/**
 * Format duration elements
 */
function formatDurationElements() {
    // Find all elements with data-duration attribute (in minutes)
    const durationElements = document.querySelectorAll('[data-duration]');
    
    durationElements.forEach(element => {
        const duration = element.getAttribute('data-duration');
        if (duration) {
            // Use the formatDuration utility function from base JS
            element.textContent = window.jitsiUtils.formatDuration(parseInt(duration, 10));
        }
    });
}

/**
 * Initialize confirmation dialogs for delete actions
 */
function initDeleteConfirmations() {
    const deleteButtons = document.querySelectorAll('.delete-meeting');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const meetingName = this.getAttribute('data-meeting-name');
            const href = this.getAttribute('href');
            
            // Use confirmAction utility from base JS
            window.jitsiUtils.confirmAction(
                `Are you sure you want to delete "${meetingName}"? This action cannot be undone.`,
                () => {
                    window.location.href = href;
                }
            );
        });
    });
}

/**
 * Setup table filtering
 */
function setupTableFilters() {
    // Get filter elements
    const filterInput = document.getElementById('meeting-search');
    const statusFilter = document.getElementById('status-filter');
    
    if (filterInput) {
        filterInput.addEventListener('input', applyFilters);
    }
    
    if (statusFilter) {
        statusFilter.addEventListener('change', applyFilters);
    }
}

/**
 * Apply filters to meeting tables
 */
function applyFilters() {
    // Get filter values
    const searchTerm = document.getElementById('meeting-search')?.value.toLowerCase() || '';
    const statusFilter = document.getElementById('status-filter')?.value || 'all';
    
    // Get all meeting rows
    const meetingRows = document.querySelectorAll('.meetings-table tbody tr');
    
    meetingRows.forEach(row => {
        const meetingName = row.querySelector('td:first-child').textContent.toLowerCase();
        const meetingStatus = row.getAttribute('data-status');
        
        // Check if meeting matches search term
        const matchesSearch = searchTerm === '' || meetingName.includes(searchTerm);
        
        // Check if meeting matches status filter
        const matchesStatus = statusFilter === 'all' || statusFilter === meetingStatus;
        
        // Show/hide based on filters
        if (matchesSearch && matchesStatus) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
    
    // Check if we need to show empty state
    const visibleRows = document.querySelectorAll('.meetings-table tbody tr:not([style*="display: none"])');
    const emptyStates = document.querySelectorAll('.filtered-empty-state');
    
    emptyStates.forEach(emptyState => {
        if (visibleRows.length === 0) {
            emptyState.style.display = 'block';
        } else {
            emptyState.style.display = 'none';
        }
    });
}

/**
 * Setup auto-refresh for active meetings
 */
function setupAutoRefresh() {
    // Check if we have active meetings section
    const activeSection = document.querySelector('.active-meetings-section');
    
    if (activeSection) {
        // Refresh active meetings every 30 seconds
        setInterval(refreshActiveMeetings, 30000);
    }
}

/**
 * Refresh active meetings via AJAX
 */
function refreshActiveMeetings() {
    // Get the current URL
    const currentUrl = window.location.href;
    
    // Create a new URL for the AJAX request
    const refreshUrl = new URL(currentUrl);
    refreshUrl.searchParams.set('partial', 'active_meetings');
    
    // Create loading indicator
    const activeSection = document.querySelector('.active-meetings-section');
    const loadingIndicator = document.createElement('div');
    loadingIndicator.className = 'loading-overlay';
    loadingIndicator.innerHTML = '<div class="loading"></div>';
    
    // Fetch updated active meetings
    fetch(refreshUrl)
        .then(response => response.text())
        .then(html => {
            // Update active meetings section
            activeSection.innerHTML = html;
            
            // Re-initialize components for new content
            formatTimeElements();
            formatDurationElements();
        })
        .catch(error => {
            console.error('Failed to refresh active meetings:', error);
        })
        .finally(() => {
            // Remove loading indicator
            const overlay = document.querySelector('.loading-overlay');
            if (overlay) {
                overlay.remove();
            }
        });
}

/**
 * Initialize status indicators
 */
function initStatusIndicators() {
    const statusElements = document.querySelectorAll('[data-status]');
    
    statusElements.forEach(element => {
        const status = element.getAttribute('data-status');
        if (status) {
            element.classList.add(`status-${status}`);
        }
    });
}

/**
 * Setup dashboard charts
 */
function setupDashboardCharts() {
    // Check if Chart.js is available
    if (typeof Chart === 'undefined') {
        console.warn('Chart.js is not available. Skipping dashboard charts.');
        return;
    }
    
    // Weekly meetings chart
    const weeklyMeetingsCanvas = document.getElementById('weekly-meetings-chart');
    if (weeklyMeetingsCanvas) {
        const ctx = weeklyMeetingsCanvas.getContext('2d');
        
        // Get data from data attributes
        const labels = JSON.parse(weeklyMeetingsCanvas.getAttribute('data-labels') || '[]');
        const data = JSON.parse(weeklyMeetingsCanvas.getAttribute('data-values') || '[]');
        
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Meetings',
                    data: data,
                    backgroundColor: 'rgba(52, 152, 219, 0.7)',
                    borderColor: 'rgba(52, 152, 219, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                }
            }
        });
    }
    
    // Meeting duration chart
    const meetingDurationCanvas = document.getElementById('meeting-duration-chart');
    if (meetingDurationCanvas) {
        const ctx = meetingDurationCanvas.getContext('2d');
        
        // Get data from data attributes
        const labels = JSON.parse(meetingDurationCanvas.getAttribute('data-labels') || '[]');
        const data = JSON.parse(meetingDurationCanvas.getAttribute('data-values') || '[]');
        
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Avg. Duration (min)',
                    data: data,
                    backgroundColor: 'rgba(46, 204, 113, 0.2)',
                    borderColor: 'rgba(46, 204, 113, 1)',
                    borderWidth: 2,
                    tension: 0.2
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
    
    // Participants chart
    const participantsCanvas = document.getElementById('participants-chart');
    if (participantsCanvas) {
        const ctx = participantsCanvas.getContext('2d');
        
        // Get data from data attributes
        const labels = JSON.parse(participantsCanvas.getAttribute('data-labels') || '[]');
        const data = JSON.parse(participantsCanvas.getAttribute('data-values') || '[]');
        
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Participants',
                    data: data,
                    backgroundColor: 'rgba(155, 89, 182, 0.2)',
                    borderColor: 'rgba(155, 89, 182, 1)',
                    borderWidth: 2,
                    tension: 0.2
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                }
            }
        });
    }
}