/**
 * Color Updater Module
 * Handles updating marker colors and color-related UI with proper filter integration
 */
const ColorUpdater = (function() {
    function updateColors(data, field) {
        console.log(`Updating colors based on field: ${field}`);

        // Always reset the color generator when changing fields
        Utils.resetColorGenerator();

        // If field is 'none' (no suitable color field), handle gracefully
        if (field === 'none') {
            console.log('No suitable color field selected. Using default coloring.');
            // Use a single color for all markers
            const colorMap = new Map();
            colorMap.set('default', '#3388ff'); // Leaflet default blue
            AppState.set('colorMap', colorMap);
            AppState.set('currentFieldContainsBooleans', false);

            // Create empty legend to clear previous one
            ColorLegendHandler.updateLegend([]);
            return;
        }

        // Determine if the field contains boolean values
        const containsBooleans = data.some(node => typeof node[field] === 'boolean');
        console.log(`Field ${field} contains boolean values: ${containsBooleans}`);

        // Determine if the field contains numeric values
        const numericValues = data.filter(node =>
            node[field] !== null &&
            node[field] !== undefined &&
            !isNaN(Number(node[field])) &&
            typeof node[field] !== 'boolean'
        ).map(node => Number(node[field]));

        const isNumeric = numericValues.length > 0;

        // Get unique values and ensure consistent handling of boolean values
        const uniqueValues = [...new Set(data.map(node => {
            const value = node[field];
            // Always convert booleans to strings for consistent handling
            return typeof value === 'boolean' ? String(value) : value;
        }))];

        console.log(`Unique values for ${field}:`, uniqueValues);
        console.log(`Field has ${uniqueValues.length} unique values`);

        const colorMap = new Map();

        if (isNumeric && !containsBooleans) {
            // If the field is numeric, use a color scale
            console.log("Using numeric color scale for field:", field);

            // Find min and max values
            const min = Math.min(...numericValues);
            const max = Math.max(...numericValues);

            console.log(`Numeric range: ${min} to ${max}`);

            // Create a color scale function
            const colorScale = Utils.getNumericColorScale(min, max);

            // Map each value to its color on the scale
            uniqueValues.forEach(value => {
                const numValue = Number(value);
                const color = !isNaN(numValue) ? colorScale(numValue) : '#cccccc';
                colorMap.set(value, color);
            });
        } else {
            // For non-numeric or mixed fields, use categorical colors
            // Force a new color generator AND pass the field name to ensure different colors
            const colorGenerator = Utils.getColorForValues(uniqueValues, true, field);

            uniqueValues.forEach(value => {
                const color = colorGenerator.getColor(value);
                colorMap.set(value, color);
                console.log(`Set color for ${value}: ${color}`);
            });
        }

        // Log the color mapping
        console.log("Color mapping:", Array.from(colorMap.entries()));

        // Update app state with new color map
        AppState.set('colorMap', colorMap);

        // Store information about whether this field contains booleans
        AppState.set('currentFieldContainsBooleans', containsBooleans);

        // Create a new color legend filter with all values selected
        const colorLegendFilter = new Set(uniqueValues);
        AppState.set('colorLegendFilter', colorLegendFilter);
        console.log('Color Legend Filter Reset:', [...colorLegendFilter]);

        // Limit the number of legend items to prevent performance issues
        const maxLegendItems = 50;
        const legendValues = uniqueValues.length > maxLegendItems ?
            uniqueValues.slice(0, maxLegendItems) : uniqueValues;

        // Update legend with new color values
        ColorLegendHandler.updateLegend(legendValues);

        console.log('Updated color map and legend');
    }

    function setupColorFieldSelector(data) {
        const colorFieldSelect = document.getElementById('colorField');
        if (!colorFieldSelect) {
            console.warn('Color field select element not found');
            return;
        }

        colorFieldSelect.innerHTML = '';

        // Add options using sorted fields, excluding high cardinality non-numeric fields
        const sortedFields = AppState.get('sortedFields');
        const maxUniqueValues = 50; // Maximum number of unique values for a non-numeric color field

        // Track fields that are suitable for color coding
        const suitableColorFields = sortedFields.filter(field => {
            // Count unique values for this field
            const uniqueValues = new Set(data.map(item => item[field]));
            const cardinalityCount = uniqueValues.size;

            // Determine if the field contains numeric values
            const numericValues = data.filter(node =>
                node[field] !== null &&
                node[field] !== undefined &&
                !isNaN(Number(node[field])) &&
                typeof node[field] !== 'boolean'
            ).map(node => Number(node[field]));

            const isNumeric = numericValues.length > 0 && numericValues.length === data.length;

            // If field has too many unique values AND isn't numeric, exclude it
            if (cardinalityCount > maxUniqueValues && !isNumeric) {
                console.log(`Excluding high cardinality non-numeric field: ${field} (${cardinalityCount} unique values)`);
                return false;
            }

            return true;
        });

        // If no suitable fields found, add a default option
        if (suitableColorFields.length === 0) {
            console.warn('No suitable fields found for color coding');
            const option = document.createElement('option');
            option.value = 'none';
            option.textContent = 'No suitable fields';
            colorFieldSelect.appendChild(option);
            return;
        }

        suitableColorFields.forEach(field => {
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