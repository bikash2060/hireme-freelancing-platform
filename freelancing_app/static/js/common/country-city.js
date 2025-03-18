document.addEventListener("DOMContentLoaded", function () {
    const countrySelect = document.getElementById("country");
    const citySelect = document.getElementById("city");

    const citiesByCountry = JSON.parse('{{ countries_and_cities_json|safe }}');  

    function populateCities(country) {
        citySelect.innerHTML = "<option value=''>Select a city</option>";
        if (citiesByCountry[country]) {
            citiesByCountry[country].forEach(city => {
                const option = document.createElement("option");
                option.value = city;
                option.textContent = city;
                if (city === "{{ client.city }}") {
                    option.selected = true;
                }
                citySelect.appendChild(option);
            });
        }
    }

    const preSelectedCountry = countrySelect.value;
    if (preSelectedCountry) {
        populateCities(preSelectedCountry);
    }

    countrySelect.addEventListener("change", function () {
        const selectedCountry = this.value;
        populateCities(selectedCountry);
    });
});
