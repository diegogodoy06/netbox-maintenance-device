# Django translation settings for netbox_maintenance_device plugin

# Add this to your NetBox configuration.py or local settings:

# Enable internationalization
USE_I18N = True
USE_L10N = True

# Language settings
LANGUAGE_CODE = 'pt-br'  # Set to Portuguese Brazilian by default
TIME_ZONE = 'America/Sao_Paulo'  # Brazilian timezone

# Available languages
LANGUAGES = [
    ('en', 'English'),
    ('pt-br', 'Português (Brasil)'),
]

# Locale paths for the plugin
LOCALE_PATHS = [
    '/opt/netbox/netbox/netbox_maintenance_device/locale',
]

# If using custom NetBox installation, adjust the path accordingly
# Example for different installations:
# - Docker: '/opt/netbox/netbox/netbox_maintenance_device/locale'
# - Local dev: '/path/to/your/netbox/netbox_maintenance_device/locale'
