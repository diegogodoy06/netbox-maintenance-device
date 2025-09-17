from netbox.plugins import PluginMenu, PluginMenuItem, PluginMenuButton
from django.utils.translation import gettext_lazy as _

# Criar menu customizado ao invés de usar o menu padrão "Plugins"
menu = PluginMenu(
    label=_('Device Maintenance'),
    groups=(
        (_('Maintenance'), (
            PluginMenuItem(
                link='plugins:netbox_maintenance_device:upcoming_maintenance',
                link_text=_('Upcoming Maintenance'),
                permissions=['netbox_maintenance_device.view_maintenanceplan']
            ),
            PluginMenuItem(
                link='plugins:netbox_maintenance_device:maintenanceplan_list',
                link_text=_('Maintenance Plans'),
                permissions=['netbox_maintenance_device.view_maintenanceplan'],
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
                buttons=(
                    PluginMenuButton(
                        link='plugins:netbox_maintenance_device:maintenanceexecution_add',
                        title=_('Add'),
                        icon_class='mdi mdi-plus-thick',
                        permissions=['netbox_maintenance_device.add_maintenanceexecution']
                    ),
                )
            ),
        )),
    ),
    icon_class='mdi mdi-wrench-cog'
)