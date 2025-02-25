/**
 * Map Initializer Module
 * Handles map and marker layer initialization
 */
const MapInitializer = (function() {
    /**
     * Create a Leaflet map with appropriate settings
     * @param {Object} bounds - Map bounds
     * @param {Object} options - Map options
     * @returns {Object} Map and bounds objects
     */
    function createMap(bounds, options = {}) {
        const {
            minZoom = -1.5,
            maxZoom = 10,
            zoomSnap = 1,
            zoomDelta = 1,
            wheelPxPerZoomLevel = 120
        } = options;

        const crs = L.CRS.Simple;
        const map = L.map('map', {
            crs,
            minZoom,
            maxZoom,
            zoomSnap,
            zoomDelta,
            wheelPxPerZoomLevel
        });

        const mapBounds = L.latLngBounds([
            [bounds.min_lat * 1.1, bounds.min_lng * 1.1],
            [bounds.max_lat * 1.1, bounds.max_lng * 1.1]
        ]);

        return { map, mapBounds };
    }

    /**
     * Create a marker cluster group with custom settings
     * @param {Object} options - Clustering options
     * @returns {L.MarkerClusterGroup} Cluster group
     */
    function createMarkerCluster(options = {}) {
        return L.markerClusterGroup({
            maxClusterRadius: (zoom) => {
                const zoomLevels = [
                    { max: -1, radius: 180 },
                    { max: -0.5, radius: 160 },
                    { max: 0, radius: 140 },
                    { max: 0.5, radius: 120 },
                    { max: 1, radius: 100 },
                    { max: 1.5, radius: 80 },
                    { max: 2, radius: 60 },
                    { max: 2.5, radius: 40 },
                    { max: Infinity, radius: 30 }
                ];
                const matchedLevel = zoomLevels.find(level => zoom <= level.max);
                return matchedLevel ? matchedLevel.radius : 30;
            },
            spiderfyOnMaxZoom: true,
            showCoverageOnHover: true,
            zoomToBoundsOnClick: true,
            removeOutsideVisibleBounds: true,
            animate: true,
            animateAddingMarkers: false,
            chunkedLoading: true,
            chunkInterval: 200,
            chunkDelay: 50,
            disableClusteringAtZoom: null,
            spiderfyDistanceMultiplier: 1.5,
            iconCreateFunction: function(cluster) {
                const childMarkers = cluster.getAllChildMarkers();
                const count = cluster.getChildCount();

                const distribution = Processors.getClusterDistribution(childMarkers);
                const labels = childMarkers.map(marker => marker.options.label);

                const totalOriginalCount = childMarkers.reduce((sum, marker) => {
                    const nodeCount = marker.options.originalData.occurrence_count ||
                                    marker.options.originalData.total_count || 1;
                    return sum + nodeCount;
                }, 0);

                const container = document.createElement('div');
                container.className = 'custom-cluster';

                const pieContainer = document.createElement('div');
                pieContainer.className = 'pie-container';

                const countDiv = document.createElement('div');
                countDiv.className = 'count';
                countDiv.textContent = count;

                container.appendChild(pieContainer);
                container.appendChild(countDiv);

                Processors.createPieChart(pieContainer, distribution);

                const size = Math.max(80, Math.min(200, 40 * Math.log(totalOriginalCount + 1)));
                const clusterIcon = L.divIcon({
                    html: container.outerHTML,
                    className: '',
                    iconSize: L.point(size, size)
                });

                const commonWords = Utils.getMostCommonWords(labels);
                cluster.bindTooltip(`Most common terms:\n${commonWords.join('\n')}`, {
                    direction: 'top',
                    offset: L.point(0, -60),
                    className: 'cluster-tooltip',
                    opacity: 0.9
                });

                return clusterIcon;
            },
        });
    }

    // Public API
    return {
        createMap: createMap,
        createMarkerCluster: createMarkerCluster
    };
})();