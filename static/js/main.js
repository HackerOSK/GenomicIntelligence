/**
 * Main JavaScript for the Precision Medicine Assistant
 * Handles common functionality across the application
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Initialize alerts dismissal
    const alertList = document.querySelectorAll('.alert');
    alertList.forEach(function(alert) {
        new bootstrap.Alert(alert);
    });
    
    // Export results button functionality
    const exportButton = document.getElementById('exportResults');
    if (exportButton) {
        exportButton.addEventListener('click', function() {
            exportTherapyResults();
        });
    }
});

/**
 * Export therapy results as PDF (simulated)
 */
function exportTherapyResults() {
    // In a real implementation, this would generate a PDF using a library
    // For this demo, we'll just show an alert
    alert('Report exported successfully! In a real implementation, this would generate a PDF.');
}

/**
 * Display a notification message
 * @param {string} message - The message to display
 * @param {string} type - The type of notification (success, error, warning, info)
 */
function showNotification(message, type = 'info') {
    const alertContainer = document.createElement('div');
    alertContainer.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertContainer.style.top = '20px';
    alertContainer.style.right = '20px';
    alertContainer.style.zIndex = '9999';
    
    alertContainer.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    document.body.appendChild(alertContainer);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const alertInstance = bootstrap.Alert.getInstance(alertContainer);
        if (alertInstance) {
            alertInstance.close();
        } else {
            alertContainer.remove();
        }
    }, 5000);
}

/**
 * Format number with commas for thousands separators
 * @param {number} num - The number to format
 * @returns {string} Formatted number
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

/**
 * Truncate text to a specific length and add ellipsis
 * @param {string} text - The text to truncate
 * @param {number} length - Maximum length before truncation
 * @returns {string} Truncated text
 */
function truncateText(text, length = 100) {
    if (!text) return '';
    if (text.length <= length) return text;
    return text.substring(0, length) + '...';
}
