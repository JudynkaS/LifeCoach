document.addEventListener('DOMContentLoaded', function() {
    // Handle Other referral source input visibility
    const referralOptions = document.querySelectorAll('input[name="referral_source"]');
    const otherInput = document.querySelector('.other-referral-input');
    
    function toggleOtherInput() {
        const otherChecked = Array.from(referralOptions).some(input => 
            input.checked && input.value === 'other'
        );
        otherInput.classList.toggle('show', otherChecked);
    }

    referralOptions.forEach(option => {
        option.addEventListener('change', toggleOtherInput);
    });

    // Initial check
    toggleOtherInput();

    // Form validation
    const form = document.querySelector('.signup-form');
    form.addEventListener('submit', function(event) {
        if (!form.checkValidity()) {
            event.preventDefault();
            event.stopPropagation();
        }
        form.classList.add('was-validated');
    });
}); 