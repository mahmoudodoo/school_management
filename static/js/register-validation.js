// static/js/register-validation.js
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('register-form');
    
    if (form) {
        // Username validation
        const usernameInput = form.querySelector('input[name="username"]');
        const usernameError = document.getElementById('username-error');
        
        usernameInput.addEventListener('blur', function() {
            const value = this.value.trim();
            if (!value) {
                showError(usernameError, 'Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.');
            } else if (value.length > 150) {
                showError(usernameError, 'Username must be 150 characters or fewer.');
            } else if (!/^[\w.@+-]+$/.test(value)) {
                showError(usernameError, 'Enter a valid username. Letters, digits and @/./+/-/_ only.');
            } else {
                hideError(usernameError);
            }
        });
        
        // Email validation
        const emailInput = form.querySelector('input[name="email"]');
        const emailError = document.getElementById('email-error');
        
        emailInput.addEventListener('blur', function() {
            const value = this.value.trim();
            if (!value) {
                showError(emailError, 'Required. Enter a valid email address.');
            } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
                showError(emailError, 'Enter a valid email address.');
            } else {
                hideError(emailError);
            }
        });
        
        // Password1 validation
        const password1Input = form.querySelector('input[name="password1"]');
        const password1Error = document.getElementById('password1-error');
        
        password1Input.addEventListener('blur', function() {
            const value = this.value;
            if (!value) {
                showError(password1Error, 'Required.');
            } else if (value.length < 8) {
                showError(password1Error, 'Password must be at least 8 characters.');
            } else {
                hideError(password1Error);
            }
        });
        
        // Password2 validation
        const password2Input = form.querySelector('input[name="password2"]');
        const password2Error = document.getElementById('password2-error');
        
        password2Input.addEventListener('blur', function() {
            const value = this.value;
            const password1Value = password1Input.value;
            if (!value) {
                showError(password2Error, 'Required.');
            } else if (value !== password1Value) {
                showError(password2Error, 'Passwords do not match.');
            } else {
                hideError(password2Error);
            }
        });
        
        // Phone validation (optional)
        const phoneInput = form.querySelector('input[name="phone_number"]');
        const phoneError = document.getElementById('phone-error');
        
        if (phoneInput) {
            phoneInput.addEventListener('blur', function() {
                const value = this.value.trim();
                if (value && !/^\+?[\d\s-]+$/.test(value)) {
                    showError(phoneError, 'Enter a valid phone number.');
                } else {
                    hideError(phoneError);
                }
            });
        }
    }
    
    function showError(element, message) {
        if (element) {
            element.textContent = message;
            element.style.display = 'block';
            element.previousElementSibling.classList.add('error');
        }
    }
    
    function hideError(element) {
        if (element) {
            element.style.display = 'none';
            element.previousElementSibling.classList.remove('error');
        }
    }
});
