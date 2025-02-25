const Processors = {
    /**
     * Get label text for a marker based on selected fields
     * @param {Object} node - Point data
     * @returns {string} Formatted label text
     */
    getLabelText(node) {
        // Default fallback if node not defined
        if (!node) return 'No Data';

        try {
            // Get selected fields directly from AppState or TextFieldControls module
            const selectedFields = AppState.get('selectedFields') ||
                (window.TextFieldControls && window.TextFieldControls.getSelectedFields()) ||
                ['labelstr'];

            console.log('Getting label text with selected fields:', selectedFields);

            if (selectedFields.length > 0) {
                return selectedFields
                    .filter(field => node.hasOwnProperty(field)) // Ensure field exists on node
                    .map(field => `${field}: ${node[field] || 'N/A'}`)
                    .join(' | ');
            } else {
                return `${node.labelstr || 'Unknown'}`;
            }
        } catch (error) {
            console.error('Error in getLabelText:', error);
            return 'Error in label';
        }
    },

    /**
     * Get the clustering distribution from a set of markers
     * @param {Array} markers - List of markers
     * @returns {Array} Distribution data for pie chart
     */
    getClusterDistribution(markers) {
        const distribution = {};
        markers.forEach(marker => {
            // Ensure we have a valid cluster_id
            const clusterId = String(marker.options.cluster_id || 'unknown');
            distribution[clusterId] = (distribution[clusterId] || 0) + 1;
        });
        return Object.entries(distribution).map(([cluster_id, value]) => ({
            cluster_id,
            value
        }));
    },

    /**
     * Create a D3 pie chart in a container
     * @param {HTMLElement} container - DOM element to place the chart
     * @param {Array} data - Distribution data
     * @returns {SVGElement} The created SVG element
     */
    createPieChart(container, data) {
        const width = 120;
        const height = 120;
        const radius = Math.min(width, height) / 2;

        d3.select(container).select('svg').remove();

        const svg = d3.select(container)
            .append('svg')
            .attr('width', width)
            .attr('height', height)
            .append('g')
            .attr('transform', `translate(${width/2},${height/2})`);

        const pie = d3.pie()
            .value(d => d.value)
            .sort(null);

        const arc = d3.arc()
            .innerRadius(radius * 0.5)
            .outerRadius(radius);

        // Ensure color map exists
        let colorMap = AppState.get('colorMap');
        if (!colorMap) {
            colorMap = new Map();
            AppState.set('colorMap', colorMap);
        }

        // Ensure unique, non-null cluster IDs
        const uniqueClusterIds = [...new Set(
            data
                .map(d => String(d.cluster_id || 'unknown'))
                .filter(id => id !== 'unknown')
        )];

        // Generate colors if not existing
        if (uniqueClusterIds.length > 0) {
            const colorGenerator = Utils.getColorForValues(uniqueClusterIds);
            uniqueClusterIds.forEach(id => {
                if (!colorMap.has(id)) {
                    colorMap.set(id, colorGenerator.getColor(id));
                }
            });
        }

        svg.selectAll('path')
            .data(pie(data))
            .enter()
            .append('path')
            .attr('d', arc)
            .attr('fill', d => {
                const clusterId = String(d.data.cluster_id || 'unknown');

                // Ensure we have a color, fallback to gray
                if (!colorMap.has(clusterId)) {
                    const newColor = Utils.getColorForValues([clusterId]).getColor(clusterId);
                    colorMap.set(clusterId, newColor);
                }

                return colorMap.get(clusterId) || '#cccccc';
            })
            .attr('stroke', 'white')
            .attr('stroke-width', '1');

        return svg.node();
    },

    /**
     * Create markers with popup for a data point
     * @param {Object} node - Point data
     * @param {string} color - Color for the marker
     * @param {string} colorField - Field used for coloring
     * @returns {L.Marker} Leaflet marker object
     */
    createMarkerWithPopup(node, color, colorField) {
        // Ensure node exists
        if (!node) {
            console.error('Attempted to create marker with undefined node');
            return null;
        }

        const radius = Utils.calculatePointRadius(node);
        const labelText = this.getLabelText(node);

        // Ensure color exists
        let colorMap = AppState.get('colorMap');
        if (!colorMap) {
            colorMap = new Map();
            AppState.set('colorMap', colorMap);
        }

        // Determine color value
        const colorValue = node[colorField] || 'unknown';

        if (!color) {
            const colorGenerator = Utils.getColorForValues([colorValue]);
            color = colorGenerator.getColor(colorValue);
            colorMap.set(colorValue, color);
            AppState.set('colorMap', colorMap);
        }

        const marker = L.marker([node.lat, node.lng], {
            icon: L.divIcon({
                html: `
                    <div style="position: relative;">
                        <div style="
                            width: ${radius}px;
                            height: ${radius}px;
                            border-radius: 50%;
                            background-color: ${color};
                            border: 2px solid white;
                            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                            display: flex;
                            align-items: center;
                            justify-content: center;
                        ">
                            ${node.total_count > 1 ? `<span style="color: white; font-size: ${radius/3}px; font-weight: bold;">${node.total_count}</span>` : ''}
                        </div>
                        <div style="
                            position: absolute;
                            top: ${radius + 2}px;
                            left: 50%;
                            transform: translateX(-50%);
                            background: white;
                            padding: 2px 6px;
                            border-radius: 3px;
                            border: 1px solid #ccc;
                            font-size: 12px;
                            white-space: nowrap;
                            box-shadow: 0 1px 3px rgba(0,0,0,0.2);
                            z-index: 1000;">
                            ${labelText}
                        </div>
                    </div>`,
                className: '',
                iconSize: [radius + 2, radius + 30],
                iconAnchor: [radius/2, radius/2]
            }),
            originalData: node,
            cluster_id: colorValue,
            label: labelText
        });

        marker.bindPopup(() => Utils.createPopupContent(node), {
            maxWidth: 350
        });

        return marker;
    },

    /**
     * Process points in chunks to avoid blocking the UI
     * @param {Array} points - Data points to process
     * @param {Object} options - Processing options
     * @returns {Promise} Promise resolving when processing is complete
     */
    createChunkedMarkers(points, options) {
        const {
            chunkSize = 100,
            colorField = 'type',
            colorMap = new Map(),
            markers,
            progressTracker
        } = options;

        // Filter out undefined or null points
        const validPoints = points.filter(point => point && point[colorField]);

        // Ensure color map is populated
        if (colorMap.size === 0) {
            const uniqueColorValues = [...new Set(
                validPoints.map(point => point[colorField])
            )];
            const colorGenerator = Utils.getColorForValues(uniqueColorValues);
            uniqueColorValues.forEach(value => {
                colorMap.set(value, colorGenerator.getColor(value));
            });
            AppState.set('colorMap', colorMap);
        }

        const totalChunks = Math.ceil(validPoints.length / chunkSize);
        let currentChunk = 0;

        return new Promise((resolve, reject) => {
            const processChunk = () => {
                const start = currentChunk * chunkSize;
                const end = Math.min(start + chunkSize, validPoints.length);

                for (let i = start; i < end; i++) {
                    const node = validPoints[i];
                    const color = colorMap.get(node[colorField]);
                    const marker = this.createMarkerWithPopup(node, color, colorField);
                    if (marker) {
                        markers.addLayer(marker);
                    }
                }

                currentChunk++;
                const progress = Math.min(60 + Math.round((currentChunk / totalChunks) * 40), 100);

                if (progressTracker) {
                    progressTracker.update(progress, `Processing markers: ${currentChunk}/${totalChunks}`);
                }

                if (currentChunk < totalChunks) {
                    // Use setTimeout to avoid blocking the UI
                    setTimeout(processChunk, 50);
                } else {
                    // Resolve the promise when all chunks are processed
                    if (progressTracker) {
                        progressTracker.hide();
                    }
                    resolve();
                }
            };

            // Start processing chunks
            processChunk();
        });
    }
};

// Add a global reference if needed
window.Processors = Processors;