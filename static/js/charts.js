// Function to parse CSV data
function parseCSV(csv) {
    const lines = csv.trim().split('\n');
    const headers = lines[0].split(',').map(header => header.trim());
    return lines.slice(1).map(line => {
        const values = line.split(',');
        return headers.reduce((obj, header, index) => {
            obj[header] = values[index].trim();
            return obj;
        }, {});
    });
}

// Function to load CSV file
async function loadCSV(url) {
    const response = await fetch(url);
    const csv = await response.text();
    return parseCSV(csv);
}

// Function to determine chart type and parameters
function determineChartParameters(data) {
    const numericColumns = Object.keys(data[0]).filter(key => !isNaN(parseFloat(data[0][key])));
    const timeColumn = numericColumns.find(col => col.toLowerCase().includes('time') || col.toLowerCase().includes('date'));
    const valueColumn = numericColumns.find(col => col !== timeColumn);

    return {
        xAxis: timeColumn || numericColumns[0],
        yAxis: valueColumn || numericColumns[1],
        chartType: timeColumn ? 'line' : 'scatter'
    };
}

// Main function to create the chart
async function createSmartChart(csvUrl) {
    // Load CSV data
    const data = await loadCSV(csvUrl);
    
    // Determine chart parameters
    const { xAxis, yAxis, chartType } = determineChartParameters(data);
    
    // Extract data for x and y axes
    const xData = data.map(entry => parseFloat(entry[xAxis]));
    const yData = data.map(entry => parseFloat(entry[yAxis]));

    // Create the chart
    const ctx = document.getElementById('chartBig1');
    const config = {
        type: chartType,
        data: {
            labels: xData,
            datasets: [{
                label: `${yAxis} vs ${xAxis}`,
                data: yData,
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderWidth: 2,
                pointRadius: 5,
                fill: false,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: `${yAxis} vs ${xAxis} Chart`
                }
            },
            scales: {
                x: {
                    type: 'linear',
                    position: 'bottom',
                    title: {
                        display: true,
                        text: xAxis
                    }
                },
                y: {
                    type: 'linear',
                    position: 'left',
                    title: {
                        display: true,
                        text: yAxis
                    }
                }
            }
        },
    };
    
    const myChart = new Chart(ctx, config);
    window.addEventListener('resize', function() {
        myChart.resize();
    });
}