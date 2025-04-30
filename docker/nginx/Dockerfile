# Use a minimal Alpine-based image
FROM nginx:alpine

# Copy custom Nginx configuration file into the image
COPY nginx.conf /etc/nginx/nginx.conf

# Copy SSL certificates (if you have them)
COPY server.crt /etc/ssl/certs/server.crt
COPY server.key /etc/ssl/private/server.key

# Expose HTTP and HTTPS ports
EXPOSE 80 443

# Start nginx server when container starts
CMD ["nginx", "-g", "daemon off;"]