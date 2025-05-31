document.addEventListener('DOMContentLoaded', function() {
    const paymentForm = document.getElementById('paymentForm');
    if (paymentForm) {
        paymentForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(paymentForm);
            const paymentMethod = formData.get('payment_method');
            
            if (paymentMethod === 'esewa') {
                // Show loading state
                const payButton = document.getElementById('payButton');
                payButton.disabled = true;
                payButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
                
                // Submit form to backend
                fetch(paymentForm.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        console.log('Debug - eSewa Form Data:', data.form_data);  // Debug log
                        
                        // Create and submit eSewa form
                        const esewaForm = document.createElement('form');
                        esewaForm.method = 'POST';
                        esewaForm.action = data.redirect_url;
                        
                        // Add form fields
                        for (const [key, value] of Object.entries(data.form_data)) {
                            console.log(`Debug - Adding field: ${key}=${value}`);  // Debug log
                            const input = document.createElement('input');
                            input.type = 'text';
                            input.name = key;
                            input.value = value;
                            input.required = true;
                            esewaForm.appendChild(input);
                        }
                        
                        // Add form to document and submit
                        document.body.appendChild(esewaForm);
                        console.log('Debug - Submitting form to:', data.redirect_url);  // Debug log
                        esewaForm.submit();
                    } else {
                        throw new Error('Payment processing failed');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Payment processing failed. Please try again.');
                    payButton.disabled = false;
                    payButton.innerHTML = '<i class="fas fa-lock"></i> Pay Now';
                });
            } else {
                // For other payment methods, submit the form normally
                paymentForm.submit();
            }
        });
    }
}); 