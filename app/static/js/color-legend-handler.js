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

        // Count occurrences of each value
        const valueCounts = AppState.get('rawData').reduce((counts, node) => {
            const value = node[AppState.get('currentColorField')];
            counts[value] = (counts[value] || 0) + 1;
            return counts;
        }, {});

        // Create legend items
        uniqueValues.forEach(value => {
            const item = document.createElement('div');
            item.className = 'legend-item';
            item.style.cursor = 'pointer';
            item.style.opacity = '1';
            item.style.transition = 'opacity 0.2s ease';

            const colorBox = document.createElement('div');
            colorBox.className = 'legend-color';
            colorBox.style.backgroundColor = AppState.get('colorMap').get(value);

            const label = document.createElement('span');
            label.className = 'legend-label';
            label.textContent = `${value} (${valueCounts[value] || 0})`;

            item.appendChild(colorBox);
            item.appendChild(label);

            item.addEventListener('click', () => {
                const colorLegendFilter = AppState.get('colorLegendFilter');

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

                // Apply filters
                FilterHandler.applyFilters();
            });

            legend.appendChild(item);
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
        selectAllLegendValues: selectAllLegendValues,
        selectNoLegendValues: selectNoLegendValues
    };
})();