/**
 * Text Field Controls Module
 * Manages the text field checkboxes for marker labels
 */
const TextFieldControls = (function() {
    // Private variables
    let _debounceTimeoutId = null;

    /**
     * Generate text field controls UI
     * @param {Array} data - Data points
     */
    function generateControls(data) {
        const container = document.getElementById('textFieldControls');
        if (!container) {
            console.warn('Text field controls container not found');
            return;
        }

        container.innerHTML = '';

        const gridContainer = document.createElement('div');
        gridContainer.className = 'checkbox-grid';
        container.appendChild(gridContainer);

        const allCheckbox = Object.assign(document.createElement('input'), {
            type: 'checkbox',
            id: 'show-all-fields',
            checked: false
        });

        const allLabel = Object.assign(document.createElement('label'), {
            htmlFor: 'show-all-fields',
            textContent: '[ALL]'
        });

        const allCheckboxWrapper = document.createElement('div');
        allCheckboxWrapper.className = 'checkbox-wrapper all-checkbox';
        allCheckboxWrapper.append(allCheckbox, allLabel);
        gridContainer.appendChild(allCheckboxWrapper);

        const labelstrCheckbox = Object.assign(document.createElement('input'), {
            type: 'checkbox',
            id: 'show-labelstr',
            name: 'labelstr',
            checked: true
        });

        const labelstrLabel = Object.assign(document.createElement('label'), {
            htmlFor: 'show-labelstr',
            textContent: 'labelstr'
        });

        const labelstrWrapper = document.createElement('div');
        labelstrWrapper.className = 'checkbox-wrapper';
        labelstrWrapper.append(labelstrCheckbox, labelstrLabel);
        gridContainer.appendChild(labelstrWrapper);

        const sortedFields = AppState.get('sortedFields');
        const fieldCheckboxes = [labelstrCheckbox, ...sortedFields.map(field => {
            const checkbox = Object.assign(document.createElement('input'), {
                type: 'checkbox',
                id: `show-${field}`,
                name: field,
                checked: false
            });

            const label = Object.assign(document.createElement('label'), {
                htmlFor: `show-${field}`,
                textContent: field
            });

            const wrapper = document.createElement('div');
            wrapper.className = 'checkbox-wrapper';
            wrapper.append(checkbox, label);
            gridContainer.appendChild(wrapper);

            return checkbox;
        })];

        // Initialize handlers for the checkboxes
        const debouncedUpdateMarkers = () => {
            const selectedFields = Array.from(
                document.querySelectorAll('#textFieldControls input:checked:not(#show-all-fields)')
            ).map(cb => cb.name);

            const markers = AppState.get('markers');
            markers.eachLayer(marker => {
                const node = marker.options.originalData;
                const labelText = selectedFields.length > 0
                    ? selectedFields
                        .map(field => `${field}: ${node[field]}`)
                        .join(' | ')
                    : `labelstr: ${node.labelstr}`;

                const color = AppState.get('colorMap').get(node[AppState.get('currentColorField')]);
                const newMarker = Processors.createMarkerWithPopup(
                    node,
                    color,
                    AppState.get('currentColorField')
                );

                markers.removeLayer(marker);
                markers.addLayer(newMarker);
            });
        };

        const updateMarkersDebounced = () => {
            if (_debounceTimeoutId) clearTimeout(_debounceTimeoutId);
            _debounceTimeoutId = setTimeout(debouncedUpdateMarkers, 1000);
        };

        allCheckbox.addEventListener('change', () => {
            fieldCheckboxes.forEach(cb => {
                cb.checked = allCheckbox.checked;
            });
            updateMarkersDebounced();
        });

        fieldCheckboxes.forEach(cb => {
            cb.addEventListener('change', () => {
                allCheckbox.checked = fieldCheckboxes.every(checkbox => checkbox.checked);
                updateMarkersDebounced();
            });
        });
    }

    // Public API
    return {
        generateControls: generateControls
    };
})();