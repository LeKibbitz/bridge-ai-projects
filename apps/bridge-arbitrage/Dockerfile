FROM node:18-alpine as builder

WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install \
    path-browserify \
    os-browserify \
    stream-browserify \
    crypto-browserify \
    buffer \
    react-app-rewired \
    customize-cra

# Copy source code
COPY . .

# Create a config-overrides.js for webpack
RUN printf "const { override } = require('customize-cra');\nmodule.exports = override(\n    config => {\n        config.resolve.fallback = {\n            path: require.resolve('path-browserify'),\n            os: require.resolve('os-browserify/browser'),\n            stream: require.resolve('stream-browserify'),\n            crypto: require.resolve('crypto-browserify'),\n            buffer: require.resolve('buffer/')\n        };\n        return config;\n    }\n);\n" > config-overrides.js

# Build the app using react-app-rewired
RUN npm run build

# Production image
FROM nginx:alpine

WORKDIR /usr/share/nginx/html

# Copy built files
COPY --from=builder /app/build .

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
