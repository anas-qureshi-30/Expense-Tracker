document.addEventListener('DOMContentLoaded', function () {
    // Password visibility toggle
    const togglePassword = document.getElementById('togglePassword');
    const password = document.getElementById('password');

    togglePassword.addEventListener('click', function () {
        const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
        password.setAttribute('type', type);
        this.classList.toggle('fa-eye');
        this.classList.toggle('fa-eye-slash');
    });

    // Form validation
    const loginForm = document.getElementById('loginForm');
    const email = document.getElementById('email');

    const emailError = document.getElementById('emailError');
    const passwordError = document.getElementById('passwordError');

    loginForm.addEventListener('submit', function (e) {
        let isValid = true;

        // Reset validation messages
        hideValidationMessage(emailError);
        hideValidationMessage(passwordError);

        // Validate email
        if (!isValidEmail(email.value)) {
            showValidationMessage(emailError, 'Please enter a valid email address');
            isValid = false;
        }

        // Validate password
        if (password.value.trim() === '') {
            showValidationMessage(passwordError, 'Please enter your password');
            isValid = false;
        }

        if (!isValid) {
            e.preventDefault();
        } else {
            // Form is valid, you can submit it
            alert('Login successful!');
            // In a real application, you would submit the form to the server
        }
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