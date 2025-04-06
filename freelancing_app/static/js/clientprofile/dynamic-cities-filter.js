document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form[data-cities-url]');
    
    forms.forEach(form => {
        const citiesUrl = form.dataset.citiesUrl;
        const countrySelect = form.querySelector('select[name="country"]');
        const citySelect = form.querySelector('select[name="city"]');
        
        if (!countrySelect || !citySelect) return; 
        
        const previousCity = citySelect.dataset.previousCity || '';
        
        countrySelect.addEventListener('change', function() {
            const countryId = this.value;
            console.log(`Form ID: ${form.id}, Selected country ID:`, countryId);
            
            citySelect.innerHTML = '<option value="" selected disabled>Loading cities...</option>';
            
            if (countryId) {
                const url = `${citiesUrl}?country_id=${countryId}`;
                
                fetch(url)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Network response was not ok');
                        }
                        return response.json();
                    })
                    .then(data => {
                        citySelect.innerHTML = '<option value="" selected disabled>Select your city</option>';
                        
                        if (data.cities && Array.isArray(data.cities)) {
                            data.cities.forEach(city => {
                                const option = document.createElement('option');
                                option.value = city.id;
                                option.textContent = city.name;
                                
                                if (city.id.toString() === previousCity) {
                                    option.selected = true;
                                }
                                
                                citySelect.appendChild(option);
                            });
                        } else {
                            console.warn('Received invalid cities data:', data);
                            citySelect.innerHTML = '<option value="" selected disabled>No cities available</option>';
                        }
                    })
                    .catch(error => {
                        console.error('Error fetching cities:', error);
                        citySelect.innerHTML = '<option value="" selected disabled>Error loading cities</option>';
                    });
            } else {
                citySelect.innerHTML = '<option value="" selected disabled>Select country first</option>';
            }
        });
        
        if (countrySelect.value) {
            countrySelect.dispatchEvent(new Event('change'));
        }
    });
});