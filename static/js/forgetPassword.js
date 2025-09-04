document.addEventListener('DOMContentLoaded', function () {
    // Form elements
    const resetForm = document.getElementById('resetForm');
    const email = document.getElementById('email');
    const emailError = document.getElementById('emailError');

    // States
    const initialState = document.getElementById('initialState');
    const successState = document.getElementById('successState');
    const backToFormBtn = document.getElementById('backToFormBtn');

    // Form validation and submission
    resetForm.addEventListener('submit', function (e) {
        //e.preventDefault();
        let isValid = true;

        // Reset validation messages
        hideValidationMessage(emailError);

        // Validate email
        if (!isValidEmail(email.value)) {
            showValidationMessage(emailError, 'Please enter a valid email address');
            isValid = false;
        }

        if (isValid) {
            // Show success state
            initialState.style.display = 'none';
            successState.style.display = 'flex';

            // In a real application, you would submit the form to the server
            // and handle the password reset process
        }
    });

    // Back to form button
    backToFormBtn.addEventListener('click', function () {
        successState.style.display = 'none';
        initialState.style.display = 'flex';
        resetForm.reset();
    });

    // Input focus effects
    const inputs = document.querySelectorAll('.input');

    inputs.forEach(input => {
        input.addEventListener('focus', function () {
            this.parentElement.classList.add('focused');
        });

        input.addEventListener('blur', function () {
            this.parentElement.classList.remove('focused');
        });
    });

    // Helper functions
    function isValidEmail(email) {
        const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return re.test(String(email).toLowerCase());
    }

    function showValidationMessage(element, message) {
        element.textContent = message;
        element.style.display = 'block';
    }

    function hideValidationMessage(element) {
        element.style.display = 'none';
    }
});