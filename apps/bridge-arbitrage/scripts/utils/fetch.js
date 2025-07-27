const { fetch } = require('node-fetch');

// Custom fetch function that uses WHATWG URL API
async function customFetch(url, options = {}) {
    // Create URL object to handle encoding
    const urlObj = new URL(url);
    
    // Handle query parameters
    if (options.body && typeof options.body === 'object') {
        options.body = JSON.stringify(options.body);
        options.headers = {
            ...options.headers,
            'Content-Type': 'application/json'
        };
    }

    return fetch(urlObj.toString(), options);
}

module.exports = customFetch;
