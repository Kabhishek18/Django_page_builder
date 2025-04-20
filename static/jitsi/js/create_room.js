/**
 * create_room.js - JavaScript for the create room page
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize form validation
    setupFormValidation();
    // Initialize datetime picker enhancement
    enhanceDateTimePicker();
    // Initialize password generator
    setupPasswordGenerator();
});

/**
 * Setup form validation
 */
function setupFormValidation() {
    const form = document.querySelector('.create-room-form');
    
    if (form) {
        form.addEventListener('submit', function(e) {
            const isValid = validateForm();
            
            if (!isValid) {
                e.preventDefault();
            }
        });
    }
}

/**
 * Validate form fields
 */
function validateForm() {
    // Get required fields
    const nameField = document.getElementById('id_name');
    const scheduledAtField = document.getElementById('id_scheduled_at');
    
    let isValid = true;
    
    // Clear previous errors
    clearValidationErrors();
    
    // Validate name
    if (!nameField.value.trim()) {
        addValidationError(nameField, 'Please enter a meeting name');
        isValid = false;
    }
    
    // Validate scheduled time
    if (!scheduledAtField.value.trim()) {
        addValidationError(scheduledAtField, 'Please set a meeting date and time');
        isValid = false;
    } else {
        // Check if date is in the past
        const scheduledDate = new Date(scheduledAtField.value);
        const now = new Date();
        
        if (scheduledDate < now) {
            addValidationError(scheduledAtField, 'Meeting time cannot be in the past');
            isValid = false;
        }
    }
    
    // Validate password fields if password protection is enabled
    const passwordProtected = document.getElementById('id_password_protected');
    
    if (passwordProtected && passwordProtected.checked) {
        const moderatorPassword = document.getElementById('id_moderator_password');
        const attendeePassword = document.getElementById('id_attendee_password');
        
        if (!moderatorPassword.value.trim()) {
            addValidationError(moderatorPassword, 'Moderator password is required');
            isValid = false;
        }
        
        if (!attendeePassword.value.trim()) {
            addValidationError(attendeePassword, 'Attendee password is required');
            isValid = false;
        }
    }
    
    return isValid;
}

/**
 * Add validation error to a field
 */
function addValidationError(field, message) {
    // Add error class to field
    field.classList.add('is-invalid');
    
    // Create error message element
    const errorElement = document.createElement('div');
    errorElement.className = 'invalid-feedback';
    errorElement.textContent = message;
    
    // Add error message after the field
    field.parentNode.appendChild(errorElement);
}

/**
 * Clear previous validation errors
 */
function clearValidationErrors() {
    // Remove error class from all fields
    const invalidFields = document.querySelectorAll('.is-invalid');
    invalidFields.forEach(field => {
        field.classList.remove('is-invalid');
    });
    
    // Remove error messages
    const errorMessages = document.querySelectorAll('.invalid-feedback');
    errorMessages.forEach(message => {
        message.remove();
    });
}

/**
 * Enhance the datetime picker
 */
function enhanceDateTimePicker() {
    const dateField = document.getElementById('id_scheduled_at');
    
    if (dateField) {
        // Set min date to now
        const now = new Date();
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        
        const minDateTime = `${year}-${month}-${day}T${hours}:${minutes}`;
        dateField.setAttribute('min', minDateTime);
        
        // If no date is set, default to current date + 1 hour
        if (!dateField.value) {
            const defaultDate = new Date(now);
            defaultDate.setHours(defaultDate.getHours() + 1);
            
            const defaultYear = defaultDate.getFullYear();
            const defaultMonth = String(defaultDate.getMonth() + 1).padStart(2, '0');
            const defaultDay = String(defaultDate.getDate()).padStart(2, '0');
            const defaultHours = String(defaultDate.getHours()).padStart(2, '0');
            const defaultMinutes = String(defaultDate.getMinutes()).padStart(2, '0');
            
            const defaultDateTime = `${defaultYear}-${defaultMonth}-${defaultDay}T${defaultHours}:${defaultMinutes}`;
            dateField.value = defaultDateTime;
        }
    }
}

/**
 * Setup password generator
 */
function setupPasswordGenerator() {
    // Add password generation buttons next to password fields
    const passwordFields = document.querySelectorAll('#id_moderator_password, #id_attendee_password');
    
    passwordFields.forEach(field => {
        const generateBtn = document.createElement('button');
        generateBtn.type = 'button';
        generateBtn.className = 'btn btn-sm btn-outline-secondary generate-password';
        generateBtn.innerHTML = '<i class="fas fa-magic"></i> Generate';
        generateBtn.style.marginTop = '5px';
        
        generateBtn.addEventListener('click', function() {
            field.value = generateRandomPassword();
        });
        
        // Insert button after the field
        field.insertAdjacentElement('afterend', generateBtn);
    });
    
    // Generate both passwords button
    const passwordFieldsContainer = document.getElementById('password-fields');
    if (passwordFieldsContainer) {
        const generateAllBtn = document.createElement('button');
        generateAllBtn.type = 'button';
        generateAllBtn.className = 'btn btn-sm btn-outline-primary';
        generateAllBtn.innerHTML = '<i class="fas fa-key"></i> Generate Both Passwords';
        generateAllBtn.style.marginTop = '15px';
        
        generateAllBtn.addEventListener('click', function() {
            document.getElementById('id_moderator_password').value = generateRandomPassword(10);
            document.getElementById('id_attendee_password').value = generateRandomPassword(8);
        });
        
        // Add to the end of the password fields container
        passwordFieldsContainer.appendChild(generateAllBtn);
    }
}

/**
 * Generate a random password
 */
function generateRandomPassword(length = 8) {
    const charset = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789';
    let password = '';
    
    for (let i = 0; i < length; i++) {
        const randomIndex = Math.floor(Math.random() * charset.length);
        password += charset.charAt(randomIndex);
    }
    
    return password;
}

/**
 * Toggle password fields based on checkbox
 */
function togglePasswordFields(isChecked) {
    const passwordFields = document.getElementById('password-fields');
    passwordFields.style.display = isChecked ? 'block' : 'none';
    
    // Set required attribute based on checkbox state
    const moderatorPassword = document.getElementById('id_moderator_password');
    const attendeePassword = document.getElementById('id_attendee_password');
    
    if (isChecked) {
        moderatorPassword.setAttribute('required', 'required');
        attendeePassword.setAttribute('required', 'required');
        
        // Generate passwords if empty
        if (!moderatorPassword.value) {
            moderatorPassword.value = generateRandomPassword(10);
        }
        
        if (!attendeePassword.value) {
            attendeePassword.value = generateRandomPassword(8);
        }
    } else {
        moderatorPassword.removeAttribute('required');
        attendeePassword.removeAttribute('required');
    }
}