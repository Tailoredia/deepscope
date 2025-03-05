/**
 * Color Legend Handler Module
 * Manages color legend display with filtering functionality
 */
const ColorLegendHandler = (function() {
    /**
     * Update the legend with current color field values
     * @param {Array} uniqueValues - Unique values for the current color field
     */
    function updateLegend(uniqueValues) {
        console.log('Updating Color Legend', uniqueValues);

        // Sort values (numerically if possible, otherwise alphabetically)
        uniqueValues = uniqueValues.sort((a, b) => {
            const numA = Number(a);
            const numB = Number(b);
            if (!isNaN(numA) && !isNaN(numB)) {
                return numA - numB;
            }
            return String(a).localeCompare(String(b));
        });

        const legend = document.getElementById('legend');
        if (!legend) return;

        legend.innerHTML = '';

        // Add legend header with Select All/None links
        const headerDiv = document.createElement('div');
        headerDiv.className = 'legend-header';

        const titleSpan = document.createElement('h4');
        titleSpan.textContent = 'Color Legend';

        const actionLinks = document.createElement('div');
        actionLinks.className = 'filter-action-links';

        // Create "Select All" link
        const selectAllLink = document.createElement('a');
        selectAllLink.href = '#';
        selectAllLink.className = 'filter-action-link select-all';
        selectAllLink.textContent = 'Select All';
        selectAllLink.addEventListener('click', (e) => {
            e.preventDefault();
            selectAllLegendValues(uniqueValues);
        });

        // Create separator
        const separator = document.createTextNode(' | ');

        // Create "Select None" link
        const selectNoneLink = document.createElement('a');
        selectNoneLink.href = '#';
        selectNoneLink.className = 'filter-action-link select-none';
        selectNoneLink.textContent = 'Select None';
        selectNoneLink.addEventListener('click', (e) => {
            e.preventDefault();
            selectNoLegendValues();
        });

        // Add links to action links container
        actionLinks.appendChild(selectAllLink);
        actionLinks.appendChild(separator);
        actionLinks.appendChild(selectNoneLink);

        headerDiv.appendChild(titleSpan);
        headerDiv.appendChild(actionLinks);
        legend.appendChild(headerDiv);

        // Initialize color legend filter with all values
        const colorLegendFilter = new Set(uniqueValues);
        AppState.set('colorLegendFilter', colorLegendFilter);

        // Get the current color field
        const colorField = AppState.get('currentColorField');
        const containsBooleans = AppState.get('currentFieldContainsBooleans');

        // Count occurrences of each value
        const valueCounts = AppState.get('rawData').reduce((counts, node) => {
            const rawValue = node[colorField];

            // Ensure boolean values are converted to strings for consistent counting
            const value = typeof rawValue === 'boolean' ? String(rawValue) : rawValue;

            counts[value] = (counts[value] || 0) + 1;
            return counts;
        }, {});

        // Get color map
        const colorMap = AppState.get('colorMap');

        // Debug: display color map
        console.log('Color map for legend:', [...colorMap.entries()]);

        // Create legend items
        uniqueValues.forEach(value => {
            const item = document.createElement('div');
            item.className = 'legend-item';
            item.dataset.value = value; // Store the value in the dataset for easy reference
            item.style.cursor = 'pointer';
            item.style.opacity = '1';
            item.style.transition = 'opacity 0.2s ease';

            const colorBox = document.createElement('div');
            colorBox.className = 'legend-color';

            // Get color from color map - this is the key part
            const color = colorMap.get(value);
            colorBox.style.backgroundColor = color;

            // For debugging
            console.log(`Legend item color for ${value}: ${color}`);

            const label = document.createElement('span');
            label.className = 'legend-label';
            label.textContent = `${value} (${valueCounts[value] || 0})`;

            item.appendChild(colorBox);
            item.appendChild(label);

            item.addEventListener('click', () => {
                const colorLegendFilter = AppState.get('colorLegendFilter');

                // Toggle the clicked value in the filter
                if (colorLegendFilter.has(value)) {
                    colorLegendFilter.delete(value);
                    item.style.opacity = '0.5';
                } else {
                    colorLegendFilter.add(value);
                    item.style.opacity = '1';
                }

                // Update AppState
                AppState.set('colorLegendFilter', colorLegendFilter);

                // Log the current filter state
                console.log('Color Legend Filter Updated:', [...colorLegendFilter]);

                // Update the opacity of all legend items based on the current selection
                updateLegendItemOpacity(colorLegendFilter);

                // Apply filters
                FilterHandler.applyFilters();
            });

            legend.appendChild(item);
        });
    }

    /**
     * Update opacity of legend items based on the current filter
     * @param {Set} colorLegendFilter - Set of currently selected values
     */
    function updateLegendItemOpacity(colorLegendFilter) {
        const legend = document.getElementById('legend');
        if (!legend) return;

        // If no filters are active (empty set) or all items are selected, set all to default opacity
        const legendItems = legend.querySelectorAll('.legend-item');

        if (colorLegendFilter.size === 0 || colorLegendFilter.size === legendItems.length) {
            // Either all or none are selected, so uniform opacity
            legendItems.forEach(item => {
                item.style.opacity = colorLegendFilter.size === 0 ? '0.5' : '1';
            });
            return;
        }

        // Some items are selected, so highlight only those
        legendItems.forEach(item => {
            const itemValue = item.dataset.value;
            item.style.opacity = colorLegendFilter.has(itemValue) ? '1' : '0.5';
        });
    }

    /**
     * Select all legend values
     * @param {Array} values - All possible values
     */
    function selectAllLegendValues(values) {
        console.log('Selecting All Legend Values');

        // Create a new Set with all values
        const colorLegendFilter = new Set(values);
        AppState.set('colorLegendFilter', colorLegendFilter);

        // Update UI to ensure all items are fully visible
        const legend = document.getElementById('legend');
        legend.querySelectorAll('.legend-item').forEach(item => {
            item.style.opacity = '1';
        });

        // Apply filters
        FilterHandler.applyFilters();
    }

    /**
     * Select no legend values
     */
    function selectNoLegendValues() {
        console.log('Deselecting All Legend Values');

        // Create empty filter (allow all values to be deselected)
        const colorLegendFilter = new Set();
        AppState.set('colorLegendFilter', colorLegendFilter);

        // Update UI to fade out all items
        const legend = document.getElementById('legend');
        legend.querySelectorAll('.legend-item').forEach(item => {
            item.style.opacity = '0.5';
        });

        // Apply filters
        FilterHandler.applyFilters();
    }

    // Public API
    return {
        updateLegend: updateLegend,
        updateLegendItemOpacity: updateLegendItemOpacity,
        selectAllLegendValues: selectAllLegendValues,
        selectNoLegendValues: selectNoLegendValues
    };
})();