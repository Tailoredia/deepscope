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

                // Get the current color field
                const currentColorField = AppState.get('currentColorField');

                // Get distribution with proper handling of numeric fields
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

                // Create pie chart with the distribution data
                Processors.createPieChart(pieContainer, distribution);

                const size = Math.max(80, Math.min(200, 40 * Math.log(totalOriginalCount + 1)));
                const clusterIcon = L.divIcon({
                    html: container.outerHTML,
                    className: '',
                    iconSize: L.point(size, size)
                });

                // Check if it's a numeric field
                const rawData = AppState.get('rawData');
                const isNumeric = rawData.filter(node =>
                    node[currentColorField] !== null &&
                    node[currentColorField] !== undefined &&
                    !isNaN(Number(node[currentColorField])) &&
                    typeof node[currentColorField] !== 'boolean'
                ).length > 0;

                // Get common words for all cluster tooltips
                const commonWords = Utils.getMostCommonWords(labels, 30);

                // Number of words per column
                const wordsPerColumn = 10;
                const numColumns = Math.ceil(commonWords.length / wordsPerColumn);

                // Create HTML for multi-column layout of common terms
                let commonTermsHtml = `<div>Most common terms:</div><table><tr>`;

                // Create columns
                for (let col = 0; col < numColumns; col++) {
                    commonTermsHtml += '<td style="vertical-align: top; padding-right: 15px;">';

                    // Add words for this column
                    const startIdx = col * wordsPerColumn;
                    const endIdx = Math.min(startIdx + wordsPerColumn, commonWords.length);

                    for (let i = startIdx; i < endIdx; i++) {
                        commonTermsHtml += `<div>${commonWords[i]}</div>`;
                    }

                    commonTermsHtml += '</td>';
                }

                commonTermsHtml += '</tr></table>';

                let tooltipContent;

                if (isNumeric) {
                    // For numeric fields, show average values AND common terms
                    const values = childMarkers.map(marker =>
                        Number(marker.options.originalData[currentColorField])
                    ).filter(val => !isNaN(val));

                    const avg = values.reduce((sum, val) => sum + val, 0) / values.length;

                    tooltipContent = `<div>Cluster of ${count} points</div>
                                     <div>Average ${currentColorField}: ${avg.toFixed(2)}</div>
                                     ${commonTermsHtml}`;
                } else {
                    // For categorical fields, show just common terms
                    tooltipContent = `<div>Cluster of ${count} points</div>
                                    ${commonTermsHtml}`;
                }

                cluster.bindTooltip(tooltipContent, {
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