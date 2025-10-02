# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.2] - 2025-10-02

### Fixed
- **[CRÍTICO] Action Buttons Not Working**: Fixed Schedule and Complete buttons not responding to clicks (Issues #8)
  - Removed jQuery dependency due to loading issues (453+ retry attempts)
  - Complete rewrite using vanilla JavaScript with native Fetch API
  - Implemented proper event delegation for dynamically loaded content
  - Added Bootstrap 5/4/fallback support for modal compatibility
  - Fixed CSRF token handling for AJAX requests
- **[CRÍTICO] Table Sorting Issues**: Added proper sorting functionality to maintenance tables (Issue #9)
  - Added database annotations for computed fields (`_next_due_date`, `_days_until`, `_status_priority`)
  - Fixed "Cannot resolve keyword 'status' into field" error in MaintenancePlanTable
  - Enabled sorting for Next Due, Days Until Due, and Status columns
  - Made non-sortable columns properly marked as `orderable=False`
- **Complete Button Logic**: Fixed Complete button appearing incorrectly
  - Button now only shows when there's a pending execution (scheduled or in_progress)
  - Changed from plan-based logic to execution-based logic
  - Uses `execution_id` instead of `plan_id` for completion
  - Applied fix to all pages: upcoming maintenance, device section, and device tab
- **Modal Close Functionality**: Fixed modal close buttons
  - Removed X (close) buttons from all modals, keeping only Cancel button
  - Fixed Cancel button functionality with proper event handlers
  - Added `hideModal()` function with Bootstrap 5/4/vanilla fallback
- **Default Notes Removed**: Schedule maintenance no longer adds default "Scheduled via quick action" notes
- **Vanilla JavaScript Implementation**: All three templates converted from jQuery to vanilla JavaScript
  - `upcoming_maintenance.html` - Main maintenance table with quick actions
  - `device_maintenance_section.html` - Device page maintenance section
  - `device_maintenance_tab.html` - Device maintenance tab page

### Added
- **Statistics Cards**: New visual dashboard showing maintenance status overview
  - Overdue count with red styling
  - Due Soon count (within 7 days) with yellow styling
  - Upcoming count (within 30 days) with blue styling
  - On Track count with green styling
  - Cards include icons and hover effects
  - Dark mode support for all statistics cards
- **Separate Usage Documentation**: Created comprehensive `USAGE.md` file
  - Detailed usage instructions moved from README
  - Complete REST API examples and authentication guide
  - Troubleshooting section with common issues
  - Data models documentation with field descriptions
  - Best practices for scheduling and completing maintenance

### Changed
- **JavaScript Architecture**: Complete modernization to vanilla JavaScript
  - Removed jQuery dependency entirely
  - Uses native Fetch API for AJAX requests
  - Native event delegation with `document.addEventListener`
  - Better error handling and user feedback
  - Improved modal management across Bootstrap versions
- **Documentation Structure**: README.md reorganized for better clarity
  - Usage section moved to separate `USAGE.md` file
  - Quick start guide added to README
  - Links to detailed documentation files
  - Cleaner, more focused README content

### Technical Details
- **Files Modified**:
  - `netbox_maintenance_device/views.py` - Added query annotations and statistics calculation
  - `netbox_maintenance_device/tables.py` - Fixed sorting, button logic, and orderable columns
  - `netbox_maintenance_device/templates/netbox_maintenance_device/upcoming_maintenance.html` - Vanilla JS rewrite, statistics cards
  - `netbox_maintenance_device/templates/netbox_maintenance_device/device_maintenance_section.html` - Vanilla JS, button logic fix
  - `netbox_maintenance_device/templates/netbox_maintenance_device/device_maintenance_tab.html` - Vanilla JS conversion
  - `netbox_maintenance_device/static/netbox_maintenance_device/css/maintenance.css` - Statistics card styling
  - `README.md` - Documentation restructure
  - `USAGE.md` - New comprehensive usage guide

## [1.2.1] - 2025-09-29

### Added
- **Complete REST API**: Full CRUD API implementation for external integrations
  - 17 API endpoints for maintenance plans and executions
  - Advanced filtering, pagination, and ordering
  - Custom actions: schedule, complete, cancel maintenance
  - Statistics and reporting endpoints
  - Comprehensive permission system
  - Token and session authentication support
- **NetBox 4.4.x Compatibility**: Full compatibility with NetBox 4.4.1
- **Enhanced Database Healing**: Plugin automatically detects and resolves orphaned table issues
- **Production Deployment Ready**: Cleaned project structure for production use
- **GitHub Actions Integration**: Automated testing and PyPI publishing workflows

### Fixed
- **[CRÍTICO] NetBox 4.4.x Compatibility**: Resolved all compatibility issues with NetBox 4.4.1
  - Fixed `ModuleNotFoundError: No module named 'utilities.utils'`
  - Fixed `ImportError: cannot import name 'NestedDeviceSerializer'`
  - Updated permission system to use `rest_framework.permissions.BasePermission`
  - Created custom `DeviceNestedSerializer` for NetBox 4.4.x compatibility
- **[CRÍTICO] IntegrityError Resolution**: Automatically resolves foreign key constraint violations
- **[CRÍTICO] Internationalization**: Fixed menu labels appearing in Portuguese when NetBox is set to English
- **Docker Deployment**: Plugin now starts correctly in NetBox 4.4.1 containers

### Changed
- **Permission System**: Completely rewritten for NetBox 4.4.x compatibility
- **API Serializers**: Updated to use NetBox 4.4.x compatible imports
- **Project Structure**: Cleaned for production deployment (removed unnecessary documentation files)
- **Package Naming**: Standardized to `netbox-maintenance-device` for PyPI
- **License Format**: Updated to standard `Apache-2.0` format

## [1.2.0] - 2025-09-16

### Added
- Enhanced visual indicators for maintenance status
- Portuguese-BR localization support
- Improved navigation and menu structure
- Device maintenance integration tabs

### Fixed
- Various UI improvements
- Better error handling in views

## [1.1.0] - 2025-09-15

### Added
- Initial release with basic maintenance planning
- Device maintenance plan management
- Maintenance execution tracking
- Basic reporting and dashboard

### Features
- Create maintenance plans for devices
- Track maintenance executions
- Monitor upcoming and overdue maintenance
- Device integration with maintenance history