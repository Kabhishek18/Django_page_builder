/**
 * Block Admin JavaScript
 * 
 * This script enhances the admin interface for Blocks by:
 * - Showing/hiding fields based on block type
 * - Previewing template blocks
 * - Improving JSON field editing for settings
 */

// Template selection enhancement
function setupTemplateSelect() {
    const templateSelect = $('.template-select');
    
    if (templateSelect.length) {
        // Add a container for template preview
        templateSelect.after('<div class="template-preview" style="margin-top: 10px; display: none;"></div>');
        const previewContainer = templateSelect.next('.template-preview');
        
        // Function to update preview
        function updateTemplatePreview() {
            const selectedTemplate = templateSelect.val();
            if (selectedTemplate) {
                // Show loading indicator
                previewContainer.html('<p>Loading preview...</p>').show();
                
                // Ajax request to get template preview
                $.get('/admin/pagebuilder/preview-template/' + selectedTemplate + '/', function(data) {
                    previewContainer.html(data).show();
                }).fail(function() {
                    previewContainer.html('<p>Preview not available</p>').show();
                });
            } else {
                previewContainer.hide();
            }
        }
        
        // Update on change
        templateSelect.on('change', updateTemplatePreview);
        
        // Initial update if a value is selected
        if (templateSelect.val()) {
            updateTemplatePreview();
        }
    }
}

// Call

(function($) {
    "use strict";
    
    $(document).ready(function() {
        // Function to show/hide fields based on block type
        function updateBlockTypeFields() {
            const blockType = $('#id_type').val();
            
            // Hide all type-specific fields first
            $('.field-template_name, .field-html_content, .field-wysiwyg_content').hide();
            
            // Show relevant fields based on selected type
            if (blockType === 'template') {
                $('.field-template_name').show();
            } else if (blockType === 'html') {
                $('.field-html_content').show();
            } else if (blockType === 'wysiwyg') {
                $('.field-wysiwyg_content').show();
            }
        }
        
        // Hide/show fields when the type changes
        $('#id_type').on('change', updateBlockTypeFields);
        
        // Initial setup on page load
        updateBlockTypeFields();
        
        // If settings are available, enhance the JSON field
        if ($('#id_settings').length) {
            // Set up a better interface for the settings field
            try {
                // Get initial value and try to parse it
                let settingsValue = $('#id_settings').val() || '{}';
                let settings = JSON.parse(settingsValue);
                
                // Format for better readability
                $('#id_settings').val(JSON.stringify(settings, null, 2));
            } catch (e) {
                console.error('Error parsing JSON settings:', e);
            }
        }
        
        // Helper function to validate JSON
        function isValidJSON(str) {
            try {
                JSON.parse(str);
                return true;
            } catch (e) {
                return false;
            }
        }
        
        // Add validation to settings field before form submission
        $('form').on('submit', function(e) {
            const settingsField = $('#id_settings');
            
            if (settingsField.length && settingsField.val().trim() !== '') {
                if (!isValidJSON(settingsField.val())) {
                    e.preventDefault();
                    alert('The settings field contains invalid JSON. Please correct it before saving.');
                    
                    // Highlight the field
                    settingsField.css('border-color', 'red');
                }
            }
        });
        
        setupTemplateSelect();

    });
})(django.jQuery);