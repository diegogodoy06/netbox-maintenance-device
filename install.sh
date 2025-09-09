#!/bin/bash

# NetBox Maintenance Device Plugin Installation Script

echo "NetBox Maintenance Device Plugin Installation"
echo "=============================================="

# Check if NetBox is installed
if [ ! -d "/opt/netbox" ] && [ ! -d "$NETBOX_ROOT" ]; then
    echo "Warning: NetBox installation not found in standard locations."
    echo "Please ensure NetBox is installed and NETBOX_ROOT is set if using a custom location."
fi

# Install the plugin
echo "Installing plugin..."
pip install .

echo ""
echo "Installation complete!"
echo ""
echo "Next steps:"
echo "1. Add 'netbox_maintenance_device' to PLUGINS in your NetBox configuration.py"
echo "2. Run 'python manage.py migrate' to create database tables"
echo "3. Restart your NetBox services"
echo ""
echo "Example configuration.py entry:"
echo "PLUGINS = ["
echo "    'netbox_maintenance_device',"
echo "]"
echo ""
echo "For more information, see README.md"