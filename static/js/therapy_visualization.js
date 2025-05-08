/**
 * Therapy Visualization JavaScript
 * Handles visualization of therapy recommendations and card interactions
 */

/**
 * Initialize the therapy comparison chart
 * @param {Array} therapyData - Array of therapy recommendations
 */
function initTherapyComparisonChart(therapyData) {
    // If no therapy data or Chart not available, return
    if (!therapyData || therapyData.length === 0 || typeof Chart === 'undefined') {
        console.warn('No therapy data available or Chart.js not loaded');
        return;
    }

    // Check if we have a canvas element
    const ctx = document.getElementById('therapyComparisonChart');
    if (!ctx) {
        console.warn('Chart canvas element not found');
        return;
    }

    // Extract therapy names and scores
    const labels = therapyData.map(therapy => {
        // Truncate long therapy names
        let name = therapy.therapy_name;
        if (name.length > 20) {
            name = name.substring(0, 17) + '...';
        }
        return `${name} (${therapy.therapy_type})`;
    });

    const efficacyScores = therapyData.map(therapy => therapy.efficacy_score);
    const compatibilityScores = therapyData.map(therapy => therapy.compatibility_score);
    const safetyScores = therapyData.map(therapy => therapy.safety_score);
    const costScores = therapyData.map(therapy => therapy.cost_score);

    // Determine if dark mode is active
    const isDarkMode = document.body.classList.contains('dark-mode');
    const textColor = isDarkMode ? '#ffffff' : '#12263f';
    const gridColor = isDarkMode ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)';

    // Create the chart
    const chart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Efficacy',
                    data: efficacyScores,
                    backgroundColor: 'rgba(0, 184, 169, 0.2)',
                    borderColor: 'rgb(0, 184, 169)',
                    pointBackgroundColor: 'rgb(0, 184, 169)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgb(0, 184, 169)'
                },
                {
                    label: 'Compatibility',
                    data: compatibilityScores,
                    backgroundColor: 'rgba(57, 160, 237, 0.2)',
                    borderColor: 'rgb(57, 160, 237)',
                    pointBackgroundColor: 'rgb(57, 160, 237)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgb(57, 160, 237)'
                },
                {
                    label: 'Safety',
                    data: safetyScores,
                    backgroundColor: 'rgba(246, 201, 14, 0.2)',
                    borderColor: 'rgb(246, 201, 14)',
                    pointBackgroundColor: 'rgb(246, 201, 14)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgb(246, 201, 14)'
                },
                {
                    label: 'Cost',
                    data: costScores,
                    backgroundColor: 'rgba(44, 123, 229, 0.2)',
                    borderColor: 'rgb(44, 123, 229)',
                    pointBackgroundColor: 'rgb(44, 123, 229)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgb(44, 123, 229)'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    min: 0,
                    max: 100,
                    ticks: {
                        stepSize: 20,
                        color: isDarkMode ? '#95aac9' : '#95aac9'
                    },
                    grid: {
                        color: gridColor
                    },
                    angleLines: {
                        color: gridColor
                    },
                    pointLabels: {
                        color: textColor,
                        font: {
                            size: 12
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: textColor,
                        font: {
                            size: 12
                        },
                        boxWidth: 15,
                        padding: 15
                    }
                },
                tooltip: {
                    backgroundColor: isDarkMode ? '#283142' : '#ffffff',
                    titleColor: isDarkMode ? '#ffffff' : '#12263f',
                    bodyColor: isDarkMode ? '#ffffff' : '#12263f',
                    borderColor: isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)',
                    borderWidth: 1,
                    padding: 10,
                    boxPadding: 5,
                    usePointStyle: true,
                    callbacks: {
                        title: function(tooltipItems) {
                            const idx = tooltipItems[0].dataIndex;
                            return therapyData[idx].therapy_name;
                        },
                        label: function(context) {
                            const label = context.dataset.label || '';
                            return `${label}: ${context.raw}/100`;
                        }
                    }
                }
            }
        }
    });

    // Store the chart instance for potential reuse or updates
    window.therapyComparisonChart = chart;
}

/**
 * Initialize score circles with animation
 */
