// Chart 1
const ctx1 = document.getElementById('myChart');

// Create an array of numbers from 1 to 1000 for the x-axis
const labels1 = Array.from({ length: 1000 }, (_, i) => i + 1); // 1000 points for smoother transitions

// Function to generate a realistic sound wave pattern with randomized peaks
function generateSoundWave(length, baseAmplitude, frequency) {
    const data = [];
    for (let i = 0; i < length; i++) {
        // Create a variable amplitude to simulate sound dynamics
        const amplitude = baseAmplitude * (Math.random() * 0.5 + 0.5); // Amplitude varies between 50% and 100%
        const x = (i / frequency) * (Math.PI * 2); // Adjust frequency
        const y = amplitude * Math.sin(x); // Generate wave points
        data.push(y);
    }
    return data;
}

// Generate sound wave data
const waveData = generateSoundWave(1000, 100, 5); // Use the function to generate sound wave data

const data1 = {
    labels: labels1,
    datasets: [
        {
            label: 'Sound Wave',
            data: [], // Start with an empty data array
            borderColor: 'rgba(255, 99, 132, 1)', // Red color
            backgroundColor: 'rgba(255, 99, 132, 0.5)', // Transparent red color
            tension: 0.2, // Tension for rounded vertices
            borderWidth: 2, // Thicker line for better visibility
        },
    ]
};

const config1 = {
    type: 'line',
    data: data1,
    options: {
        responsive: true,
        plugins: {
            legend: {
                position: 'top',
            },
            title: {
                display: true,
                text: 'Simulated Sound Wave'
            }
        },
        scales: {
            y: {
                beginAtZero: false // Allow negative values for wave effect
            }
        },
    },
};

const myChart1 = new Chart(ctx1, config1);

// Animation function to progressively add data points
function animateChart() {
    let index = 0; // Start at the first point
    const interval = setInterval(() => {
        if (index < waveData.length) {
            // Add the next point to the dataset
            data1.datasets[0].data.push(waveData[index]);
            myChart1.update(); // Update the chart
            index++;
        } else {
            clearInterval(interval); // Stop the animation when all points are added
        }
    }, 5); // Adjust the interval timing for speed
}

// Start the animation
animateChart();
