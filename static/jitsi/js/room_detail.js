/**
 * room_detail.js - JavaScript for the room detail page
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize copy to clipboard functionality
    setupCopyLink();
    // Handle password visibility toggling
    setupPasswordToggle();
});

/**
 * Setup copy to clipboard functionality
 */
function setupCopyLink() {
    // This is now handled by the base JS file's copyToClipboard function
    // The button has the copy-to-clipboard class and data-copy-target attribute
}

/**
 * Setup password visibility toggling
 */
function setupPasswordToggle() {
    const passwordFields = document.querySelectorAll('.password-field');
    
    passwordFields.forEach(field => {
        const toggleButton = field.nextElementSibling;
        if (toggleButton && toggleButton.classList.contains('password-toggle')) {
            toggleButton.addEventListener('click', function() {
                const fieldType = field.getAttribute('type');
                
                if (fieldType === 'password') {
                    field.setAttribute('type', 'text');
                    this.innerHTML = '<i class="fas fa-eye-slash"></i>';
                } else {
                    field.setAttribute('type', 'password');
                    this.innerHTML = '<i class="fas fa-eye"></i>';
                }
            });
        }
    });
}

/**
 * Confirm cancellation before submitting the form
 */
function confirmCancel() {
    jitsiUtils.confirmAction(
        'Are you sure you want to cancel this meeting? This action cannot be undone.',
        function() {
            document.getElementById('cancel-form').submit();
        }
    );
}