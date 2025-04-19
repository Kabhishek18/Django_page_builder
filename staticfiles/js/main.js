/**
 * Main JavaScript for Portfolio Website
 */
(function() {
    'use strict';
    
    // Initialize when DOM is fully loaded
    document.addEventListener('DOMContentLoaded', function() {
        // Handle mobile menu toggle
        setupMobileMenu();
        
        // Initialize Bootstrap components like tooltips
        initBootstrapComponents();
        
        // Handle forms with AJAX
        setupAjaxForms();
        
        // Set up scroll animations
        initScrollAnimations();
        
        // Set up any custom behavior for blocks
        initBlockFunctionality();
    });
    
    /**
     * Set up mobile menu toggle behavior
     */
    function setupMobileMenu() {
        // This is handled by Bootstrap's navbar-toggler, but we can add custom behavior here
        const mobileToggle = document.querySelector('.navbar-toggler');
        if (mobileToggle) {
            // Add any additional custom behavior for mobile menu
        }
    }
    
    /**
     * Initialize Bootstrap components
     */
    function initBootstrapComponents() {
        // Initialize tooltips
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
        
        // Initialize popovers
        var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    }
    
    /**
     * Set up AJAX form submissions to prevent page reloads
     */
    function setupAjaxForms() {
        // Find all forms with the ajax-form class
        const ajaxForms = document.querySelectorAll('form.ajax-form');
        
        ajaxForms.forEach(function(form) {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                
                // Get form data
                const formData = new FormData(form);
                
                // Submit form via AJAX
                fetch(form.action, {
                    method: form.method,
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    // Handle successful response
                    if (data.success) {
                        // Show success message
                        const messageElement = document.createElement('div');
                        messageElement.className = 'alert alert-success';
                        messageElement.textContent = data.message || 'Form submitted successfully';
                        
                        // Insert message before the form
                        form.parentNode.insertBefore(messageElement, form);
                        
                        // Reset form
                        form.reset();
                        
                        // Remove message after a delay
                        setTimeout(() => {
                            messageElement.remove();
                        }, 5000);
                    } else {
                        // Show error message
                        const messageElement = document.createElement('div');
                        messageElement.className = 'alert alert-danger';
                        messageElement.textContent = data.message || 'There was an error submitting the form';
                        
                        // Insert message before the form
                        form.parentNode.insertBefore(messageElement, form);
                        
                        // Remove message after a delay
                        setTimeout(() => {
                            messageElement.remove();
                        }, 5000);
                    }
                })
                .catch(error => {
                    console.error('Error submitting form:', error);
                    
                    // Show error message
                    const messageElement = document.createElement('div');
                    messageElement.className = 'alert alert-danger';
                    messageElement.textContent = 'There was an error submitting the form. Please try again.';
                    
                    // Insert message before the form
                    form.parentNode.insertBefore(messageElement, form);
                    
                    // Remove message after a delay
                    setTimeout(() => {
                        messageElement.remove();
                    }, 5000);
                });
            });
        });
    }
    
    /**
     * Initialize scroll animations for elements
     */
    function initScrollAnimations() {
        // Add animation classes when elements scroll into view
        const animatedElements = document.querySelectorAll('.animate-on-scroll');
        
        if (animatedElements.length > 0) {
            // Create intersection observer
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('animated');
                        // Unobserve after animation is triggered
                        observer.unobserve(entry.target);
                    }
                });
            }, {
                threshold: 0.1 // Trigger when 10% of the element is visible
            });
            
            // Observe all animated elements
            animatedElements.forEach(el => {
                observer.observe(el);
            });
        }
    }
    
    /**
     * Initialize functionality for specific block types
     */
    function initBlockFunctionality() {
        // Handle specific block types that need JavaScript interaction
        initCarouselBlocks();
        initTabBlocks();
        initGalleryBlocks();
    }
    
    /**
     * Initialize carousel blocks
     */
    function initCarouselBlocks() {
        // Bootstrap carousels are automatically initialized, but we can add custom behavior
        const carousels = document.querySelectorAll('.block-carousel .carousel');
        if (carousels.length > 0) {
            // Add any custom behavior for carousels
        }
    }
    
    /**
     * Initialize tab blocks
     */
    function initTabBlocks() {
        // Bootstrap tabs are automatically initialized, but we can add custom behavior
        const tabBlocks = document.querySelectorAll('.block-tabs');
        if (tabBlocks.length > 0) {
            // Add any custom behavior for tabs
        }
    }
    
    /**
     * Initialize gallery blocks
     */
    function initGalleryBlocks() {
        // Set up lightbox or other gallery functionality
        const galleries = document.querySelectorAll('.block-gallery');
        if (galleries.length > 0) {
            // Simple lightbox functionality
            const galleryItems = document.querySelectorAll('.gallery-item');
            
            galleryItems.forEach(item => {
                item.addEventListener('click', function(e) {
                    if (item.dataset.fullImage) {
                        e.preventDefault();
                        
                        // Create lightbox
                        const lightbox = document.createElement('div');
                        lightbox.className = 'lightbox';
                        lightbox.innerHTML = `
                            <div class="lightbox-content">
                                <img src="${item.dataset.fullImage}" alt="${item.querySelector('img').alt}">
                                <button class="lightbox-close">&times;</button>
                            </div>
                        `;
                        
                        // Add to body
                        document.body.appendChild(lightbox);
                        
                        // Prevent scroll
                        document.body.style.overflow = 'hidden';
                        
                        // Close on click
                        lightbox.addEventListener('click', function() {
                            document.body.removeChild(lightbox);
                            document.body.style.overflow = '';
                        });
                    }
                });
            });
        }
    }
})();