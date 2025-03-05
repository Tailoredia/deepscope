/**
 * Utilities Module
 * General utility functions for the visualization
 */
const Utils = (function() {
    // Shared color generator to ensure consistent colors
    let _sharedColorGenerator = null;

    /**
     * Generate a consistent color palette for a set of values
     * @param {Array} values - Values to generate colors for
     * @returns {Object} Color generator with consistent color mapping
     */
    function getColorForValues(values) {
        // Clean and deduplicate values, ensuring boolean values are converted to strings
        const cleanValues = [...new Set(values.filter(val =>
            val != null &&
            val !== '' &&
            String(val).trim() !== ''
        ).map(val => typeof val === 'boolean' ? String(val) : val))];

        // If we already have a color generator, use it
        if (_sharedColorGenerator) {
            return _sharedColorGenerator;
        }

        // Generate categorical colors with consistent strategy
        const colors = generateCategoricalColors(cleanValues.length);

        // Create a color mapping generator
        _sharedColorGenerator = {
            _colorMap: new Map(),

            getColor: function(value) {
                // Convert boolean values to strings for consistent lookup
                const lookupValue = typeof value === 'boolean' ? String(value) : value;

                // If color already assigned, return it
                if (this._colorMap.has(lookupValue)) {
                    return this._colorMap.get(lookupValue);
                }

                // If we've run out of colors, cycle back
                const index = this._colorMap.size % colors.length;
                const color = colors[index];

                // Store and return the color
                this._colorMap.set(lookupValue, color);
                return color;
            }
        };

        return _sharedColorGenerator;
    }

    /**
     * Generate a categorical color palette
     * @param {number} count - Number of colors to generate
     * @returns {Array} List of color strings
     */
    function generateCategoricalColors(count) {
        const baseColors = [
            '#1F77B4', // muted blue
            '#FF7F0E', // safety orange
            '#2CA02C', // cooked asparagus green
            '#D62728', // brick red
            '#9467BD', // muted purple
            '#8C564B', // chestnut brown
            '#E377C2', // raspberry yogurt pink
            '#7F7F7F', // middle gray
            '#BCBD22', // curry yellow-green
            '#17BECF'  // blue-teal
        ];

        // If count is small, return a subset of base colors
        if (count <= baseColors.length) {
            return baseColors.slice(0, count);
        }

        // If more colors needed, generate additional colors
        const colors = [...baseColors];
        while (colors.length < count) {
            // Generate a new color by slightly shifting hue
            const lastColor = colors[colors.length - 1];
            const newColor = shiftColor(lastColor);
            colors.push(newColor);
        }

        return colors;
    }

    /**
     * Shift color slightly to create a new unique color
     * @param {string} baseColor - Base color to shift
     * @returns {string} New color
     */
    function shiftColor(baseColor) {
        // Convert hex to HSL
        const rgb = hexToRgb(baseColor);
        let [h, s, l] = rgbToHsl(rgb.r, rgb.g, rgb.b);

        // Shift hue
        h = (h + 30) % 360;

        // Slightly vary saturation and lightness
        s = Math.min(100, s + 10);
        l = (l + 20) % 100;

        // Convert back to hex
        return hslToHex(h, s, l);
    }

    /**
     * Convert hex color to RGB
     * @param {string} hex - Hex color string
     * @returns {Object} RGB values
     */
    function hexToRgb(hex) {
        const shorthandRegex = /^#?([a-f\d])([a-f\d])([a-f\d])$/i;
        hex = hex.replace(shorthandRegex, (m, r, g, b) => r + r + g + g + b + b);
        const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result ? {
            r: parseInt(result[1], 16),
            g: parseInt(result[2], 16),
            b: parseInt(result[3], 16)
        } : null;
    }

    /**
     * Convert RGB to HSL
     * @param {number} r - Red value
     * @param {number} g - Green value
     * @param {number} b - Blue value
     * @returns {Array} HSL values
     */
    function rgbToHsl(r, g, b) {
        r /= 255, g /= 255, b /= 255;
        const max = Math.max(r, g, b), min = Math.min(r, g, b);
        let h, s, l = (max + min) / 2;

        if (max === min) {
            h = s = 0; // achromatic
        } else {
            const d = max - min;
            s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
            switch (max) {
                case r: h = (g - b) / d + (g < b ? 6 : 0); break;
                case g: h = (b - r) / d + 2; break;
                case b: h = (r - g) / d + 4; break;
            }
            h /= 6;
        }

        return [
            Math.round(h * 360),
            Math.round(s * 100),
            Math.round(l * 100)
        ];
    }

    /**
     * Convert HSL to hex
     * @param {number} h - Hue
     * @param {number} s - Saturation
     * @param {number} l - Lightness
     * @returns {string} Hex color
     */
    function hslToHex(h, s, l) {
        h /= 360;
        s /= 100;
        l /= 100;
        let r, g, b;
        if (s === 0) {
            r = g = b = l; // achromatic
        } else {
            const hue2rgb = (p, q, t) => {
                if (t < 0) t += 1;
                if (t > 1) t -= 1;
                if (t < 1/6) return p + (q - p) * 6 * t;
                if (t < 1/2) return q;
                if (t < 2/3) return p + (q - p) * (2/3 - t) * 6;
                return p;
            };
            const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
            const p = 2 * l - q;
            r = hue2rgb(p, q, h + 1/3);
            g = hue2rgb(p, q, h);
            b = hue2rgb(p, q, h - 1/3);
        }
        const toHex = x => {
            const hex = Math.round(x * 255).toString(16);
            return hex.length === 1 ? '0' + hex : hex;
        };
        return `#${toHex(r)}${toHex(g)}${toHex(b)}`;
    }

    /**
     * Get JSON filename from URL parameters or default
     * @returns {string} JSON filename
     */
    function getJsonFilename() {
        const urlParams = new URLSearchParams(window.location.search);
        const jsonParam = urlParams.get('json');

        if (jsonParam) {
            return jsonParam;
        }

        // Check if there's a data attribute in the HTML
        const dataFilename = document.querySelector('meta[name="json-filename"]')?.getAttribute('content');
        if (dataFilename) {
            return dataFilename;
        }

        // If template variable wasn't replaced, check if we can extract it from the URL
        const pathParts = window.location.pathname.split('/');
        const lastPart = pathParts[pathParts.length - 1];

        if (lastPart && lastPart !== "" && !lastPart.includes('{{')) {
            return lastPart;
        }

        // Fallback to a known filename if available
        return 'unified_map_20250224_175106.json';
    }

    /**
     * Calculate point radius based on count
     * @param {Object} node - Point data
     * @returns {number} Radius in pixels
     */
    function calculatePointRadius(node) {
        // Base size for points
        const baseRadius = 12;
        const count = parseInt(node.occurrence_count || node.total_count || 1);
        return Math.max(baseRadius, baseRadius * Math.sqrt(count));
    }

    /**
     * Create popup content HTML for a data point
     * @param {Object} node - Data point
     * @returns {string} HTML content for popup
     */
    function createPopupContent(node) {
        const sortedFields = AppState.get('sortedFields') || [];
        return `
            <div style="max-width: 300px; max-height: 400px; overflow-y: auto;">
                <h3>Point Details</h3>
                ${sortedFields.map(field => `
                    <div>
                        <strong>${field}:</strong> ${node[field]}
                    </div>
                `).join('')}
            </div>
        `;
    }

    // Reset shared color generator (useful for multiple visualizations)
    function resetColorGenerator() {
        _sharedColorGenerator = null;
    }

    function getNumericColorScale(min, max) {
      // Use a blue-to-red color scale
      return function(value) {
        // Normalize the value between 0 and 1
        const normalized = (value - min) / (max - min);

        // Create a color gradient from blue to red
        // Blue for low values, red for high values
        const r = Math.floor(normalized * 255);
        const b = Math.floor(255 - (normalized * 255));
        const g = Math.floor(100 - (normalized * 50));

        return `rgb(${r}, ${g}, ${b})`;
      };
    }

    function getMostCommonWords(labels, maxWords = 5) {
        const sortedFields = AppState.get('sortedFields') || [];
        const wordFreq = {};
        labels.forEach(label => {
            // Exclude fields from substring calculation
            const filteredLabel = label.toLowerCase().split(/[^a-zA-Z0-9]+/)
                .filter(word =>
                    word.length >= 3 &&
                    !sortedFields.includes(word) &&
                    !word.match(/^[0-9]+$/)
                );

            filteredLabel.forEach(word => {
                wordFreq[word] = (wordFreq[word] || 0) + 1;
            });
        });

        return Object.entries(wordFreq)
            .sort(([,a], [,b]) => b - a)
            .slice(0, maxWords)
            .map(([word, freq]) => `${word} (${freq})`);
    }

    // Public API
    return {
        getColorForValues: getColorForValues,
        getJsonFilename: getJsonFilename,
        calculatePointRadius: calculatePointRadius,
        createPopupContent: createPopupContent,
        resetColorGenerator: resetColorGenerator,
        getMostCommonWords: getMostCommonWords,
        getNumericColorScale: getNumericColorScale
    }
})();