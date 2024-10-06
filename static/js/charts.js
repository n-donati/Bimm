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
async function loadData(recordId) {
    const response = await fetch(`/api/line-data/?record_id=${recordId}`);
    return await response.json();
}

// Main function to create or update the chart
async function createOrUpdateSmartChart(recordId) {
    try {
        // Load data from API
        const data = await loadData(recordId);
   
        // Extract and normalize data for x and y axes
        const normalizedData = data.map(entry => ({
            x: normalizeTime(entry.time),
            y: normalizeAmplitude(entry.amplitude)
        }));

        if (chartInstance) {
            // Update existing chart
            chartInstance.data.datasets[0].data = normalizedData;
            chartInstance.update();
        } else {
            // Create new chart
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
        }
    } catch (error) {
        console.error('Error creating/updating chart:', error);
    }
}

// Function to handle button clicks
function handleSelectButton(event) {
    if (event.target.classList.contains('select-record')) {
        const recordId = event.target.getAttribute('data-record-id');
        createOrUpdateSmartChart(recordId);
    }
}

// Set up event listeners when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Add click event listener to the table body
    document.querySelector('tbody').addEventListener('click', handleSelectButton);

    // Create initial chart with first record (if any)
    const firstSelectButton = document.querySelector('.select-record');
    if (firstSelectButton) {
        const firstRecordId = firstSelectButton.getAttribute('data-record-id');
        createOrUpdateSmartChart(firstRecordId);
    }
});