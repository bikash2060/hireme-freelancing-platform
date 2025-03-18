document.addEventListener("DOMContentLoaded", function () {
  const forms = document.querySelectorAll("form");

  forms.forEach(form => {
      const inputs = form.querySelectorAll("input");

      inputs.forEach(input => {
          input.addEventListener("keypress", function (event) {
              if (event.key === "Enter") {
                  event.preventDefault();
              }
          });
      });

      form.addEventListener("submit", function (event) {
          event.preventDefault();  
          form.submit();  
      });
  });

  if (window.history.replaceState) {
      window.history.replaceState(null, null, window.location.href);
  }
});
