/**
 * Unified API Client for making requests with loading overlay support
 * Usage: APIClient.request(endpoint, method, data, options)
 */
class APIClient {
    /**
     * Make an API request with automatic loading overlay management
     * @param {string} endpoint - API endpoint URL
     * @param {string} method - HTTP method (GET, POST, PUT, DELETE, etc.)
     * @param {Object} data - Data to send with the request
     * @param {Object} options - Additional options
     *   - loadingText: Custom loading text (default: 'Loading...')
     *   - showOverlay: Whether to show loading overlay (default: true)
     *   - timeout: Request timeout in milliseconds (default: 30000)
     * @returns {Promise} Response JSON
     */
    static async request(endpoint, method = 'GET', data = null, options = {}) {
        const {
            loadingText = 'Loading...',
            showOverlay = true,
            timeout = 30000
        } = options;

        try {
            // Show loading overlay if enabled
            if (showOverlay && window.LoadingOverlay) {
                window.LoadingOverlay.show(loadingText);
            }

            // Prepare request options
            const requestOptions = {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            };

            // Get CSRF token from cookie if available
            const csrfToken = this.getCookie('csrftoken');
            if (csrfToken) {
                requestOptions.headers['X-CSRFToken'] = csrfToken;
            }

            // Add body for POST, PUT, PATCH requests
            if (method !== 'GET' && method !== 'HEAD' && data) {
                requestOptions.body = JSON.stringify(data);
            }

            // Set timeout
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), timeout);
            requestOptions.signal = controller.signal;

            // Make the request
            const response = await fetch(endpoint, requestOptions);
            clearTimeout(timeoutId);

            // Parse response
            let responseData;
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                responseData = await response.json();
            } else {
                responseData = await response.text();
            }

            // Hide loading overlay
            if (showOverlay && window.LoadingOverlay) {
                window.LoadingOverlay.hide();
            }

            // Handle non-200 responses
            if (!response.ok) {
                const errorMessage = responseData?.message || `HTTP Error: ${response.status}`;
                throw new Error(errorMessage);
            }

            return responseData;

        } catch (error) {
            // Hide loading overlay
            if (showOverlay && window.LoadingOverlay) {
                window.LoadingOverlay.hide();
            }

            // Handle different error types
            if (error.name === 'AbortError') {
                console.error('Request timeout:', endpoint);
                throw new Error('Request timeout. Please try again.');
            }

            console.error('API Request Error:', error);
            throw error;
        }
    }

    /**
     * GET request helper
     * @param {string} endpoint - API endpoint
     * @param {Object} options - Request options
     * @returns {Promise} Response JSON
     */
    static async get(endpoint, options = {}) {
        return this.request(endpoint, 'GET', null, options);
    }

    /**
     * POST request helper
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Data to send
     * @param {Object} options - Request options
     * @returns {Promise} Response JSON
     */
    static async post(endpoint, data = {}, options = {}) {
        return this.request(endpoint, 'POST', data, options);
    }

    /**
     * PUT request helper
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Data to send
     * @param {Object} options - Request options
     * @returns {Promise} Response JSON
     */
    static async put(endpoint, data = {}, options = {}) {
        return this.request(endpoint, 'PUT', data, options);
    }

    /**
     * PATCH request helper
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Data to send
     * @param {Object} options - Request options
     * @returns {Promise} Response JSON
     */
    static async patch(endpoint, data = {}, options = {}) {
        return this.request(endpoint, 'PATCH', data, options);
    }

    /**
     * DELETE request helper
     * @param {string} endpoint - API endpoint
     * @param {Object} options - Request options
     * @returns {Promise} Response JSON
     */
    static async delete(endpoint, options = {}) {
        return this.request(endpoint, 'DELETE', null, options);
    }

    /**
     * Get CSRF token from cookies
     * @param {string} name - Cookie name
     * @returns {string|null} Cookie value
     */
    static getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}

// Make available globally
window.APIClient = APIClient;