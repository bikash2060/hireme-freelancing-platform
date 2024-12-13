document.addEventListener("DOMContentLoaded", function () {
    const otpInputs = document.querySelectorAll(".otp-box");
  
    otpInputs.forEach((input, index) => {
      input.addEventListener("input", (e) => {
        const value = e.target.value;
  
        if (value && index < otpInputs.length - 1) {
          otpInputs[index + 1].focus();
        }
  
        if (!/^\d$/.test(value)) {
          e.target.value = ""; 
        }
      });
  
      input.addEventListener("keydown", (e) => {
        if (e.key === "Backspace" && !e.target.value && index > 0) {
          otpInputs[index - 1].focus(); 
        }
      });
    });
  
    document.querySelector(".verify-btn").addEventListener("click", () => {
      const otpCode = Array.from(otpInputs)
        .map((input) => input.value)
        .join("");
  
      if (otpCode.length !== 6) {
        alert("Please enter a valid 6-digit OTP.");
      }
    });
  });
  
  const otpInputs = document.querySelectorAll('.otp-box');
  
  otpInputs.forEach(input => {
      input.addEventListener('input', function() {
          if (input.value.length === 1) {
              input.classList.add('filled');
          } else {
              input.classList.remove('filled');
          }
      });
  });
  