function initScoreCircles() {
    const scoreCircles = document.querySelectorAll('.score-circle');
    
    scoreCircles.forEach(circle => {
        const score = parseFloat(circle.getAttribute('data-score'));
        
        // Calculate the percentage of the circle to fill (based on score out of 100)
        const percentage = score / 100;
        
        // Calculate the clip-path based on the percentage
        animateScoreCircle(circle, percentage);
        
        // Also update the circle color based on the score
        updateScoreCircleColor(circle, score);
    });
}

/**
 * Animate the score circle filling effect
 * @param {HTMLElement} circle - The score circle element
 * @param {number} targetPercentage - The percentage to fill (0-1)
 */
function animateScoreCircle(circle, targetPercentage) {
    // Start from 0
    let currentPercentage = 0;
    
    // Get the before pseudo-element for the clip-path
    const circleBeforePseudo = circle.querySelector('::before');
    
    // Animation duration in ms
    const duration = 1000;
    const fps = 60;
    const frameDuration = 1000 / fps;
    const frames = duration / frameDuration;
    const increment = targetPercentage / frames;
    
    // Animate the fill using requestAnimationFrame for smooth animation
    function animate() {
        if (currentPercentage < targetPercentage) {
            currentPercentage += increment;
            
            if (currentPercentage > targetPercentage) {
                currentPercentage = targetPercentage;
            }
            
            updateScoreCircleFill(circle, currentPercentage);
            requestAnimationFrame(animate);
        }
    }
    
    // Start the animation
    requestAnimationFrame(animate);
}

/**
 * Update the score circle fill based on percentage
 * @param {HTMLElement} circle - The score circle element
 * @param {number} percentage - The percentage to fill (0-1)
 */
function updateScoreCircleFill(circle, percentage) {
    // Calculate the clip-path polygon points for the circle fill
    // This is a complex calculation to create a circular reveal effect
    // For simplicity, we'll use a basic approach with conic-gradient
    
    const degrees = percentage * 360;
    circle.style.background = `conic-gradient(var(--primary-color) ${degrees}deg, transparent 0deg)`;
}

/**
 * Update the score circle color based on the score value
 * @param {HTMLElement} circle - The score circle element
 * @param {number} score - The score value (0-100)
 */
function updateScoreCircleColor(circle, score) {
    let color;
    
    // Color scale based on score range
    if (score >= 90) {
        color = 'var(--success-color)';  // Excellent
    } else if (score >= 75) {
        color = '#4cc9f0';  // Good
    } else if (score >= 60) {
        color = 'var(--primary-color)';  // Average
    } else if (score >= 40) {
        color = 'var(--warning-color)';  // Below average
    } else {
        color = 'var(--danger-color)';  // Poor
    }
    
    // Update the before element's border color
    // Since we can't directly modify pseudo-elements with JS,
    // we'll add a custom property to the element that the CSS can use
    circle.style.setProperty('--score-color', color);
    
    // For the demo, we'll directly set the border color of the circle
    circle.style.borderColor = color;
}

/**
 * Initialize therapy card interactions
 */
document.addEventListener('DOMContentLoaded', function() {
    // Add click event listeners to all detail toggles
    const detailToggles = document.querySelectorAll('.details-toggle');
    
    detailToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            // Toggle the icon rotation
            const icon = this.querySelector('i');
            icon.classList.toggle('rotate-180');
            
            // Get the target collapse element ID
            const targetId = this.getAttribute('data-bs-target');
            const targetElement = document.querySelector(targetId);
            
            // If bootstrap is available, it will handle the collapse
            // If not, we'll handle it manually
            if (!window.bootstrap) {
                if (targetElement) {
                    targetElement.classList.toggle('show');
                }
            }
        });
    });
    
    // Set up therapy card hover interactions
    const therapyCards = document.querySelectorAll('.therapy-card');
    
    therapyCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.classList.add('active-card');
        });
        
        card.addEventListener('mouseleave', function() {
            this.classList.remove('active-card');
        });
    });
    
    // Export button functionality
    const exportButton = document.getElementById('exportResults');
    if (exportButton) {
        exportButton.addEventListener('click', exportTherapyResults);
    }
});

