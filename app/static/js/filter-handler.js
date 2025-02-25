/**
 * Filter Handler Module
 * Centralized filtering logic with properly functioning color legend filter
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

        // Log current application state for debugging
        console.log('Current Color Field:', currentColorField);

        // Collect all filter sets
        const colorLegendFilter = AppState.get('colorLegendFilter');
        console.log('Color Legend Filter:', colorLegendFilter ? [...colorLegendFilter] : 'undefined');

        // Get all categorical filters
        const categoryFilters = {};
        Object.keys(AppState.getAll())
            .filter(key => key.endsWith('Filters') && key !== 'colorLegendFilter')
            .forEach(key => {
                const field = key.replace('Filters', '');
                const fieldFilter = AppState.get(key);
                if (fieldFilter) {
                    categoryFilters[field] = fieldFilter;
                }
            });

        console.log('Category Filters:', Object.fromEntries(
            Object.entries(categoryFilters).map(([k, v]) => [k, [...v]])
        ));

        // Filter data with combined logic
        const filteredData = rawData.filter(node => {
            // 1. Check color legend filter
            const passesColorFilter = !colorLegendFilter ||
                                      colorLegendFilter.size === 0 ||
                                      colorLegendFilter.has(node[currentColorField]);

            if (!passesColorFilter) {
                return false;
            }

            // 2. Check all category filters
            return Object.entries(categoryFilters).every(([field, filterSet]) => {
                return filterSet.size === 0 || filterSet.has(node[field]);
            });
        });

        // Log filtering results
        console.log('Filtering Results:', {
            totalDataPoints: rawData.length,
            filteredDataPoints: filteredData.length,
            colorFilterActive: colorLegendFilter && colorLegendFilter.size > 0,
            categoryFiltersActive: Object.values(categoryFilters).some(set => set.size > 0)
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
            const value = node[currentColorField];
            const color = colorMap.get(value);
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
        if (currentColorField) {
            const colorValues = [...new Set(data.map(node => node[currentColorField]))];
            AppState.set('colorLegendFilter', new Set(colorValues));
            console.log('Color Legend Filter Initialized:', colorValues);
        }

        // Initialize categorical field filters
        sortedFields.forEach(field => {
            const uniqueValues = [...new Set(data.map(node => node[field]))];
            AppState.set(`${field}Filters`, new Set(uniqueValues));
            console.log(`${field} Filter Initialized:`, uniqueValues);
        });

        // Apply filters to ensure all nodes are initially visible
        applyFilters();
    }

    // Public API
    return {
        applyFilters: applyFilters,
        initializeFilters: initializeFilters
    };
})();