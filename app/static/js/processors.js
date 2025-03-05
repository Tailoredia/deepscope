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

    getClusterDistribution(markers) {
        // Get the current color field
        const colorField = AppState.get('currentColorField');

        // Determine if we're dealing with a numeric field
        const numeric = AppState.get('rawData').filter(node =>
            node[colorField] !== null &&
            node[colorField] !== undefined &&
            !isNaN(Number(node[colorField])) &&
            typeof node[colorField] !== 'boolean'
        ).length > 0;

        // Handle differently based on whether it's a numeric or categorical field
        if (numeric) {
            // For numeric fields, group by rounded value ranges and calculate averages
            const valueGroups = {};
            const valueCounts = {};

            markers.forEach(marker => {
                // Get the value from the marker's original data
                const value = marker.options.originalData[colorField];
                if (value === null || value === undefined || isNaN(Number(value))) return;

                const numValue = Number(value);

                // Create bins for the values (adjust the bin size as needed)
                // This example uses 10 bins across the range
                const min = Math.min(...markers.map(m => Number(m.options.originalData[colorField])));
                const max = Math.max(...markers.map(m => Number(m.options.originalData[colorField])));
                const range = max - min;
                const binSize = range / 10;

                // Determine which bin this value belongs in
                const binIndex = Math.min(Math.floor((numValue - min) / binSize), 9);
                const binKey = `bin_${binIndex}`;

                // Accumulate values for calculating averages
                if (!valueGroups[binKey]) {
                    valueGroups[binKey] = 0;
                    valueCounts[binKey] = 0;
                }

                valueGroups[binKey] += numValue;
                valueCounts[binKey]++;
            });

            // Calculate average values for each group and prepare distribution
            return Object.entries(valueGroups).map(([binKey, sum]) => {
                const count = valueCounts[binKey];
                const average = sum / count;

                return {
                    cluster_id: binKey,
                    value: count,
                    average: average // Store the average for coloring
                };
            });
        } else {
            // Original categorical logic
            const distribution = {};
            markers.forEach(marker => {
                // Ensure we have a valid cluster_id with consistent handling of boolean values
                const rawClusterId = marker.options.cluster_id || 'unknown';
                // Convert all cluster IDs to strings for consistency, with special handling for booleans
                const clusterId = String(rawClusterId);
                distribution[clusterId] = (distribution[clusterId] || 0) + 1;
            });

            return Object.entries(distribution).map(([cluster_id, value]) => ({
                cluster_id,
                value
            }));
        }
    },

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

        // Get color map and current color field
        let colorMap = AppState.get('colorMap');
        const colorField = AppState.get('currentColorField');

        // Determine if the current field is numeric
        const rawData = AppState.get('rawData');
        const isNumeric = rawData.filter(node =>
            node[colorField] !== null &&
            node[colorField] !== undefined &&
            !isNaN(Number(node[colorField])) &&
            typeof node[colorField] !== 'boolean'
        ).length > 0;

        // If numeric and contains 'average' property, use numeric color scale
        if (isNumeric && data[0] && 'average' in data[0]) {
            // Get min and max values from raw data
            const numericValues = rawData
                .filter(node => node[colorField] !== null && node[colorField] !== undefined)
                .map(node => Number(node[colorField]))
                .filter(val => !isNaN(val));

            const min = Math.min(...numericValues);
            const max = Math.max(...numericValues);

            // Create color scale function
            const colorScale = Utils.getNumericColorScale(min, max);

            // Draw pie slices with colors based on average values
            svg.selectAll('path')
                .data(pie(data))
                .enter()
                .append('path')
                .attr('d', arc)
                .attr('fill', d => {
                    // Use the average value to determine color
                    return colorScale(d.data.average);
                })
                .attr('stroke', 'white')
                .attr('stroke-width', '1');
        } else {
            // Original categorical coloring logic
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
        }

        return svg.node();
    },
    createMarkerWithPopup(node, color, colorField) {
        // Ensure node exists
        if (!node) {
            console.error('Attempted to create marker with undefined node');
            return null;
        }

        const radius = Utils.calculatePointRadius(node);
        const labelText = this.getLabelText(node);

        // Get label visibility state from AppState
        const labelsVisible = AppState.get('labelsVisible') !== false; // Default to visible if not set

        // Ensure color exists
        let colorMap = AppState.get('colorMap');
        if (!colorMap) {
            colorMap = new Map();
            AppState.set('colorMap', colorMap);
        }

        // Determine color value with consistent handling of boolean values
        const rawColorValue = node[colorField];
        const colorValue = typeof rawColorValue === 'boolean' ? String(rawColorValue) : rawColorValue;

        if (!color) {
            // Try to get color from the map first
            color = colorMap.get(colorValue);

            // If no color is found, generate one
            if (!color) {
                const colorGenerator = Utils.getColorForValues([colorValue]);
                color = colorGenerator.getColor(colorValue);
                colorMap.set(colorValue, color);
                AppState.set('colorMap', colorMap);
            }
        }

        // Create marker HTML with label display conditional on visibility setting
        const markerHtml = `
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
                ${labelsVisible ? `
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
                </div>` : ''}
            </div>`;

        const marker = L.marker([node.lat, node.lng], {
            icon: L.divIcon({
                html: markerHtml,
                className: '',
                iconSize: [radius + 2, radius + (labelsVisible ? 30 : 2)],
                iconAnchor: [radius/2, radius/2]
            }),
            originalData: node,
            cluster_id: colorValue,  // Use the consistent color value here
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