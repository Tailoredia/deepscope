/**
 * App State Module
 * Central state management for the application
 */
const AppState = (function() {
    // Private state object
    const _state = {
        map: null,
        markers: null,
        rawData: [],
        sortedFields: [],
        currentColorField: null,
        colorMap: new Map(),
        colorLegendFilter: new Set(), // Re-added for legend filtering
        selectedFields: []
    };

    /**
     * Get a value from state
     * @param {string} key - State key
     * @returns {*} State value
     */
    function get(key) {
        return _state[key];
    }

    /**
     * Set a value in state
     * @param {string} key - State key
     * @param {*} value - Value to set
     */
    function set(key, value) {
        _state[key] = value;
    }

    /**
     * Get all state values
     * @returns {Object} State object
     */
    function getAll() {
        return {..._state};
    }

    /**
     * Reset the state to its initial configuration
     */
    function reset() {
        // Reset core values
        _state.map = null;
        _state.markers = null;
        _state.rawData = [];
        _state.sortedFields = [];
        _state.currentColorField = null;
        _state.colorMap = new Map();
        _state.colorLegendFilter = new Set();
        _state.selectedFields = [];

        // Clear any field-specific filters
        Object.keys(_state)
            .filter(key => key.endsWith('Filters'))
            .forEach(key => delete _state[key]);
    }

    // Public API
    return {
        get: get,
        set: set,
        getAll: getAll,
        reset: reset
    };
})();