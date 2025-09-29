# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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