/**
 * Main Visualization Module
 * Coordinates the overall visualization process
 */
const TsneVisualization = (function() {
    /**
     * Load and initialize the visualization
     */
    async function loadVisualization() {
        try {
            // Reset color generator to ensure fresh colors
            Utils.resetColorGenerator();

            // Create progress tracker
            const progressTracker = ProgressTracker.create();

            // Start loading
            progressTracker.update(20, 'Processing data...');

            // Fetch data
            const jsonFilename = Utils.getJsonFilename();
            console.log("Loading JSON file:", jsonFilename);

            // Try different possible paths for the JSON file
            let response;
            const possiblePaths = [
                `/ds/${jsonFilename}`,
                `/deepscope/${jsonFilename}`,
                `/${jsonFilename}`,
                jsonFilename
            ];

            for (const path of possiblePaths) {
                try {
                    response = await fetch(path);
                    if (response.ok) {
                        console.log("Successfully loaded from path:", path);
                        break;
                    }
                } catch (e) {
                    console.log("Failed to load from path:", path);
                }
            }

            if (!response || !response.ok) {
                throw new Error(`Failed to load JSON file: ${jsonFilename}`);
            }

            const data = await response.json();

            // Extract points and bounds
            const { points, bounds } = data;

            // Update progress
            progressTracker.update(40, 'Initializing map...');

            // Create map
            const { map, mapBounds } = MapInitializer.createMap(bounds);
            AppState.set('map', map);

            // IMPORTANT: Set window.map for any legacy code or direct access
            window.map = map;

            // Create marker cluster
            const markers = MapInitializer.createMarkerCluster();
            AppState.set('markers', markers);

            // Update progress
            progressTracker.update(60, 'Creating markers...');

            // Set raw data and sorted fields
            AppState.set('rawData', points);
            const sortedFields = Object.keys(points[0] || {})
                .filter(key => !['lat', 'lng', 'label', 'type'].includes(key))
                .sort();
            AppState.set('sortedFields', sortedFields);

            // Determine initial color field (first non-standard field)
            const currentColorField = sortedFields[0] || 'label';
            AppState.set('currentColorField', currentColorField);

            // Add markers to map
            map.addLayer(markers);

            // Fit bounds
            map.fitBounds(mapBounds, {
                padding: [30, 30],
                maxZoom: 1,
                animate: true,
                duration: 0.5
            });

            // Initialize UI
            UIHandlers.initializeMap(points);

            // Initialize filters
            FilterHandler.initializeFilters(points);

            // Finalize loading
            progressTracker.update(100, 'Complete!');
            setTimeout(() => progressTracker.hide(), 500);

        } catch (error) {
            console.error('Error loading visualization:', error);
            const progressTracker = ProgressTracker.create();
            progressTracker.update(100, 'Error loading visualization');
            setTimeout(() => progressTracker.hide(), 1000);
        }
    }

    /**
     * Reset the visualization state
     */
    function resetVisualization() {
        const map = AppState.get('map');
        const markers = AppState.get('markers');

        if (map && markers) {
            map.removeLayer(markers);
        }

        // Clear window.map reference
        window.map = null;

        // Reset color generator
        Utils.resetColorGenerator();

        AppState.reset();
    }

    /**
     * Initialize the visualization
     */
    function init() {
        // Call the load function when ready
        loadVisualization();
    }

    // Public API
    return {
        init: init,
        loadVisualization: loadVisualization,
        resetVisualization: resetVisualization
    };
})();

// Initialize visualization when the document is ready
document.addEventListener('DOMContentLoaded', function() {
    TsneVisualization.init();
});