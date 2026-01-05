// Theme Toggle Functionality
(function() {
    'use strict';
    
    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');
    const html = document.documentElement;
    
    // Get saved theme or default to light
    const currentTheme = localStorage.getItem('theme') || 'light';
    html.setAttribute('data-theme', currentTheme);
    updateIcon(currentTheme);
    
    // Toggle theme on button click
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const currentTheme = html.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            html.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateIcon(newTheme);
        });
    }
    
    function updateIcon(theme) {
        if (themeIcon) {
            if (theme === 'dark') {
                themeIcon.className = 'ti-moon';
            } else {
                themeIcon.className = 'ti-sun';
            }
        }
    }
    
    // Listen for system theme changes
    if (window.matchMedia) {
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        
        // Only apply system theme if user hasn't set a preference
        if (!localStorage.getItem('theme')) {
            mediaQuery.addEventListener('change', function(e) {
                const newTheme = e.matches ? 'dark' : 'light';
                html.setAttribute('data-theme', newTheme);
                updateIcon(newTheme);
            });
        }
    }
})();

