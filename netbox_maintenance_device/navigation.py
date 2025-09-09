from netbox.plugins import PluginMenuItem, PluginMenuButton

menu_items = (
    PluginMenuItem(
        link='plugins:netbox_maintenance_device:upcoming_maintenance',
        link_text='Upcoming Maintenance',
        permissions=['netbox_maintenance_device.view_maintenanceplan']
    ),
    PluginMenuItem(
        link='plugins:netbox_maintenance_device:maintenanceplan_list',
        link_text='Maintenance Plans',
        permissions=['netbox_maintenance_device.view_maintenanceplan'],
        buttons=(
            PluginMenuButton(
                link='plugins:netbox_maintenance_device:maintenanceplan_add',
                title='Add',
                icon_class='mdi mdi-plus-thick',
                permissions=['netbox_maintenance_device.add_maintenanceplan']
            ),
        )
    ),
    PluginMenuItem(
        link='plugins:netbox_maintenance_device:maintenanceexecution_list',
        link_text='Maintenance Executions',
        permissions=['netbox_maintenance_device.view_maintenanceexecution'],
        buttons=(
            PluginMenuButton(
                link='plugins:netbox_maintenance_device:maintenanceexecution_add',
                title='Add',
                icon_class='mdi mdi-plus-thick',
                permissions=['netbox_maintenance_device.add_maintenanceexecution']
            ),
        )
    ),
)