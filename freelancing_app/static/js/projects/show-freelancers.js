document.getElementById("toggle-freelancers").addEventListener("click", function() {
    var freelancersSection = document.getElementById("freelancers-section");
    if (freelancersSection.style.display === "none") {
        freelancersSection.style.display = "block";
        this.textContent = "Hide Other Freelancers"; 
    } else {
        freelancersSection.style.display = "none";
        this.textContent = "Show Other Freelancers"; 
    }
});