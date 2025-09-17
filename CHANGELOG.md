# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.1] - 2025-09-17

### Added
- **Automatic Database Healing**: Plugin now automatically detects and resolves orphaned table issues
- **Enhanced Migration System**: Migration `0002_cleanup_notifications.py` handles database cleanup
- **Model-Level Safety Checks**: MaintenancePlan and MaintenanceExecution models include integrity verification
- **Database Healer Module**: Comprehensive auto-healing functionality for common database issues
- **Signal Handlers**: Post-migration signal handling for automatic cleanup
- **Configuration Options**: New `auto_heal_database` configuration option

### Fixed
- **[CRÍTICO] IntegrityError Resolution**: Automatically resolves foreign key constraint violations from orphaned notification tables
- **[CRÍTICO] collectstatic AttributeError**: Fixed `'MaintenanceDeviceConfig' object has no attribute 'get_config'` during Docker builds
- **[CRÍTICO] Manager AttributeError**: Fixed `'MaintenanceDeviceManager' object has no attribute 'restrict'` by removing custom manager
- **Database Consistency**: Ensures database integrity during save/delete operations
- **Migration Safety**: Enhanced migration process with multi-database support
- **Docker Build Compatibility**: Plugin now initializes safely during collectstatic operations

### Changed
- **Plugin Version**: Updated to 1.2.1
- **NetBox Compatibility**: Narrowed to 4.4.x for this release (following best practices)
- **Versioning Strategy**: Using conservative version ranges instead of broad compatibility claims
- **Plugin Description**: Enhanced description with Portuguese-BR support mention
- **Model Managers**: Added custom manager with safety check capabilities
- **Error Handling**: Improved error handling during database operations

### Technical Details
- Orphaned `netbox_maintenance_device_maintenancenotification` table is automatically detected and removed
- Foreign key constraints are safely dropped before table removal
- Multi-database support (PostgreSQL, SQLite, and others)
- Graceful failure handling - plugin continues to work even if auto-healing fails
- Comprehensive logging for troubleshooting

### Migration Notes
- Users upgrading from previous versions will benefit from automatic database healing
- No manual intervention required - all fixes are applied automatically
- Migration is irreversible but safe (only removes orphaned data)

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