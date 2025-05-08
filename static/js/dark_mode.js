/**
 * Dark mode toggle functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get the stored theme from localStorage
    const currentTheme = localStorage.getItem('theme');
    
    // Apply the theme if it exists in localStorage
    if (currentTheme) {
        document.body.classList.toggle('dark-mode', currentTheme === 'dark');
        updateThemeIcon(currentTheme === 'dark');
    }
    
    // Set up theme toggle button
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleDarkMode);
    }
});

/**
 * Toggle dark mode on/off
 */
function toggleDarkMode() {
    // Toggle the dark-mode class on the body
    document.body.classList.toggle('dark-mode');
    
    // Determine the current theme based on the body class
    const isDarkMode = document.body.classList.contains('dark-mode');
    
    // Store the theme preference in localStorage
    localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
    
    // Update the icon
    updateThemeIcon(isDarkMode);
    
    // Update charts if they exist on the page
    updateChartsTheme(isDarkMode);
}

/**
 * Update the theme toggle icon
 * @param {boolean} isDarkMode - Whether dark mode is enabled
 */
function updateThemeIcon(isDarkMode) {
    const themeIcon = document.querySelector('#theme-toggle i');
    if (themeIcon) {
        // Remove existing classes
        themeIcon.classList.remove('fa-sun', 'fa-moon');
        
        // Add appropriate icon class
        themeIcon.classList.add(isDarkMode ? 'fa-sun' : 'fa-moon');
    }
}

/**
 * Update Chart.js charts to match the current theme
 * @param {boolean} isDarkMode - Whether dark mode is enabled
 */
function updateChartsTheme(isDarkMode) {
    // Get all charts on the page
    if (typeof Chart !== 'undefined') {
        Chart.helpers.each(Chart.instances, function(instance) {
            // Update chart options for the theme
            instance.options.plugins.legend.labels.color = isDarkMode ? '#ffffff' : '#12263f';
            instance.options.scales.x.ticks.color = isDarkMode ? '#95aac9' : '#95aac9';
            instance.options.scales.y.ticks.color = isDarkMode ? '#95aac9' : '#95aac9';
            instance.options.scales.x.grid.color = isDarkMode ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)';
            instance.options.scales.y.grid.color = isDarkMode ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)';
            
            // Update the chart
            instance.update();
        });
    }
}
