// Global variable to store the chart instance
let chartInstance = null;

// Function to normalize time string to Date object
function normalizeTime(timeString) {
    return new Date(timeString);
}

// Function to normalize amplitude to a number
function normalizeAmplitude(amplitudeString) {
    return parseFloat(amplitudeString);
}

// Function to load data from API
async function loadData() {
    const response = await fetch('/api/line-data/?record_id=1');
    return await response.json();
}

// Main function to create the chart
async function createSmartChart() {
    try {
        // Destroy existing chart if it exists
        if (chartInstance) {
            chartInstance.destroy();
        }

        // Load data from API
        const data = await loadData();
   
        // Extract and normalize data for x and y axes
        const normalizedData = data.map(entry => ({
            x: normalizeTime(entry.time),
            y: normalizeAmplitude(entry.amplitude)
        }));

        // Create the chart
        const ctx = document.getElementById('chartBig1');
        const config = {
            type: 'line',
            data: {
                datasets: [{
                    label: 'Amplitude vs Time',
                    data: normalizedData,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderWidth: 1,
                    pointRadius: 0,
                    fill: false,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Amplitude vs Time Chart'
                    }
                },
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'second',
                            displayFormats: {
                                second: 'HH:mm:ss.SSS'
                            }
                        },
                        title: {
                            display: true,
                            text: 'Time'
                        }
                    },
                    y: {
                        type: 'linear',
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Amplitude'
                        },
                        ticks: {
                            callback: function(value) {
                                return value.toExponential(2);
                            }
                        }
                    }
                }
            },
        };
   
        chartInstance = new Chart(ctx, config);
    } catch (error) {
        console.error('Error creating chart:', error);
    }
}

// Call this function when the DOM is loaded
document.addEventListener('DOMContentLoaded', createSmartChart);