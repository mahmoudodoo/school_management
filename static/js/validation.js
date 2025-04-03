// static/js/validation.js
document.addEventListener('DOMContentLoaded', function() {
    // Add real-time validation for all forms with input fields
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
        
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
            
            // For better UX, validate on input change after first blur
            input.addEventListener('input', function() {
                if (this.dataset.touched === 'true') {
                    validateField(this);
                }
            });
            
            input.addEventListener('focus', function() {
                this.dataset.touched = 'true';
            });
        });
    });
    
    function validateField(field) {
        const errorElement = document.getElementById(`${field.name}-error`) || 
                            field.nextElementSibling?.classList.contains('error-message') ? 
                            field.nextElementSibling : null;
        
        if (!field.checkValidity()) {
            showError(field, errorElement, field.validationMessage);
        } else {
            hideError(field, errorElement);
        }
    }
    
    function showError(field, errorElement, message) {
        field.classList.add('error');
        if (errorElement) {
            errorElement.textContent = message || 'This field is required.';
            errorElement.style.display = 'block';
        }
    }
    
    function hideError(field, errorElement) {
        field.classList.remove('error');
        if (errorElement) {
            errorElement.style.display = 'none';
        }
    }
});
