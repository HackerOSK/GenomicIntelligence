/**
 * Therapy Visualization JavaScript
 * Handles visualization of therapy recommendations and card interactions
 */

/**
 * Initialize the therapy comparison chart
 * @param {Array} therapyData - Array of therapy recommendations
 */
function initTherapyComparisonChart(therapyData) {
    console.log("initTherapyComparisonChart called with data:", therapyData);
    
    // If no therapy data, return
    if (!therapyData || !Array.isArray(therapyData) || therapyData.length === 0) {
        console.warn('No therapy data available or data is not an array');
        return;
    }
    
    // Check if Chart.js is available
    if (typeof Chart === 'undefined') {
        console.error('Chart.js not loaded');
        throw new Error('Chart.js library is not loaded. Please check your network connection or include the Chart.js script.');
    }

    // Check if we have a canvas element
    const ctx = document.getElementById('therapyComparisonChart');
    if (!ctx) {
        console.warn('Chart canvas element not found');
        throw new Error('Chart canvas element not found. Please check the HTML structure.');
    }
    
    console.log("Canvas element found:", ctx);
    
    // Extract therapy names for labels
    const labels = therapyData.map(therapy => therapy.therapy_name || 'Unknown');
    console.log("Chart labels:", labels);

    // Extract scores for each category with fallbacks
    const efficacyScores = therapyData.map(therapy => Number(therapy.efficacy_score || 0));
    const compatibilityScores = therapyData.map(therapy => Number(therapy.compatibility_score || 0));
    const safetyScores = therapyData.map(therapy => Number(therapy.safety_score || 0));
    const costScores = therapyData.map(therapy => Number(therapy.cost_score || 0));
    
    console.log("Efficacy scores:", efficacyScores);
    console.log("Compatibility scores:", compatibilityScores);
    console.log("Safety scores:", safetyScores);
    console.log("Cost scores:", costScores);

    // Determine if dark mode is active
    const isDarkMode = document.body.classList.contains('dark-mode');
    const textColor = isDarkMode ? '#ffffff' : '#12263f';
    const gridColor = isDarkMode ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)';

    // Create the chart
    try {
        // Destroy existing chart if it exists
        if (window.therapyComparisonChart instanceof Chart) {
            window.therapyComparisonChart.destroy();
        }
        
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
                                return therapyData[idx].therapy_name || 'Unknown';
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
        
        console.log("Chart successfully created:", chart);
        
        // Store the chart instance for potential reuse or updates
        window.therapyComparisonChart = chart;
        
        return chart;
    } catch (error) {
        console.error("Error creating chart:", error);
        throw error;
    }
}

/**
 * Initialize the score circles
 */
function initScoreCircles() {
    console.log("Initializing score circles");
    const scoreCircles = document.querySelectorAll('.score-circle');
    
    if (!scoreCircles || scoreCircles.length === 0) {
        console.warn("No score circles found");
        return;
    }
    
    console.log(`Found ${scoreCircles.length} score circles`);
    
    scoreCircles.forEach(circle => {
        try {
            const score = parseInt(circle.getAttribute('data-score') || '0');
            const circumference = 2 * Math.PI * 38; // 38 is the radius of the circle
            const dashoffset = circumference - (score / 100) * circumference;
            
            // Create SVG for circle
            const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
            svg.setAttribute('width', '90');
            svg.setAttribute('height', '90');
            svg.setAttribute('viewBox', '0 0 90 90');
            svg.classList.add('score-svg');
            
            // Background circle
            const bgCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            bgCircle.setAttribute('cx', '45');
            bgCircle.setAttribute('cy', '45');
            bgCircle.setAttribute('r', '38');
            bgCircle.setAttribute('fill', 'none');
            bgCircle.setAttribute('stroke', '#e9ecef');
            bgCircle.setAttribute('stroke-width', '6');
            
            // Progress circle
            const progressCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            progressCircle.setAttribute('cx', '45');
            progressCircle.setAttribute('cy', '45');
            progressCircle.setAttribute('r', '38');
            progressCircle.setAttribute('fill', 'none');
            progressCircle.setAttribute('stroke', getScoreColor(score));
            progressCircle.setAttribute('stroke-width', '6');
            progressCircle.setAttribute('stroke-dasharray', circumference);
            progressCircle.setAttribute('stroke-dashoffset', dashoffset);
            progressCircle.setAttribute('transform', 'rotate(-90 45 45)');
            
            svg.appendChild(bgCircle);
            svg.appendChild(progressCircle);
            
            // Get the score value element
            const scoreValue = circle.querySelector('.score-value');
            
            // Clear the circle and append the SVG and score value
            circle.innerHTML = '';
            circle.appendChild(svg);
            if (scoreValue) {
                circle.appendChild(scoreValue.cloneNode(true));
            } else {
                const newScoreValue = document.createElement('span');
                newScoreValue.classList.add('score-value');
                newScoreValue.textContent = score;
                circle.appendChild(newScoreValue);
            }
        } catch (error) {
            console.error("Error initializing score circle:", error);
        }
    });
}

/**
 * Get color based on score
 * @param {number} score - The score value
 * @returns {string} - Color code
 */
function getScoreColor(score) {
    if (score >= 80) return '#00b8a9'; // High score - teal
    if (score >= 60) return '#39a0ed'; // Good score - blue
    if (score >= 40) return '#f6c90e'; // Medium score - yellow
    return '#f25f5c'; // Low score - red
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


