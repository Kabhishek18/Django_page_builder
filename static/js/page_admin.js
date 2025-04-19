/**
 * Page Admin JavaScript
 * 
 * This script enhances the admin interface for Pages by:
 * - Auto-generating slugs
 * - Toggling visibility of sections
 * - Handling page settings JSON
 */
(function($) {
    "use strict";
    
    $(document).ready(function() {
        // Auto-generate slug from title if slug is empty
        $('#id_title').on('change keyup', function() {
            const slugField = $('#id_slug');
            
            // Only auto-generate if slug is empty
            if (!slugField.val()) {
                // Convert to lowercase, replace spaces with hyphens, remove special chars
                const slugValue = $(this).val()
                    .toLowerCase()
                    .replace(/\s+/g, '-')           // Replace spaces with -
                    .replace(/[^\w\-]+/g, '')       // Remove all non-word chars
                    .replace(/\-\-+/g, '-')         // Replace multiple - with single -
                    .replace(/^-+/, '')             // Trim - from start of text
                    .replace(/-+$/, '');            // Trim - from end of text
                
                slugField.val(slugValue);
            }
        });
        
        // Toggle sections based on parent fieldset's classes
        $('.collapse').each(function() {
            const $fieldset = $(this).closest('fieldset');
            const $legend = $fieldset.find('h2');
            
            // Make legend clickable to toggle collapse
            $legend.css('cursor', 'pointer');
            
            // Add indicators
            const $indicator = $('<span class="collapse-indicator">▼</span>');
            $legend.append($indicator);
            
            // Setup toggle behavior
            $legend.on('click', function() {
                const $content = $(this).parent().find('.collapse');
                $content.toggle();
                $indicator.text($content.is(':visible') ? '▼' : '►');
            });
        });
        
        // Helper function to validate JSON
        function isValidJSON(str) {
            try {
                JSON.parse(str);
                return true;
            } catch (e) {
                return false;
            }
        }
        
        // If page_settings_json field exists, enhance it
        if ($('#id_page_settings_json').length) {
            try {
                // Format for better readability
                let settingsValue = $('#id_page_settings_json').val() || '{}';
                let settings = JSON.parse(settingsValue);
                $('#id_page_settings_json').val(JSON.stringify(settings, null, 2));
            } catch (e) {
                console.error('Error parsing JSON settings:', e);
            }
            
            // Add validation before form submission
            $('form').on('submit', function(e) {
                const settingsField = $('#id_page_settings_json');
                
                if (settingsField.length && settingsField.val().trim() !== '') {
                    if (!isValidJSON(settingsField.val())) {
                        e.preventDefault();
                        alert('The page settings field contains invalid JSON. Please correct it before saving.');
                        settingsField.css('border-color', 'red');
                    }
                }
            });
        }
        
        // Show/hide menu_label field based on menu_placement
        function toggleMenuFields() {
            const menuPlacement = $('#id_menu_placement').val();
            const showMenuFields = menuPlacement !== 'none';
            
            if (showMenuFields) {
                $('.field-menu_label, .field-parent, .field-order').show();
            } else {
                $('.field-menu_label, .field-parent, .field-order').hide();
            }
        }
        
        $('#id_menu_placement').on('change', toggleMenuFields);
        toggleMenuFields(); // Initial call
        
        // Show/hide background_color field based on background_theme
        function toggleBackgroundColorField() {
            const backgroundTheme = $('#id_background_theme').val();
            if (backgroundTheme === 'custom') {
                $('.field-background_color').show();
            } else {
                $('.field-background_color').hide();
            }
        }
        
        $('#id_background_theme').on('change', toggleBackgroundColorField);
        toggleBackgroundColorField(); // Initial call
        
        // Show a preview URL for published pages
        const status = $('#id_status').val();
        const slug = $('#id_slug').val();
        
        if (status === 'published' && slug) {
            const previewUrl = '/' + slug + '/';
            $('.field-slug .help').append(
                ' <a href="' + previewUrl + '" target="_blank" class="viewsitelink">View page</a>'
            );
        }
    });
})(django.jQuery);