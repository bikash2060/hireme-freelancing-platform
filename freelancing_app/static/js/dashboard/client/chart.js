// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Get the canvas element
    const ctx = document.getElementById('clientProgressChart').getContext('2d');

    // Sample data - In a real application, this would come from your backend
    const data = {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        datasets: [
            {
                label: 'Budget',
                data: [25000, 30000, 35000, 40000, 45000, 50000],
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                tension: 0.4,
                fill: true
            },
            {
                label: 'Actual',
                data: [22000, 28000, 32000, 38000, 42000, 48000],
                borderColor: 'rgba(255, 99, 132, 1)',
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                tension: 0.4,
                fill: true
            }
        ]
    };

    // Chart configuration
    const config = {
        type: 'line',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false, // We're using custom legend in HTML
                    position: 'top',
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: Rs ${context.parsed.y.toLocaleString()}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return 'Rs ' + value.toLocaleString();
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            }
        }
    };

    // Create the chart
    const clientProgressChart = new Chart(ctx, config);

    // Add event listeners for time filter buttons
    const filterButtons = document.querySelectorAll('.filter-btn');
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove active class from all buttons
            filterButtons.forEach(btn => btn.classList.remove('active'));
            // Add active class to clicked button
            this.classList.add('active');
            
            // In a real application, you would fetch new data based on the selected period
            // and update the chart accordingly
            const period = this.dataset.period;
            updateChartData(period);
        });
    });

    // Function to update chart data based on selected period
    function updateChartData(period) {
        // This is a placeholder - in a real application, you would fetch new data from your backend
        // based on the selected period
        let newData;
        switch(period) {
            case 'week':
                newData = {
                    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                    datasets: [
                        {
                            label: 'Budget',
                            data: [5000, 6000, 7000, 8000, 9000, 10000, 11000],
                            borderColor: 'rgba(75, 192, 192, 1)',
                            backgroundColor: 'rgba(75, 192, 192, 0.2)',
                            tension: 0.4,
                            fill: true
                        },
                        {
                            label: 'Actual',
                            data: [4500, 5500, 6500, 7500, 8500, 9500, 10500],
                            borderColor: 'rgba(255, 99, 132, 1)',
                            backgroundColor: 'rgba(255, 99, 132, 0.2)',
                            tension: 0.4,
                            fill: true
                        }
                    ]
                };
                break;
            case 'month':
                newData = {
                    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                    datasets: [
                        {
                            label: 'Budget',
                            data: [10000, 15000, 20000, 25000],
                            borderColor: 'rgba(75, 192, 192, 1)',
                            backgroundColor: 'rgba(75, 192, 192, 0.2)',
                            tension: 0.4,
                            fill: true
                        },
                        {
                            label: 'Actual',
                            data: [9000, 14000, 19000, 24000],
                            borderColor: 'rgba(255, 99, 132, 1)',
                            backgroundColor: 'rgba(255, 99, 132, 0.2)',
                            tension: 0.4,
                            fill: true
                        }
                    ]
                };
                break;
            case 'year':
                newData = data; // Use the original yearly data
                break;
        }

        // Update the chart with new data
        clientProgressChart.data = newData;
        clientProgressChart.update();
    }
});
