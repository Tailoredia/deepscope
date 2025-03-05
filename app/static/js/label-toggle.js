/**
 * Label Toggle Module
 * Adds functionality to toggle marker label visibility
 */
const LabelToggle = (function() {
    /**
     * Initialize the label toggle control
     */
    function initialize() {
        console.log('Initializing label toggle control');

        // Set initial label visibility state in AppState
        if (AppState.get('labelsVisible') === undefined) {
            AppState.set('labelsVisible', true);
        }

        // Create toggle element
        createToggleControl();
    }

    /**
     * Create the toggle control UI element
     */
    function createToggleControl() {
        // Find the container - ideally near text field controls
        const textFieldControlsContainer = document.getElementById('textFieldControls');
        if (!textFieldControlsContainer) {
            console.warn('Text field controls container not found');
            return;
        }

        // Create container for the toggle
        const toggleContainer = document.createElement('div');
        toggleContainer.className = 'label-visibility-control';
        toggleContainer.style.marginTop = '15px';
        toggleContainer.style.display = 'flex';
        toggleContainer.style.alignItems = 'center';

        // Create checkbox
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.id = 'toggle-labels';
        checkbox.checked = AppState.get('labelsVisible');

        // Create label
        const label = document.createElement('label');
        label.htmlFor = 'toggle-labels';
        label.textContent = 'Show Point Labels';
        label.style.marginLeft = '8px';
        label.style.fontWeight = 'bold';

        // Add event listener
        checkbox.addEventListener('change', () => {
            const isVisible = checkbox.checked;
            AppState.set('labelsVisible', isVisible);

            // Apply the change to all markers
            updateLabelVisibility(isVisible);
        });

        // Add elements to container
        toggleContainer.appendChild(checkbox);
        toggleContainer.appendChild(label);

        // Insert toggle control before the text field controls
        textFieldControlsContainer.parentNode.insertBefore(
            toggleContainer,
            textFieldControlsContainer
        );
    }

    /**
     * Update the visibility of all marker labels
     * @param {boolean} isVisible - Whether labels should be visible
     */
    function updateLabelVisibility(isVisible) {
        console.log(`Updating label visibility: ${isVisible}`);

        // Force refresh of markers with updated visibility
        FilterHandler.refreshMarkers();
    }

    // Return public API
    return {
        initialize: initialize,
        updateLabelVisibility: updateLabelVisibility
    };
})();

// Initialize label toggle when the document is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize after a short delay to ensure the map has loaded
    setTimeout(() => {
        LabelToggle.initialize();
    }, 1000);
});