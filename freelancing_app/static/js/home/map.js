document.addEventListener('DOMContentLoaded', function() {
    const mapTabs = document.querySelectorAll('.map-tab');
    const officeMap = document.getElementById('office-map');
    
    mapTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            mapTabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            const mapType = this.getAttribute('data-map-type');
            const currentSrc = officeMap.src;
            const newSrc = mapType === 'satellite' 
                ? currentSrc.replace('!1m18!1m12', '!1m18!1m12!3m2!1d27.7050104!2d85.3226595!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0x0!2zMjfCsDQyJzE4LjAiTiA4NcKwMTknMjEuNiJF!5e0!3m2!1sen!2snp!4v1620000000000')
                : 'https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3532.456715090843!2d85.32047091506203!3d27.70501038279393!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x39eb19a64b5f13e1%3A0x28b2d0eacda46b98!2sHireMe%20Nepal%20Pvt.%20Ltd.%2C%20Baneshwor%2C%20Kathmandu%2044600!5e0!3m2!1sen!2snp!4v1620000000000!5m2!1sen!2snp';
            
            officeMap.src = newSrc;
        });
    });
    
    document.getElementById('get-directions').addEventListener('click', function() {
        window.open('https://www.google.com/maps/dir//HireMe+Nepal+Pvt.+Ltd.,+Baneshwor,+Kathmandu/@27.7050104,85.3226595,17z/data=!4m8!4m7!1m0!1m5!1m1!1s0x39eb19a64b5f13e1:0x28b2d0eacda46b98!2m2!1d85.3226595!2d27.7050104', '_blank');
    });
    
    document.getElementById('save-location').addEventListener('click', function() {
        alert('Location saved to your favorites!');
    });
    
    document.getElementById('book-appointment').addEventListener('click', function() {
        window.location.href = '/book-appointment';
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const overlay = document.querySelector('.map-overlay');
    const toggleButton = document.querySelector('.overlay-toggle');
    
    if (toggleButton) {
        toggleButton.addEventListener('click', function() {
            overlay.classList.toggle('collapsed');
            
            const isCollapsed = overlay.classList.contains('collapsed');
            toggleButton.setAttribute('aria-label', 
                isCollapsed ? 'Show contact information' : 'Hide contact information');
        });
    }
});