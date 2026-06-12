# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.2] - 2026-06-12

### Added

- **NetBox event system integration (#20)**: maintenance activity now fires native NetBox events, so event rules can trigger webhooks, notifications, and scripts.
  - Three custom event types registered at startup: `maintenance_due` (warning), `maintenance_scheduled` (info), and `maintenance_completed` (success).
  - Events fire automatically when a `MaintenanceExecution` is scheduled or completed.
  - New `CheckMaintenanceJob` system job and `check_maintenance` management command periodically detect overdue plans and fire `maintenance_due` events.
  - `MaintenancePlan` tracks the last notified date to prevent duplicate `maintenance_due` events for the same cycle.
- Filter forms for `MaintenancePlan` and `MaintenanceExecution` list views.

### Fixed

- **NetBox < 4.6 compatibility** in the events migration and payload:
  - Migration `0004` depended on `extras.0138` (which only ships with NetBox 4.6.0), making `migrate` fail with `NodeNotFoundError` on NetBox 4.4 / 4.5. It now depends on `extras.__latest__`, matching the plugin's other migrations.
  - Event payloads now include the serialized object data eagerly. Without it, the plain-dict queue path (NetBox ≤ 4.5 fallback and the immediate-flush branch used by `check_maintenance` / `CheckMaintenanceJob`) raised `KeyError`, so `maintenance_due` notifications never fired outside an HTTP request.

### Technical Details

Files Modified / Added:

- `netbox_maintenance_device/__init__.py` — custom event type registration, system jobs loading, version bump to `1.4.2`.
- `netbox_maintenance_device/events.py` — new core events module; dispatches events safely within and outside HTTP request contexts.
- `netbox_maintenance_device/jobs.py` — new `CheckMaintenanceJob` system job.
- `netbox_maintenance_device/management/commands/check_maintenance.py` — new management command.
- `netbox_maintenance_device/migrations/0004_remove_maintenanceplan_last_executed_and_more.py` — last-notified tracking field, `extras.__latest__` dependency.
- `netbox_maintenance_device/models.py` — event dispatch on schedule / complete, last-notified tracking.
- `netbox_maintenance_device/forms.py` — filter forms.
- `pyproject.toml` — version bump to `1.4.2`.

## [1.4.1] - 2026-05-14

### Fixed

- **Crash on Maintenance Plan create/edit (`AttributeError: 'NoneType' object has no attribute 'get'`)** on NetBox 4.6 / Django 6.0. `NetBoxModelForm.clean()` modifies `self.cleaned_data` in place and does not always return it, so `super().clean()` was sometimes `None`. The plugin now reads from `self.cleaned_data` directly.
- **Unreadable Device / VM badges** on the Maintenance Plans and Upcoming Maintenance tables. Bootstrap 5's `bg-secondary` / `bg-info` don't auto-set the foreground color in NetBox 4.6's theme, producing low-contrast text. Replaced with `text-bg-primary` (Device) and `text-bg-info` (VM), which set both background and contrasting text in one utility class.

### Changed

- **Plan form UX (#15 follow-up)**: relabeled the schedule fields to make calendar scheduling discoverable.
  - `Frequency` → `Repeat every`
  - `Frequency Unit` → `Unit`
  - `Anchor Date` → `Calendar anchor (optional)` with a worked example in help text ("pick any 1st-of-month to schedule on the 1st of every month; pick 2026-01-01 with unit 'quarters' to land on Jan 1 / Apr 1 / Jul 1 / Oct 1").
  - Grouped fields into `FieldSet`s (`Plan`, `Target`, `Schedule`, `Tags`) so the schedule controls read as one unit.
- **Device / Virtual Machine field locking** on the plan form: picking one now disables the other client-side via a small static JS file (`static/netbox_maintenance_device/js/plan_target_toggle.js`, loaded via `form.Media`). The server-side XOR validation remains as a safety net.
- **Upcoming & Overdue Maintenance**: added a filter bar above the table with **Status** (Overdue / Due Soon / Upcoming / On Track), **Maintenance Type**, and **Target** (Device / VM). Filtering happens in `UpcomingMaintenanceView.get_queryset` since the status is derived from the Python `days_until_due()` computation that can't be expressed as a single SQL predicate. Statistics cards continue to reflect the *unfiltered* totals so badges don't change with the current view slice.

### Technical Details

Files Modified / Added:

- `netbox_maintenance_device/forms.py` — defensive `clean()`, fieldsets, relabeled schedule fields, `Media.js` reference.
- `netbox_maintenance_device/static/netbox_maintenance_device/js/plan_target_toggle.js` — client-side toggle for Device / VM fields.
- `netbox_maintenance_device/tables.py` — `text-bg-primary` / `text-bg-info` badges.
- `netbox_maintenance_device/templates/netbox_maintenance_device/maintenanceplan.html` — same badge swap on the detail page.
- `netbox_maintenance_device/templates/netbox_maintenance_device/maintenanceexecution.html` — same badge swap on the execution detail page.
- `netbox_maintenance_device/templates/netbox_maintenance_device/upcoming_maintenance.html` — new filter form, empty-state copy updated.
- `netbox_maintenance_device/views.py` — `_classify_plan` helper, status / type / target filtering in `UpcomingMaintenanceView.get_queryset`, stats remain based on the unfiltered base queryset.
- `netbox_maintenance_device/__init__.py` / `pyproject.toml` — version bump to `1.4.1`.

## [1.4.0] - 2026-05-14

### Added

- **Virtual Machine support (#14)**: Maintenance plans can now target either a `dcim.Device` **or** a `virtualization.VirtualMachine`. A new "Maintenance" section appears on VM detail pages with the same UX as devices (active plans, recent activity, schedule / complete actions), plus a dedicated VM maintenance tab at `/plugins/maintenance-device/virtual-machine/<pk>/maintenance/`.
- **Calendar-based scheduling (#15)**: Plans now have a `frequency_unit` (`days` / `weeks` / `months` / `quarters` / `years`) and an optional `anchor_date`. When `anchor_date` is set, the next maintenance is computed as `anchor_date + n * step` strictly after the last execution, eliminating the date drift that affected the legacy day-only schedules. Example: a quarterly plan anchored on Jan 1 stays on Jan 1 / Apr 1 / Jul 1 / Oct 1 indefinitely.
- New `MaintenancePlan.target`, `target_type`, `target_name` helpers; `get_frequency_display()` for human-readable rendering in tables and templates.
- API: `MaintenancePlanSerializer` exposes `virtual_machine`, `frequency_unit`, `anchor_date`, and `target_type`. `MaintenanceExecutionSerializer` exposes `virtual_machine`, `virtual_machine_id`, and `target_type` (legacy `device` / `device_id` fields remain for backward compatibility, now nullable). Filter sets accept `virtual_machine` / `virtual_machine_id` and `frequency_unit`.

### Changed

- **Schema**: `MaintenancePlan.device` is now nullable; new `virtual_machine` FK with the same `related_name='maintenance_plans'`; uniqueness rule replaced by two conditional `UniqueConstraint`s — name unique per device, and independently unique per VM.
- `MaintenancePlan.frequency_days` is now a generic count (`Frequency`), interpreted via `frequency_unit`. Existing rows are preserved unchanged (default `frequency_unit='days'` means previous "Frequency (days)" semantics are kept on upgrade).
- `UpcomingMaintenanceView` queryset no longer relies on SQL-side annotations for the next-due date (multi-unit / anchored math doesn't fit a single SQL expression); next-due / days-until are computed in Python via the model and the existing table fallback. `select_related` for `device` and `virtual_machine` added.
- Tables, list views and detail templates now show a unified "Target" column with a Device / VM badge, an "Anchor" column and a human-readable "Frequency" column.

### Migration

- New `0003_virtual_machine_and_calendar_schedule` migration. Forward-compatible — existing day-based plans keep their behavior; no manual data migration required.

### Closes

- #14 (Feature request - supporting virtual devices)
- #15 (Feature request - Support calendar-based scheduling)

## [1.3.1] - 2026-05-14

### Fixed

- **`TypeError: args or kwargs must be provided.` on NetBox 4.6.x list views**: Affected `/plugins/maintenance-device/maintenance-plans/` and `/plugins/maintenance-device/upcoming/`. Root cause: Django 6.0 (shipped with NetBox 4.6) now raises `TypeError` when `django.utils.html.format_html()` is called without any positional / keyword arguments. Previous Django versions only emitted a `DeprecationWarning`.
- Replaced 10 unsafe `format_html('<span ...>literal</span>')` calls in `netbox_maintenance_device/tables.py` with `mark_safe(...)` (already imported), since those strings are fully static and contain no user input. The one remaining `format_html('... {} ...', abs(days))` call uses a placeholder and a positional arg, which remains valid under Django 6.0.

### Technical Details

Files Modified:

- `netbox_maintenance_device/tables.py` – Replaced `format_html(static_html)` with `mark_safe(static_html)` in `MaintenancePlanTable.render_status`, `UpcomingMaintenanceTable.render_days_until`, `UpcomingMaintenanceTable.render_status`, and `UpcomingMaintenanceTable.render_actions`.
- `netbox_maintenance_device/__init__.py` – Bumped `version` to `1.3.1`.
- `pyproject.toml` – Bumped version to `1.3.1`.
- `README.md` / `USAGE.md` / `CHANGELOG.md` – Version references updated.

## [1.3.0] - 2026-05-14

### Added

- **NetBox 4.6.x Compatibility**: Full compatibility with NetBox 4.6.0 and later (extended supported version range to `4.4.0` – `4.6.99` via `max_version`).
- Verified plugin loads and runs against NetBox 4.6.x (Django 6.0).
- Confirmed all plugin APIs used by this plugin remain stable in 4.6: `NetBoxModel`, `NetBoxModelForm`, `NetBoxModelFilterSet`, `NetBoxTable`, `NetBoxModelSerializer`, `WritableNestedSerializer`, `NetBoxModelViewSet`, `NetBoxRouter`, `PluginConfig`, `PluginMenu`, `PluginMenuItem`, `PluginMenuButton`, `PluginTemplateExtension`, and `netbox.views.generic.*`.

### Changed

- **Version**: Bumped plugin version to `1.3.0`.
- **Documentation**: Updated compatibility table, badges and installation examples to reference NetBox 4.6.x and plugin version `1.3.0`.

### Fixed

- **Plugin failing to load on NetBox 4.6.x**: Root cause was the strict `max_version = '4.5.99'` declaration in `PluginConfig`, which made NetBox 4.6 refuse to load the plugin even though the underlying APIs are compatible.
- **Removed deprecated import**: `OptionalLimitOffsetPagination` was imported (but unused) in `api/views.py`. It has been renamed to `NetBoxPagination` in NetBox 4.6 and will be removed in 4.7. The unused import was removed to eliminate the `DeprecationWarning` at startup.

### Technical Details

Files Modified:

- `netbox_maintenance_device/__init__.py` – Bumped `version` to `1.3.0` and `max_version` to `4.6.99`.
- `netbox_maintenance_device/api/views.py` – Removed unused, deprecated `from netbox.api.pagination import OptionalLimitOffsetPagination`.
- `pyproject.toml` – Bumped version to `1.3.0`.
- `README.md` – Updated badge, compatibility table and install instructions.
- `USAGE.md` – Updated version/compatibility footer.
- `CHANGELOG.md` – Added 1.3.0 release notes.

### Verification

No breaking changes from NetBox 4.6.x affect this plugin:

- Plugin does not use the deprecated `OptionalLimitOffsetPagination` (unused import was removed).
- Plugin does not use the deprecated `querystring` template tag.
- Plugin does not use the deprecated `ExpandableIPAddressField` or `expand_ipaddress_pattern()`.
- Plugin does not rely on `LOGIN_REQUIRED`, `DEFAULT_ACTION_PERMISSIONS` or the deprecated `models` key in the application registry.
- Plugin remains compatible with Django 6.0 (used by NetBox 4.6.x).

## [1.2.3] - 2026-01-14

### Added
- **NetBox 4.5.x Compatibility**: Full compatibility with NetBox 4.5.0 and later
  - Verified compatibility with NetBox 4.5.x plugin API changes
  - No deprecated imports or APIs are used by the plugin
  - Plugin uses standard NetBox plugin API that remains stable across versions

### Changed
- **Python Version Requirements**: Updated minimum Python version to 3.12
  - NetBox 4.5.x requires Python 3.12, 3.13, or 3.14
  - Dropped support for Python 3.8, 3.9, 3.10, and 3.11
  - Updated Black formatter target version to Python 3.12
- **Version Compatibility Range**: Extended NetBox compatibility to 4.4.0 - 4.5.99
  - Plugin now officially supports both NetBox 4.4.x and 4.5.x
  - Backward compatibility maintained for NetBox 4.4.x users
- **Documentation**: Updated compatibility table and installation instructions
  - Added Python requirements note for different NetBox versions
  - Clarified version support and testing status

### Technical Details
- **Files Modified**:
  - `pyproject.toml` - Updated version to 1.2.3, Python requirements to >=3.12, and classifiers
  - `netbox_maintenance_device/__init__.py` - Updated version and max_version to 4.5.99
  - `README.md` - Updated compatibility table and installation instructions
  - `CHANGELOG.md` - Added version 1.2.3 release notes

### Verification
- No breaking changes from NetBox 4.5.x affect this plugin:
  - Plugin does not use deprecated `core.models.contenttypes` module
  - Plugin does not use deprecated `utilities.utils` imports
  - Plugin does not use deprecated `load_yaml()` or `load_json()` methods
  - Plugin does not use deprecated `/api/extras/object-types/` endpoint
  - Plugin does not reference deprecated `is_staff` field
  - Plugin does not create webhooks with `model` key in payload
  - Plugin uses standard permissions.BasePermission (not deprecated classes)

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