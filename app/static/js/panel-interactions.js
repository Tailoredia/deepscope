/**
 * Panel Interaction Handlers
 * Manages collapsible panels and toggle interactions
 */
document.addEventListener('DOMContentLoaded', () => {
    // Panel Section Toggles
    const panelSectionHeaders = document.querySelectorAll('.panel-section-header');
    panelSectionHeaders.forEach(header => {
        header.addEventListener('click', () => {
            const section = header.closest('.panel-section');
            const toggleButton = header.querySelector('.panel-section-toggle');

            section.classList.toggle('collapsed');

            // Update toggle button text
            toggleButton.textContent = section.classList.contains('collapsed') ? '+' : '−';
        });
    });

    // Left Panel Toggle
    const leftPanel = document.querySelector('.left-panel');
    const leftPanelToggle = document.querySelector('.left-panel-toggle');

    leftPanelToggle.addEventListener('click', () => {
        leftPanel.classList.toggle('collapsed');
        leftPanelToggle.textContent = leftPanel.classList.contains('collapsed') ? '❮' : '❯';
    });

    // Right Panel Toggle
    const rightPanel = document.querySelector('.right-panel');
    const rightPanelToggle = document.querySelector('.right-panel-toggle');

    rightPanelToggle.addEventListener('click', () => {
        rightPanel.classList.toggle('collapsed');
        rightPanelToggle.textContent = rightPanel.classList.contains('collapsed') ? '❮' : '❯';
    });

    // Responsive Resize Handling
    window.addEventListener('resize', () => {
        // Use AppState to get map safely
        const map = AppState.get('map');

        // Check if map exists and has invalidateSize method
        if (map && typeof map.invalidateSize === 'function') {
            try {
                map.invalidateSize();
            } catch (error) {
                console.warn('Error invalidating map size:', error);
            }
        }
    });
});