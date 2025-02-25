/**
 * Categorical Filters Module
 * Manages dynamic filtering of categorical fields with proper empty state handling
 */
const CategoricalFilters = (function() {
    /**
     * Add toggle functionality to categorical filter sections
     */
    function addFilterSectionToggles() {
        const filterSections = document.querySelectorAll('.categorical-filter-section');

        filterSections.forEach(section => {
            const header = section.querySelector('.categorical-filter-header');
            const toggleButton = header.querySelector('.categorical-filter-toggle');

            // Ensure toggle button exists
            if (!toggleButton) {
                const newToggleButton = document.createElement('button');
                newToggleButton.className = 'categorical-filter-toggle';
                newToggleButton.textContent = '−';
                header.appendChild(newToggleButton);
            }

            header.addEventListener('click', (e) => {
                // Don't toggle when clicking on select all/none links
                if (e.target.classList.contains('filter-action-link')) {
                    return;
                }

                section.classList.toggle('collapsed');
                const toggleBtn = section.querySelector('.categorical-filter-toggle');
                toggleBtn.textContent = section.classList.contains('collapsed') ? '+' : '−';
            });
        });
    }

    /**
     * Generate categorical filter controls
     * @param {Array} data - Data points
     */
    function generateCategoricalFilterControls(data) {
        console.log('Generating Categorical Filter Controls');

        const container = document.getElementById('categoricalFilters');
        if (!container) return;

        container.innerHTML = ''; // Clear existing filters

        // Track which fields are categorical
        const categoricalFields = {};

        // Determine categorical fields
        AppState.get('sortedFields').forEach(field => {
            const values = [...new Set(data.map(node => node[field]))];
            const isNumeric = values.every(val =>
                val !== null &&
                val !== undefined &&
                !isNaN(Number(val))
            );

            if (!isNumeric) {
                categoricalFields[field] = values;
            }
        });

        // Create filter controls for categorical fields
        Object.entries(categoricalFields).forEach(([field, values]) => {
            // Create container for the field's filters
            const filterSection = document.createElement('div');
            filterSection.className = 'categorical-filter-section';

            // Create header
            const filterHeader = document.createElement('div');
            filterHeader.className = 'categorical-filter-header';

            // Create header content wrapper to hold the field title and action links
            const headerContentWrapper = document.createElement('div');
            headerContentWrapper.className = 'header-content-wrapper';

            const fieldTitle = document.createElement('h4');
            fieldTitle.textContent = field;

            // Create action links container
            const actionLinks = document.createElement('div');
            actionLinks.className = 'filter-action-links';

            // Create "Select All" link
            const selectAllLink = document.createElement('a');
            selectAllLink.href = '#';
            selectAllLink.className = 'filter-action-link select-all';
            selectAllLink.textContent = 'Select All';
            selectAllLink.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                selectAllValues(field, values);
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
                e.stopPropagation();
                selectNoValues(field);
            });

            // Add links to action links container
            actionLinks.appendChild(selectAllLink);
            actionLinks.appendChild(separator);
            actionLinks.appendChild(selectNoneLink);

            // Add field title and action links to wrapper
            headerContentWrapper.appendChild(fieldTitle);
            headerContentWrapper.appendChild(actionLinks);

            // Create toggle button
            const toggleButton = document.createElement('button');
            toggleButton.className = 'categorical-filter-toggle';
            toggleButton.textContent = '−';

            // Add wrapper and toggle button to header
            filterHeader.appendChild(headerContentWrapper);
            filterHeader.appendChild(toggleButton);

            // Create content container
            const filterContent = document.createElement('div');
            filterContent.className = 'categorical-filter-content';

            // Create filter grid
            const filterGrid = document.createElement('div');
            filterGrid.className = 'categorical-filter-grid';

            // Count occurrences of each value
            const valueCounts = data.reduce((counts, node) => {
                const value = node[field];
                counts[value] = (counts[value] || 0) + 1;
                return counts;
            }, {});

            // Sort values
            const sortedValues = values.sort((a, b) => {
                const numA = Number(a);
                const numB = Number(b);
                if (!isNaN(numA) && !isNaN(numB)) {
                    return numA - numB;
                }
                return String(a).localeCompare(String(b));
            });

            // Initialize field filters with all values
            const fieldFilters = new Set(sortedValues);
            AppState.set(`${field}Filters`, fieldFilters);

            // Create checkboxes for each value
            sortedValues.forEach(value => {
                const filterItem = document.createElement('div');
                filterItem.className = 'categorical-filter-item';

                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.id = `filter-${field}-${value}`;
                checkbox.name = value;
                checkbox.checked = true;  // Always start checked

                const label = document.createElement('label');
                label.htmlFor = checkbox.id;
                label.textContent = `${value} (${valueCounts[value] || 0})`;

                filterItem.appendChild(checkbox);
                filterItem.appendChild(label);
                filterGrid.appendChild(filterItem);

                // Add event listener for individual value filters
                checkbox.addEventListener('change', () => {
                    const fieldFilters = AppState.get(`${field}Filters`);

                    if (checkbox.checked) {
                        fieldFilters.add(value);
                    } else {
                        // Allow removing any filter, even if it's the last one
                        fieldFilters.delete(value);
                    }

                    // Update AppState
                    AppState.set(`${field}Filters`, fieldFilters);

                    // Log the current filter state
                    console.log(`${field} Filter Updated:`, [...fieldFilters]);

                    // Apply filters
                    FilterHandler.applyFilters();
                });
            });

            // Append elements
            filterContent.appendChild(filterGrid);
            filterSection.appendChild(filterHeader);
            filterSection.appendChild(filterContent);
            container.appendChild(filterSection);
        });

        // Add toggle functionality
        addFilterSectionToggles();
    }

    /**
     * Select all values for a field
     * @param {String} field - Field name
     * @param {Array} values - Field values
     */
    function selectAllValues(field, values) {
        console.log(`Selecting All Values for ${field}`);

        // Update field filters in AppState
        const fieldFilters = new Set(values);
        AppState.set(`${field}Filters`, fieldFilters);

        // Update checkboxes
        const checkboxes = document.querySelectorAll(`input[id^="filter-${field}-"]`);
        checkboxes.forEach(checkbox => {
            checkbox.checked = true;
        });

        // Apply filters
        FilterHandler.applyFilters();
    }

    /**
     * Select no values for a field
     * @param {String} field - Field name
     */
    function selectNoValues(field) {
        console.log(`Deselecting All Values for ${field}`);

        // Create an empty filter set - allow completely empty filters
        const fieldFilters = new Set();
        AppState.set(`${field}Filters`, fieldFilters);

        // Update checkboxes
        const checkboxes = document.querySelectorAll(`input[id^="filter-${field}-"]`);
        checkboxes.forEach(checkbox => {
            checkbox.checked = false;
        });

        // Apply filters
        FilterHandler.applyFilters();
    }

    // Public API
    return {
        generateCategoricalFilterControls: generateCategoricalFilterControls,
        selectAllValues: selectAllValues,
        selectNoValues: selectNoValues
    };
})();