/**
 * Export therapy results as PDF
 * This function would be connected to the API in a full implementation
 */
function exportTherapyResults() {
    // Show a loading indicator
    showNotification('Preparing your report...', 'info');
    
    // Simulate API call delay
    setTimeout(() => {
        // In a real implementation, this would call the API to generate a PDF
        // For this demo, we'll just show a success message
        fetch('/api/export-report', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                therapies: window.therapyData || []
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('Report exported successfully!', 'success');
            } else {
                showNotification(`Error exporting report: ${data.error}`, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Failed to export report. Please try again.', 'error');
        });
    }, 1000);
}

/**
 * Create a bar chart comparing the overall scores of therapies
 * @param {Array} therapyData - Array of therapy recommendations
 */
function createOverallScoreChart(therapyData) {
    if (!therapyData || therapyData.length === 0 || typeof Chart === 'undefined') {
        return;
    }
    
    const ctx = document.getElementById('overallScoreChart');
    if (!ctx) return;
    
    // Extract therapy names and overall scores
    const labels = therapyData.map(therapy => {
        let name = therapy.therapy_name;
        if (name.length > 15) {
            name = name.substring(0, 12) + '...';
        }
        return name;
    });
    
    const overallScores = therapyData.map(therapy => therapy.overall_score);
    
    // Create color arrays based on therapy types
    const backgroundColors = therapyData.map(therapy => 
        therapy.therapy_type === 'allopathy' ? 'rgba(67, 97, 238, 0.7)' : 'rgba(63, 143, 104, 0.7)'
    );
    
    const borderColors = therapyData.map(therapy => 
        therapy.therapy_type === 'allopathy' ? 'rgb(67, 97, 238)' : 'rgb(63, 143, 104)'
    );
    
    // Determine if dark mode is active
    const isDarkMode = document.body.classList.contains('dark-mode');
    const textColor = isDarkMode ? '#ffffff' : '#12263f';
    const gridColor = isDarkMode ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)';
    
    // Create the chart
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Overall Score',
                data: overallScores,
                backgroundColor: backgroundColors,
                borderColor: borderColors,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        color: isDarkMode ? '#95aac9' : '#95aac9'
                    },
                    grid: {
                        color: gridColor
                    }
                },
                x: {
                    ticks: {
                        color: isDarkMode ? '#95aac9' : '#95aac9'
                    },
                    grid: {
                        color: gridColor
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: isDarkMode ? '#283142' : '#ffffff',
                    titleColor: isDarkMode ? '#ffffff' : '#12263f',
                    bodyColor: isDarkMode ? '#ffffff' : '#12263f',
                    borderColor: isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)',
                    borderWidth: 1,
                    callbacks: {
                        title: function(tooltipItems) {
                            const idx = tooltipItems[0].dataIndex;
                            return therapyData[idx].therapy_name;
                        },
                        label: function(context) {
                            const idx = context.dataIndex;
                            const therapy = therapyData[idx];
                            return [
                                `Type: ${therapy.therapy_type}`,
                                `Overall Score: ${therapy.overall_score}`
                            ];
                        }
                    }
                }
            }
        }
    });
}

/**
 * Helper function to show notifications, ensuring we have access to the main notification function
 * @param {string} message - The message to display
 * @param {string} type - The type of notification (success, error, warning, info)
 */
function showNotification(message, type = 'info') {
    // Check if the main notification function exists
    if (typeof window.showNotification === 'function') {
        window.showNotification(message, type);
    } else {
        // Fallback implementation if the main function is not available
        console.log(`${type.toUpperCase()}: ${message}`);
        
        // Create a simple notification
        const notificationDiv = document.createElement('div');
        notificationDiv.className = `alert alert-${type} alert-dismissible fade show`;
        notificationDiv.setAttribute('role', 'alert');
        notificationDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        // Add to the page
        const container = document.querySelector('.container');
        if (container) {
            container.prepend(notificationDiv);
        } else {
            document.body.prepend(notificationDiv);
        }
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            notificationDiv.remove();
        }, 5000);
    }
}
