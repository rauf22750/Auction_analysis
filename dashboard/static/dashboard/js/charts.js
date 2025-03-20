/**
 * Charts utility functions for the Auction Analysis Dashboard
 */

/**
 * Creates a line chart with the given data
 * @param {string} elementId - The ID of the canvas element
 * @param {Array} data - The data to display
 * @param {string} labelKey - The key in the data objects to use for labels
 * @param {Array} datasets - Array of dataset configurations
 */
function createLineChart(elementId, data, labelKey, datasets) {
    const ctx = document.getElementById(elementId).getContext('2d');
    
    const chartData = {
        labels: data.map(item => item[labelKey]),
        datasets: datasets.map(dataset => ({
            label: dataset.label,
            data: data.map(item => item[dataset.key]),
            borderColor: dataset.color,
            backgroundColor: dataset.bgColor || 'transparent',
            tension: 0.1,
            pointRadius: 3,
            pointHoverRadius: 5
        }))
    };
    
    new Chart(ctx, {
        type: 'line',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                }
            },
            plugins: {
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(0, 0, 0, 0.7)',
                    padding: 10,
                    cornerRadius: 4,
                    titleFont: {
                        size: 14
                    },
                    bodyFont: {
                        size: 13
                    }
                },
                legend: {
                    position: 'top',
                    labels: {
                        padding: 20,
                        boxWidth: 15,
                        usePointStyle: true
                    }
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            }
        }
    });
}

/**
 * Creates a bar chart with the given data
 * @param {string} elementId - The ID of the canvas element
 * @param {Array} data - The data to display
 * @param {string} labelKey - The key in the data objects to use for labels
 * @param {Array} datasets - Array of dataset configurations
 * @param {Function} labelFormatter - Optional function to format labels
 */
function createBarChart(elementId, data, labelKey, datasets, labelFormatter) {
    const ctx = document.getElementById(elementId).getContext('2d');
    
    const chartData = {
        labels: data.map(item => labelFormatter ? labelFormatter(item[labelKey]) : item[labelKey]),
        datasets: datasets.map(dataset => ({
            label: dataset.label,
            data: data.map(item => item[dataset.key]),
            backgroundColor: dataset.color,
            borderColor: dataset.borderColor || 'transparent',
            borderWidth: 1
        }))
    };
    
    new Chart(ctx, {
        type: 'bar',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
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
            plugins: {
                tooltip: {
                    mode: 'index',
                    intersect: false
                },
                legend: {
                    position: 'top'
                }
            }
        }
    });
}

/**
 * Creates a stacked bar chart with the given data
 * @param {string} elementId - The ID of the canvas element
 * @param {Array} data - The data to display
 * @param {string} labelKey - The key in the data objects to use for labels
 * @param {Array} datasets - Array of dataset configurations
 * @param {Function} labelFormatter - Optional function to format labels
 */
function createStackedBarChart(elementId, data, labelKey, datasets, labelFormatter) {
    const ctx = document.getElementById(elementId).getContext('2d');
    
    const chartData = {
        labels: data.map(item => labelFormatter ? labelFormatter(item[labelKey]) : item[labelKey]),
        datasets: datasets.map(dataset => ({
            label: dataset.label,
            data: data.map(item => item[dataset.key]),
            backgroundColor: dataset.color,
            borderColor: dataset.borderColor || 'transparent',
            borderWidth: 1
        }))
    };
    
    new Chart(ctx, {
        type: 'bar',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    stacked: true,
                    grid: {
                        display: false
                    }
                },
                y: {
                    stacked: true,
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                }
            },
            plugins: {
                tooltip: {
                    mode: 'index',
                    intersect: false
                },
                legend: {
                    position: 'top'
                }
            }
        }
    });
}

/**
 * Creates a pie chart with the given data
 * @param {string} elementId - The ID of the canvas element
 * @param {Array} data - The data to display
 * @param {string} labelKey - The key in the data objects to use for labels
 * @param {string} dataKey - The key in the data objects to use for values
 * @param {Array} colors - Array of colors for the pie slices
 */
function createPieChart(elementId, data, labelKey, dataKey, colors) {
    const ctx = document.getElementById(elementId).getContext('2d');
    
    const chartData = {
        labels: data.map(item => item[labelKey]),
        datasets: [{
            data: data.map(item => item[dataKey]),
            backgroundColor: colors || [
                'rgba(54, 162, 235, 0.7)',
                'rgba(255, 99, 132, 0.7)',
                'rgba(255, 206, 86, 0.7)',
                'rgba(75, 192, 192, 0.7)',
                'rgba(153, 102, 255, 0.7)',
                'rgba(255, 159, 64, 0.7)',
                'rgba(199, 199, 199, 0.7)',
                'rgba(83, 102, 255, 0.7)',
                'rgba(40, 159, 64, 0.7)',
                'rgba(210, 199, 199, 0.7)'
            ],
            borderWidth: 1
        }]
    };
    
    new Chart(ctx, {
        type: 'pie',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}