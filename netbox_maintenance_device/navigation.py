from netbox.plugins import PluginMenuItem, PluginMenuButton
from django.utils.translation import gettext_lazy as _

menu_items = (
    PluginMenuItem(
        link='plugins:netbox_maintenance_device:upcoming_maintenance',
        link_text=_('Upcoming Maintenance'),
        permissions=['netbox_maintenance_device.view_maintenanceplan'],
        icon_class='mdi-clock-alert-outline'
    ),
    PluginMenuItem(
        link='plugins:netbox_maintenance_device:maintenanceplan_list',
        link_text=_('Maintenance Plans'),
        permissions=['netbox_maintenance_device.view_maintenanceplan'],
        icon_class='mdi-calendar-check',
        buttons=(
            PluginMenuButton(
                link='plugins:netbox_maintenance_device:maintenanceplan_add',
                title=_('Add'),
                icon_class='mdi mdi-plus-thick',
                permissions=['netbox_maintenance_device.add_maintenanceplan']
            ),
        )
    ),
    PluginMenuItem(
        link='plugins:netbox_maintenance_device:maintenanceexecution_list',
        link_text=_('Maintenance Executions'),
        permissions=['netbox_maintenance_device.view_maintenanceexecution'],
        icon_class='mdi-wrench',
        buttons=(
            PluginMenuButton(
                link='plugins:netbox_maintenance_device:maintenanceexecution_add',
                title=_('Add'),
                icon_class='mdi mdi-plus-thick',
                permissions=['netbox_maintenance_device.add_maintenanceexecution']
            ),
        )
    ),
)