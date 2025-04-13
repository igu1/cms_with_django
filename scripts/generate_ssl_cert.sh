#!/bin/bash

# Script to generate self-signed SSL certificates for development

# Create directories if they don't exist
mkdir -p nginx/ssl

# Generate self-signed certificate
echo "Generating self-signed SSL certificate for development..."
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

# Set permissions
chmod 600 nginx/ssl/key.pem
chmod 600 nginx/ssl/cert.pem

echo "Self-signed SSL certificate generated successfully!"
echo "Certificate location: nginx/ssl/cert.pem"
echo "Key location: nginx/ssl/key.pem"
echo ""
echo "NOTE: This is for development only. Use proper certificates for production."
