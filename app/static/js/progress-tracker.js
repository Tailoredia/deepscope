/**
 * Progress Tracker Module
 * Provides UI for showing loading progress
 */
const ProgressTracker = (function() {
    // Private variables
    let _loadingOverlay = null;
    let _progressBar = null;
    let _loadingText = null;

    // Constructor function
    function createTracker() {
        // Create DOM elements if they don't exist
        if (!_loadingOverlay) {
            _loadingOverlay = document.createElement('div');
            _loadingOverlay.innerHTML = `
                <div id="loading-overlay" style="
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(255, 255, 255, 0.9);
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    z-index: 10000;
                ">
                    <div style="
                        width: 300px;
                        background: white;
                        padding: 20px;
                        border-radius: 8px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    ">
                        <div id="loading-text" style="
                            text-align: center;
                            margin-bottom: 10px;
                            font-family: Arial;
                            color: #333;
                        ">Loading visualization...</div>
                        <div style="
                            width: 100%;
                            height: 4px;
                            background: #eee;
                            border-radius: 2px;
                            overflow: hidden;
                        ">
                            <div id="loading-progress" style="
                                width: 0%;
                                height: 100%;
                                background: #4CAF50;
                                transition: width 0.3s ease;
                            "></div>
                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(_loadingOverlay);

            // Store references to important elements
            _progressBar = document.getElementById('loading-progress');
            _loadingText = document.getElementById('loading-text');
        }

        return {
            /**
             * Update progress display
             * @param {number} percent - Percentage complete (0-100)
             * @param {string} text - Status text to display
             */
            update: function(percent, text) {
                if (_progressBar) _progressBar.style.width = `${percent}%`;
                if (_loadingText) _loadingText.textContent = text;
            },

            /**
             * Hide the progress tracker
             */
            hide: function() {
                const overlay = document.getElementById('loading-overlay');
                if (overlay) {
                    overlay.style.opacity = '0';
                    overlay.style.transition = 'opacity 0.5s ease';
                    setTimeout(() => {
                        if (overlay.parentNode) {
                            overlay.parentNode.removeChild(overlay);
                        }
                        _loadingOverlay = null;
                        _progressBar = null;
                        _loadingText = null;
                    }, 500);
                }
            }
        };
    }

    // Public API
    return {
        /**
         * Create a new progress tracker
         * @returns {Object} Progress tracker instance
         */
        create: createTracker
    };
})();