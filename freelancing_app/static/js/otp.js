document.addEventListener("DOMContentLoaded", function () {
    const otpInputs = document.querySelectorAll(".otp-box");
  
    otpInputs.forEach((input, index) => {
      input.addEventListener("input", (e) => {
        const value = e.target.value;
  
        // Move to the next input if a number is entered
        if (value && index < otpInputs.length - 1) {
          otpInputs[index + 1].focus();
        }
  
        // Restrict input to only numbers
        if (!/^\d$/.test(value)) {
          e.target.value = ""; // Clear invalid input
        }
      });
  
      input.addEventListener("keydown", (e) => {
        if (e.key === "Backspace" && !e.target.value && index > 0) {
          otpInputs[index - 1].focus(); // Move to the previous input on Backspace
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
  
