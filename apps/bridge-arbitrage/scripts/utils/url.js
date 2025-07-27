const { URL } = require('whatwg-url');

function createURL(url) {
    return new URL(url);
}

function parseURL(url) {
    const urlObj = new URL(url);
    return {
        protocol: urlObj.protocol,
        hostname: urlObj.hostname,
        port: urlObj.port,
        pathname: urlObj.pathname,
        search: urlObj.search,
        hash: urlObj.hash
    };
}

module.exports = {
    createURL,
    parseURL
};
