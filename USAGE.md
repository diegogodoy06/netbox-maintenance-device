# Usage Guide

Complete guide for using the NetBox Maintenance Device Plugin.

## Table of Contents

- [Creating Maintenance Plans](#creating-maintenance-plans)
- [Scheduling Maintenance](#scheduling-maintenance)
- [Completing Maintenance](#completing-maintenance)
- [Monitoring Maintenance](#monitoring-maintenance)
- [Data Models](#data-models)
- [REST API](#rest-api)

---

## Creating Maintenance Plans

1. Navigate to **Plugins > Manutenção de Dispositivos > Planos de Manutenção**
2. Click **Add** to create a new maintenance plan
3. Select a device, provide a name, and set the frequency in days
4. Choose between preventive or corrective maintenance type
5. Save and activate the plan

### Best Practices

- Use descriptive names that indicate the maintenance type (e.g., "Weekly Backup Verification")
- Set realistic frequency intervals based on manufacturer recommendations
- Keep plans active for ongoing monitoring
- Deactivate plans for devices being decommissioned

---

## Scheduling Maintenance

### From Device Page

1. Go to any device detail page
2. View the **Maintenance** section
3. Click the **📅 Schedule** button next to any plan
4. Set date, technician, and notes
5. Confirm to create a scheduled execution

### From Upcoming Maintenance Dashboard

1. Navigate to **Plugins > Upcoming Maintenance**
2. Find the maintenance plan in the table
3. Click **📅 Schedule** in the Actions column
4. Complete the scheduling form

### Scheduling Tips

- Schedule maintenance during maintenance windows
- Add detailed notes about specific tasks to be performed
- Assign a responsible technician for accountability
- Use consistent date formats for better tracking

---

## Completing Maintenance

### Quick Complete

**When to Use**: For overdue or due-soon maintenance that needs immediate action.

1. From the **Upcoming Maintenance** page or device section
2. Click the **✅ Complete** button for overdue/due maintenance
3. Add technician notes and confirm
4. The system automatically marks the execution as completed

> **Note**: The Complete button only appears when there's a pending execution (scheduled or in progress)

### Manual Recording

**When to Use**: For recording maintenance that was performed outside the system.

1. Navigate to **Plugins > Maintenance Executions**
2. Click **Add** to record a new execution
3. Select the plan, set dates, and update status
4. Add detailed notes and technician information

### Completion Best Practices

- Always add meaningful notes about work performed
- Record actual completion time for accurate tracking
- Include any issues encountered or parts replaced
- Update status promptly to maintain accurate records

---

## Monitoring Maintenance

### Device-Level Monitoring

Each device page includes a **Maintenance** section with:

- **Active Plans**: List of all active maintenance plans
- **Visual Indicators**: 
  - 🔴 Red badge = Overdue
  - 🟡 Yellow badge = Due soon (within 7 days)
  - 🟢 Green = On track
- **Quick Actions**: Schedule and complete buttons for urgent items
- **Recent Activity**: Last 5 maintenance executions

### Dashboard Monitoring

The **Upcoming Maintenance** dashboard provides:

#### Statistics Cards

- **Overdue**: Maintenance past due date (red)
- **Due Soon**: Maintenance due within 7 days (yellow)
- **Upcoming**: Maintenance due within 30 days (blue)
- **On Track**: All other active plans (green)

#### Table Features

- **Sortable Columns**: Click headers to sort by any column
- **Status Badges**: Visual indicators for each plan
- **Days Until Due**: Shows countdown or overdue days
- **Quick Actions**: Schedule and complete directly from table

#### Filtering Options

- Filter by device
- Filter by maintenance type
- Filter by status
- Search by plan name

---

## Data Models

### MaintenancePlan

Defines recurring maintenance requirements for devices.

| Field | Type | Description |
|-------|------|-------------|
| `device` | ForeignKey | Links to a specific NetBox device |
| `name` | CharField | Descriptive name for the maintenance type |
| `maintenance_type` | CharField | Type: `preventive` or `corrective` |
| `frequency_days` | IntegerField | Maintenance interval in days |
| `is_active` | BooleanField | Active/inactive flag |
| `description` | TextField | Optional detailed description |

**Methods**:
- `get_next_maintenance_date()`: Calculate next due date
- `days_until_due()`: Calculate days until next maintenance
- `is_overdue()`: Check if maintenance is overdue

### MaintenanceExecution

Records individual maintenance events.

| Field | Type | Description |
|-------|------|-------------|
| `maintenance_plan` | ForeignKey | Links to the maintenance plan |
| `scheduled_date` | DateTimeField | When maintenance is scheduled |
| `completed_date` | DateTimeField | When maintenance was completed |
| `status` | CharField | Status: `scheduled`, `in_progress`, `completed`, `cancelled` |
| `technician` | CharField | Person responsible for maintenance |
| `notes` | TextField | Detailed maintenance notes |
| `completed` | BooleanField | Quick flag for completion status |

**Status Options**:
- `scheduled`: Maintenance is scheduled but not started
- `in_progress`: Work is currently being performed
- `completed`: Maintenance successfully finished
- `cancelled`: Maintenance was cancelled

---

## REST API

The plugin provides a complete REST API for external integrations and automation.

### Available Endpoints

| Endpoint | Operations | Description |
|----------|------------|-------------|
| `/api/plugins/maintenance-device/maintenance-plans/` | CRUD + Custom Actions | Manage maintenance plans |
| `/api/plugins/maintenance-device/maintenance-executions/` | CRUD + Custom Actions | Manage maintenance executions |
| `/api/plugins/maintenance-device/maintenance-plans/overdue/` | GET | Get overdue plans |
| `/api/plugins/maintenance-device/maintenance-plans/upcoming/` | GET | Get upcoming plans |
| `/api/plugins/maintenance-device/maintenance-plans/statistics/` | GET | Get plan statistics |
| `/api/plugins/maintenance-device/maintenance-executions/pending/` | GET | Get pending executions |

### Example API Calls

#### Get All Maintenance Plans

```bash
curl -X GET "https://netbox.example.com/api/plugins/maintenance-device/maintenance-plans/" \
  -H "Authorization: Token YOUR_API_TOKEN" \
  -H "Accept: application/json"
```

#### Create a Maintenance Plan

```bash
curl -X POST "https://netbox.example.com/api/plugins/maintenance-device/maintenance-plans/" \
  -H "Authorization: Token YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "device": 1,
    "name": "Monthly Backup Verification",
    "maintenance_type": "preventive",
    "frequency_days": 30,
    "is_active": true
  }'
```

#### Get Overdue Maintenance

```bash
curl -X GET "https://netbox.example.com/api/plugins/maintenance-device/maintenance-plans/overdue/" \
  -H "Authorization: Token YOUR_API_TOKEN" \
  -H "Accept: application/json"
```

#### Schedule Maintenance

```bash
curl -X POST "https://netbox.example.com/api/plugins/maintenance-device/maintenance-executions/" \
  -H "Authorization: Token YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "maintenance_plan": 1,
    "scheduled_date": "2025-10-15T10:00:00Z",
    "technician": "John Doe",
    "notes": "Regular scheduled maintenance"
  }'
```

#### Complete Maintenance

```bash
curl -X PATCH "https://netbox.example.com/api/plugins/maintenance-device/maintenance-executions/1/" \
  -H "Authorization: Token YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed",
    "completed_date": "2025-10-15T12:00:00Z",
    "completed": true,
    "notes": "Maintenance completed successfully. All systems operational."
  }'
```

#### Get Statistics

```bash
curl -X GET "https://netbox.example.com/api/plugins/maintenance-device/maintenance-plans/statistics/" \
  -H "Authorization: Token YOUR_API_TOKEN" \
  -H "Accept: application/json"
```

### API Authentication

All API requests require authentication using a NetBox API token:

1. Generate a token in NetBox: **Admin > Users > API Tokens**
2. Include the token in the `Authorization` header: `Token YOUR_API_TOKEN`
3. Ensure the token has appropriate permissions for maintenance operations

### API Permissions

Required permissions for different operations:

- **View**: `netbox_maintenance_device.view_maintenanceplan`, `netbox_maintenance_device.view_maintenanceexecution`
- **Add**: `netbox_maintenance_device.add_maintenanceplan`, `netbox_maintenance_device.add_maintenanceexecution`
- **Change**: `netbox_maintenance_device.change_maintenanceplan`, `netbox_maintenance_device.change_maintenanceexecution`
- **Delete**: `netbox_maintenance_device.delete_maintenanceplan`, `netbox_maintenance_device.delete_maintenanceexecution`

---

## Troubleshooting

### Common Issues

#### Buttons Not Working

If Schedule or Complete buttons don't open modals:
- Clear browser cache and reload
- Check browser console for JavaScript errors
- Ensure NetBox version is 4.0+

#### Sorting Not Working

If table columns can't be sorted:
- Verify migrations are up to date: `python manage.py migrate`
- Check for any error messages in NetBox logs

#### Maintenance Not Appearing on Device Page

If maintenance section is missing:
- Verify plugin is properly installed: `pip list | grep netbox-maintenance-device`
- Check plugin is enabled in `configuration.py`
- Restart NetBox services

---

## Support

For issues, feature requests, or questions:

- **GitHub Issues**: [netbox-maintenance-device/issues](https://github.com/diegogodoy06/netbox-maintenance-device/issues)
- **Documentation**: [README.md](README.md)
- **Installation Guide**: [DOCKER_INSTALL.md](DOCKER_INSTALL.md)

---

**Last Updated**: October 2025  
**Plugin Version**: 1.2.1  
**NetBox Compatibility**: 4.0+
