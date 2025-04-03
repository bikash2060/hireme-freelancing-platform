document.addEventListener('DOMContentLoaded', function() {
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not loaded');
        return;
    }

    const filterButtons = document.querySelectorAll('.filter-btn');
    const ctx = document.getElementById('progressChart');
    
    if (!ctx) {
        console.error('Canvas element not found');
        return;
    }

    console.log('Initial active button:', document.querySelector('.filter-btn.active'));

    const chartDataConfig = {
        week: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            current: [450, 600, 350, 700, 500, 300, 200],
            previous: [400, 550, 300, 650, 450, 250, 150],
            target: 500
        },
        month: {
            labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
            current: [1800, 2200, 2500, 2100],
            previous: [1500, 2000, 2300, 1900],
            target: 2000
        },
        year: {
            labels: ['Q1', 'Q2', 'Q3', 'Q4'],
            current: [8500, 9200, 8800, 9500],
            previous: [8000, 8500, 8200, 9000],
            target: 9000
        }
    };

    const progressChart = new Chart(ctx, {
        type: 'line',
        data: getChartData('week'),
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: '#1e293b',
                    titleFont: {
                        size: 14,
                        weight: 'bold'
                    },
                    bodyFont: {
                        size: 13
                    },
                    padding: 12,
                    cornerRadius: 8,
                    displayColors: true,
                    callbacks: {
                        label: function(context) {
                            const label = context.dataset.label || '';
                            const value = context.raw;
                            const formattedValue = `Rs ${value.toLocaleString('en-IN')}.00`;
                            
                            if (context.datasetIndex === 2) { 
                                return `${label}: ${formattedValue}`;
                            }
                            
                            return `${label}: ${formattedValue}`;
                        },
                        afterLabel: function(context) {
                            if (context.datasetIndex !== 0) return null;
                            
                            const activeButton = document.querySelector('.filter-btn.active');
                            if (!activeButton) return null;
                            
                            const period = activeButton.getAttribute('data-period');
                            const current = context.raw;
                            const prev = chartDataConfig[period].previous[context.dataIndex];
                            const target = chartDataConfig[period].target;
                            
                            const changeFromPrev = prev !== 0 ? ((current - prev) / prev * 100).toFixed(1) : 0;
                            const varianceFromTarget = current - target;
                            
                            return [
                                `Change from previous: ${changeFromPrev}%`,
                                `Variance from target: Rs ${Math.abs(varianceFromTarget).toLocaleString('en-IN')}.00 ${varianceFromTarget >= 0 ? 'above' : 'below'}`
                            ];
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    grid: {
                        color: 'rgba(241, 245, 249, 1)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#64748b',
                        callback: function(value) {
                            return `Rs ${value.toLocaleString('en-IN')}`;
                        }
                    }
                },
                x: {
                    grid: {
                        display: false,
                        drawBorder: false
                    },
                    ticks: {
                        color: '#64748b'
                    }
                }
            }
        }
    });

    function getChartData(period) {
        const data = chartDataConfig[period];
        const periodLabel = period === 'week' ? 'Week' : period === 'month' ? 'Month' : 'Year';
        
        return {
            labels: data.labels,
            datasets: [
                {
                    label: `Current ${periodLabel}`,
                    data: data.current,
                    backgroundColor: 'rgba(79, 70, 229, 0.1)',
                    borderColor: 'rgba(79, 70, 229, 1)',
                    borderWidth: 3,
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: '#4f46e5',
                    pointBorderColor: '#fff'
                },
                {
                    label: `Previous ${periodLabel}`,
                    data: data.previous,
                    backgroundColor: 'rgba(199, 210, 254, 0.1)',
                    borderColor: 'rgba(199, 210, 254, 1)',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: false,
                    borderDash: [5, 5],
                    pointBackgroundColor: '#c7d2fe',
                    pointBorderColor: '#fff'
                },
                {
                    label: 'Target',
                    data: Array(data.labels.length).fill(data.target),
                    borderColor: '#10b981',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    backgroundColor: 'transparent',
                    pointRadius: 0,
                    pointHoverRadius: 0
                }
            ]
        };
    }

    function updateProgressData(period) {
        console.log('Updating chart with period:', period);
        progressChart.data = getChartData(period);
        progressChart.update();
    }

    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            console.log('Filter button clicked:', this.getAttribute('data-period'));
            
            filterButtons.forEach(btn => {
                btn.classList.remove('active');
                console.log('Removed active from:', btn.getAttribute('data-period'));
            });
            
            this.classList.add('active');
            console.log('Added active to:', this.getAttribute('data-period'));
            
            console.log('Current active button:', document.querySelector('.filter-btn.active'));
            
            updateProgressData(this.getAttribute('data-period'));
        });
    });

    updateProgressData('week');
});