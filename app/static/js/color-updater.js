/**
 * Color Updater Module
 * Handles updating marker colors and color-related UI with proper filter integration
 */
const ColorUpdater = (function() {
    /**
     * Update colors for data based on a specific field
     * @param {Array} data - Data points
     * @param {String} field - Field to use for coloring
     */
    function updateColors(data, field) {
        console.log(`Updating colors based on field: ${field}`);

        // Get unique values and handle numeric vs categorical
        const uniqueValues = [...new Set(data.map(node => {
            const value = node[field];
            // Explicitly convert boolean to string
            return typeof value === 'boolean' ? String(value) : value;
        }))];

        console.log(`Unique values for ${field}:`, uniqueValues);

        const colorGenerator = Utils.getColorForValues(uniqueValues);
        const colorMap = new Map();

        uniqueValues.forEach((value) => {
            // Ensure string conversion for boolean
            const stringValue = typeof value === 'boolean' ? String(value) : value;
            const color = colorGenerator.getColor(stringValue);
            colorMap.set(stringValue, color);
        });

        // Update app state with new color map
        AppState.set('colorMap', colorMap);

        // Create a new color legend filter with all values selected
        const colorLegendFilter = new Set(uniqueValues);
        AppState.set('colorLegendFilter', colorLegendFilter);
        console.log('Color Legend Filter Reset:', [...colorLegendFilter]);

        // Update legend with new color values
        ColorLegendHandler.updateLegend(uniqueValues);

        console.log('Updated color map and legend');
    }

    /**
     * Setup color field selector
     * @param {Array} data - Data points
     */
    function setupColorFieldSelector(data) {
        const colorFieldSelect = document.getElementById('colorField');
        if (!colorFieldSelect) {
            console.warn('Color field select element not found');
            return;
        }

        colorFieldSelect.innerHTML = '';

        // Add options using sorted fields
        const sortedFields = AppState.get('sortedFields');
        sortedFields.forEach(field => {
            const option = document.createElement('option');
            option.value = field;
            option.textContent = field;
            colorFieldSelect.appendChild(option);
        });

        // Set initial value
        const initialColorField = colorFieldSelect.value;
        AppState.set('currentColorField', initialColorField);
        console.log('Initial color field set to:', initialColorField);

        // Add event listener
        colorFieldSelect.addEventListener('change', (e) => {
            const newColorField = e.target.value;
            console.log('Color field changed to:', newColorField);

            AppState.set('currentColorField', newColorField);
            updateColors(data, newColorField);

            // Force refresh of markers with new colors
            FilterHandler.applyFilters();
        });

        // Initialize colors
        updateColors(data, initialColorField);
    }

    // Public API
    return {
        updateColors: updateColors,
        setupColorFieldSelector: setupColorFieldSelector
    };
})();

/**
 * UI Handlers Module
 * Provides main UI initialization functionality
 */
const UIHandlers = (function() {
    /**
     * Initialize map UI and event handlers
     * @param {Array} data - Data points
     */
    function initializeMap(data) {
        console.log('Initializing map UI with data points:', data.length);

        // Store raw data in state
        AppState.set('rawData', data);

        // Initialize sorted fields
        const sortedFields = Object.keys(data[0] || {})
            .filter(key => !['lat', 'lng', 'label', 'type'].includes(key))
            .sort();
        AppState.set('sortedFields', sortedFields);
        console.log('Sorted fields:', sortedFields);

        // Set up color field selector
        ColorUpdater.setupColorFieldSelector(data);

        // Generate field checkboxes
        TextFieldControls.generateControls(data);

        // Generate categorical filter controls
        CategoricalFilters.generateCategoricalFilterControls(data);
    }

    // Public API
    return {
        initializeMap: initializeMap,
        updateColors: ColorUpdater.updateColors
    };
})();