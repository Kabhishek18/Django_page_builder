/**
 * customize_meeting.js - JavaScript for the customize meeting page
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tabs
    initTabs();
    // Initialize color pickers
    initColorPickers();
    // Initialize form validation
    setupFormValidation();
    // Initialize file input preview
    setupFilePreview();
});

/**
 * Initialize tabs
 */
function initTabs() {
    const tabs = document.querySelectorAll('.tab');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            // Deactivate all tabs
            document.querySelectorAll('.tab').forEach(t => {
                t.classList.remove('active');
            });
            
            // Deactivate all tab contents
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            
            // Activate clicked tab
            this.classList.add('active');
            
            // Activate corresponding tab content
            const tabId = this.getAttribute('data-tab');
            document.querySelector(`.tab-content[data-tab="${tabId}"]`).classList.add('active');
        });
    });
}

/**
 * Initialize color pickers
 */
function initColorPickers() {
    const colorInputs = document.querySelectorAll('input[type="color"]');
    
    colorInputs.forEach(input => {
        // Update color value text when color changes
        input.addEventListener('input', function() {
            const valueSpan = this.nextElementSibling;
            if (valueSpan) {
                valueSpan.textContent = this.value.toUpperCase();
            }
        });
        
        // Ensure color value text is displayed initially
        const valueSpan = input.nextElementSibling;
        if (valueSpan) {
            valueSpan.textContent = input.value.toUpperCase();
        }
    });
}

/**
 * Setup form validation
 */
function setupFormValidation() {
    const form = document.querySelector('form');
    
    if (form) {
        form.addEventListener('submit', function(e) {
            // Simple validation for required fields
            const requiredInputs = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredInputs.forEach(input => {
                if (!input.value.trim()) {
                    input.classList.add('is-invalid');
                    isValid = false;
                } else {
                    input.classList.remove('is-invalid');
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                alert('Please fill in all required fields.');
            }
        });
    }
}

/**
 * Setup file input preview
 */
function setupFilePreview() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const file = this.files[0];
                const reader = new FileReader();
                
                // Find preview container
                let previewContainer = this.parentNode.querySelector('.preview-container');
                if (!previewContainer) {
                    // Create preview container if it doesn't exist
                    previewContainer = document.createElement('div');
                    previewContainer.className = 'preview-container';
                    
                    const label = document.createElement('p');
                    label.className = 'label';
                    label.textContent = 'Preview:';
                    previewContainer.appendChild(label);
                    
                    const img = document.createElement('img');
                    img.className = this.id.includes('logo') ? 'logo-preview' : 'background-preview';
                    previewContainer.appendChild(img);
                    
                    this.parentNode.appendChild(previewContainer);
                }
                
                // Update preview image when file is loaded
                reader.onload = function(e) {
                    const img = previewContainer.querySelector('img');
                    if (img) {
                        img.src = e.target.result;
                    }
                };
                
                // Read the file
                reader.readAsDataURL(file);
            }
        });
    });
}

/**
 * Reset customization to default
 */
function resetToDefault() {
    if (confirm('Are you sure you want to reset all customizations to default? This cannot be undone.')) {
        // Reset color pickers
        document.getElementById('id_primary_color').value = '#0056E0';
        document.getElementById('id_secondary_color').value = '#17A0DB';
        document.getElementById('id_background_color').value = '#040404';
        
        // Update color value texts
        document.querySelectorAll('input[type="color"]').forEach(input => {
            const valueSpan = input.nextElementSibling;
            if (valueSpan) {
                valueSpan.textContent = input.value.toUpperCase();
            }
        });
        
        // Reset checkboxes
        document.getElementById('id_show_footer').checked = true;
        
        // Reset text inputs
        document.getElementById('id_footer_text').value = '';
        
        // Reset file inputs (can't directly reset value due to security restrictions)
        document.querySelectorAll('input[type="file"]').forEach(input => {
            // Create a clone with no value
            const newInput = input.cloneNode(true);
            input.parentNode.replaceChild(newInput, input);
            
            // Remove preview containers
            const previewContainer = newInput.parentNode.querySelector('.preview-container');
            if (previewContainer) {
                previewContainer.remove();
            }
        });
        
        // Reset custom CSS/JS
        document.getElementById('id_custom_css').value = '';
        document.getElementById('id_custom_js').value = '';
        
        // Reset feature toggles to defaults
        document.querySelectorAll('.feature-group input[type="checkbox"]').forEach(checkbox => {
            // Enable core features by default
            if (checkbox.id.includes('audio') || 
                checkbox.id.includes('video') || 
                checkbox.id.includes('chat') ||
                checkbox.id.includes('screen_sharing') ||
                checkbox.id.includes('raise_hand') ||
                checkbox.id.includes('reactions') ||
                checkbox.id.includes('tile_view')) {
                checkbox.checked = true;
            } else {
                checkbox.checked = false;
            }
        });
        
        alert('All customizations have been reset to default values.');
    }
}