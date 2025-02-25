/**
 * Filter Handler Module
 * Centralized filtering logic for all filters
 */
const FilterHandler = (function() {
    /**
     * Apply all filters to markers
     */
    function applyFilters() {
        console.log('------- APPLYING FILTERS -------');

        // Get critical application state
        const rawData = AppState.get('rawData');
        const markers = AppState.get('markers');
        const currentColorField = AppState.get('currentColorField');

        // Sanity checks
        if (!rawData || !markers || !currentColorField) {
            console.error('Cannot apply filters: missing critical data', {
                rawData: !!rawData,
                markers: !!markers,
                currentColorField
            });
            return;
        }

        // Collect all filter sets
        const allFilters = {};

        // Collect color legend filters
        const colorLegendFilter = AppState.get('colorLegendFilter');
        if (colorLegendFilter && colorLegendFilter.size > 0) {
            allFilters[currentColorField] = colorLegendFilter;
        }

        // Collect categorical field filters
        Object.keys(AppState.getAll())
            .filter(key => key.endsWith('Filters') && key !== 'colorLegendFilter')
            .forEach(key => {
                const field = key.replace('Filters', '');
                const fieldFilter = AppState.get(key);
                if (fieldFilter && fieldFilter.size > 0) {
                    allFilters[field] = fieldFilter;
                }
            });

        // Log all active filters
        console.log('Active Filters:', allFilters);

        // Filter data using AND logic
        const filteredData = rawData.filter(node => {
            // Check each active filter
            return Object.entries(allFilters).every(([field, filterSet]) => {
                // Check if the node has the field and its value is in the filter set
                const isValid = node.hasOwnProperty(field) && filterSet.has(node[field]);

                // Detailed logging for debugging
                if (!isValid) {
                    console.log(`Filtered out:`, {
                        node,
                        field,
                        fieldValue: node[field],
                        allowedValues: [...filterSet]
                    });
                }

                return isValid;
            });
        });

        // Log filtering results
        console.log('Filtering Results:', {
            totalDataPoints: rawData.length,
            filteredDataPoints: filteredData.length
        });

        // Ensure color map exists
        let colorMap = AppState.get('colorMap');
        if (!colorMap || colorMap.size === 0) {
            const uniqueColorValues = [...new Set(rawData.map(node => node[currentColorField]))];
            colorMap = new Map();
            const colorGenerator = Utils.getColorForValues(uniqueColorValues);
            uniqueColorValues.forEach(value => {
                colorMap.set(value, colorGenerator.getColor(value));
            });
            AppState.set('colorMap', colorMap);
        }

        // Clear and recreate markers
        markers.clearLayers();

        // Add filtered markers
        filteredData.forEach(node => {
            const color = colorMap.get(node[currentColorField]);
            const marker = Processors.createMarkerWithPopup(
                node,
                color,
                currentColorField
            );
            markers.addLayer(marker);
        });

        // Fit bounds if possible
        const map = AppState.get('map');
        if (markers.getLayers().length > 0 && map) {
            try {
                map.fitBounds(markers.getBounds(), {
                    padding: [30, 30],
                    maxZoom: map.getZoom()
                });
            } catch (e) {
                console.warn('Could not fit bounds:', e);
            }
        }

        console.log('------- FILTERS APPLIED -------');
    }

    /**
     * Refresh all markers (used for updating display fields)
     */
    function refreshMarkers() {
        console.log('------- REFRESHING MARKERS -------');

        // This is a simpler version of applyFilters that just recreates all markers
        // to update their display text without changing the filtering

        const rawData = AppState.get('rawData');
        const markers = AppState.get('markers');
        const currentColorField = AppState.get('currentColorField');
        const colorMap = AppState.get('colorMap');

        if (!rawData || !markers || !currentColorField || !colorMap) {
            console.error('Cannot refresh markers: missing critical data');
            return;
        }

        // Get the currently visible markers' data
        const visibleData = [];
        markers.eachLayer(marker => {
            if (marker.options && marker.options.originalData) {
                visibleData.push(marker.options.originalData);
            }
        });

        // Clear and recreate markers
        markers.clearLayers();

        // Add recreated markers with updated labels
        visibleData.forEach(node => {
            const color = colorMap.get(node[currentColorField]);
            const marker = Processors.createMarkerWithPopup(
                node,
                color,
                currentColorField
            );
            markers.addLayer(marker);
        });

        console.log(`Refreshed ${visibleData.length} markers with updated display fields`);
        console.log('------- MARKERS REFRESHED -------');
    }

    /**
     * Initialize default filter state
     * @param {Array} data - Raw data points
     */
    function initializeFilters(data) {
        console.log('Initializing Filters');

        // Ensure data exists
        if (!data || data.length === 0) {
            console.warn('Cannot initialize filters: no data');
            return;
        }

        // Get current color field
        const currentColorField = AppState.get('currentColorField');
        const sortedFields = AppState.get('sortedFields');

        // Initialize color legend filter with all unique values
        const colorValues = [...new Set(data.map(node => node[currentColorField]))];
        AppState.set('colorLegendFilter', new Set(colorValues));
        console.log('Color Legend Filter:', colorValues);

        // Initialize categorical field filters
        sortedFields.forEach(field => {
            const uniqueValues = [...new Set(data.map(node => node[field]))];
            AppState.set(`${field}Filters`, new Set(uniqueValues));
            console.log(`${field} Filter:`, uniqueValues);
        });

        // Ensure color map is populated
        const colorMap = new Map();
        const colorGenerator = Utils.getColorForValues(colorValues);
        colorValues.forEach(value => {
            colorMap.set(value, colorGenerator.getColor(value));
        });
        AppState.set('colorMap', colorMap);

        // Initialize selectedFields with labelstr as default
        if (!AppState.get('selectedFields')) {
            AppState.set('selectedFields', ['labelstr']);
        }

        // Apply filters to ensure all nodes are initially visible
        applyFilters();
    }

    // Public API
    return {
        applyFilters: applyFilters,
        refreshMarkers: refreshMarkers,
        initializeFilters: initializeFilters
    };
})();