#!/bin/bash

# Script to toggle maintenance mode on/off

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    exit 1
fi

# Check current maintenance mode status
current_status=$(grep "MAINTENANCE_MODE=" .env | cut -d= -f2)

if [ "$current_status" == "True" ]; then
    # Disable maintenance mode
    sed -i 's/MAINTENANCE_MODE=True/MAINTENANCE_MODE=False/g' .env
    echo "✅ Maintenance mode disabled"
else
    # Enable maintenance mode
    sed -i 's/MAINTENANCE_MODE=False/MAINTENANCE_MODE=True/g' .env
    echo "🔧 Maintenance mode enabled"
    
    # Check if allowed IPs are configured
    allowed_ips=$(grep "MAINTENANCE_ALLOWED_IPS=" .env | cut -d= -f2)
    if [ "$allowed_ips" == "127.0.0.1,your-ip-address" ]; then
        echo "⚠️ Warning: Default allowed IPs detected. You may want to update MAINTENANCE_ALLOWED_IPS in .env"
        echo "   Current value: $allowed_ips"
        
        # Get current IP
        current_ip=$(curl -s https://api.ipify.org)
        if [ -n "$current_ip" ]; then
            echo "   Your current public IP appears to be: $current_ip"
            
            read -p "   Would you like to add this IP to allowed IPs? (y/n): " add_ip
            if [ "$add_ip" == "y" ] || [ "$add_ip" == "Y" ]; then
                sed -i "s/MAINTENANCE_ALLOWED_IPS=.*/MAINTENANCE_ALLOWED_IPS=127.0.0.1,$current_ip/g" .env
                echo "   ✅ Updated MAINTENANCE_ALLOWED_IPS to include your IP"
            fi
        fi
    fi
fi

# If running with Docker, restart the web container
if [ -f docker-compose.yml ]; then
    read -p "Do you want to restart the web container to apply changes? (y/n): " restart
    if [ "$restart" == "y" ] || [ "$restart" == "Y" ]; then
        docker-compose restart web
        echo "✅ Web container restarted"
    else
        echo "⚠️ Remember to restart the web container for changes to take effect"
    fi
fi

echo "Done!"
