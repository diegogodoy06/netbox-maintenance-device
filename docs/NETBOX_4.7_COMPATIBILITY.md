# NetBox 4.7 compatibility review

Reviewed on 2026-10-13 for [issue #24](https://github.com/diegogodoy06/netbox-maintenance-device/issues/24).
The newest stable upstream release at review time is [NetBox 4.7.3](https://github.com/netbox-community/netbox/releases/tag/v4.7.3), published that day. The issue reports 4.7.2.

## Conclusion

Plugin 1.4.4 enables NetBox 4.7 while retaining the supported 4.4–4.6 families. Raising `max_version` alone was insufficient: runtime tests exposed broken API scheduling and background webhooks, and an actual database upgrade exposed inconsistent migration history.

Those problems also affected earlier releases. The API scheduling and background webhook failures were reproduced against the original plugin code on NetBox 4.6.10; they are not attributed to new upstream breaking changes.

## Upstream changes and their impact

The review used the official [4.7 release notes](https://github.com/netbox-community/netbox/blob/v4.7.3/docs/release-notes/version-4.7.md) and compared 4.6.10 with 4.7.3 source, including event processing, serializers, model features, generic views, jobs and template extensions.

| Change in upstream NetBox | Plugin impact and decision |
| --- | --- |
| Event rules now delegate to registered action providers; webhook jobs no longer accept `username` | The plugin delegates to NetBox's event pipeline rather than calling webhook jobs itself. Its custom events work with the new dispatcher. Background events must omit an absent request: modern action providers copy it whenever the key exists. Keep the legacy `username`/`request_id` event keys for older processors; they are not passed directly to 4.7 webhook jobs. |
| Snapshot-aware event conditions | The plugin already supplies `snapshots` and serialized `data`. No payload rewrite is needed. Actual scheduled/completed/due event dispatch is covered by integration tests. |
| django-tables2 3.0 and removal/renaming of query-string template tags | The plugin uses neither `RelatedLinkColumn` nor the removed query-string tag signatures. Lists, dashboard, detail pages and embedded tables render successfully. |
| Hierarchical models moved from MPTT to PostgreSQL `ltree` | Maintenance models inherit `NetBoxModel`, not hierarchical base classes, and do not filter on removed tree columns or call removed MPTT methods. No plugin schema conversion is needed. Device/VM relationships and data survive the tested upgrades. |
| Config-context caching and removal of separate config-context serializers | The plugin's small nested device/VM serializers use `WritableNestedSerializer`, which is still present. They do not inherit the removed serializer classes or manipulate config-context caches. |
| Nested serializer reuse and prefetch changes in 4.7.3 | Device/VM create/read/update operations, nested references, lists and bulk writes pass against the actual 4.7.3 serializer implementation. |
| Selection custom fields now return value/label objects in upstream REST serializers; custom-field accessors return lists | The plugin does not call queryset methods on custom-field accessors. Its existing public `custom_field_data` field exposes raw stored data; the selection-field round-trip test verifies that contract without changing existing API responses. |
| `MAILERS` replaces old Django email settings | The plugin uses NetBox event-rule notification actions and does not read obsolete email settings or instantiate an email backend. No mailer shim is needed. |
| Service ORM fields, deprecated pagination helpers, registry stores, legacy view action mappings and housekeeping were removed or changed | No direct references to the affected APIs exist in the plugin. Existing generic view integration remains functional. |
| PostgreSQL 15+ and Redis 6+ are required | Tests use PostgreSQL 16 and Redis 7. Deployment requirements remain those of the installed NetBox release. |

## Required fixes

1. **Version bound:** change `max_version` from `4.6.99` to `4.7.99`. Preserve `min_version = 4.4.0`, keeping future unreviewed minor releases gated.
2. **Upgrade history:** replace every upstream `__latest__` migration dependency with a named migration available in NetBox 4.4.0: `dcim.0215_rackreservation_status`, `extras.0132_configcontextprofile`, and `virtualization.0048_populate_mac_addresses`. Previously, upgrading a populated 4.6 database failed because `0001_initial` appeared to depend on the newly added `extras.0144_customfield_status`. The dependency correction changes no migration operations or plugin tables, and requires neither fake migrations nor deleting migration records.
3. **Background events:** modern processors must receive no `request` key when there is no request. The legacy 4.4 processor requires that key, even when its value is `None`, and looks up a nonempty username in the user table. Detect its actual function signature and supply the legacy shape with a null username for system events.
4. **API scheduling:** validate through the existing execution serializer before saving. Directly assigning an ISO date string caused `MaintenanceExecution.__str__()` to fail when change logging called `strftime()`. The serializer converts it to a datetime and rejects invalid input before any execution is written.

Package discovery is also scoped to the plugin package so CI's upstream NetBox checkouts cannot enter the distribution.

## Validation

The suite runs inside official NetBox source checkouts, with each tag's exact `requirements.txt`, a real PostgreSQL database and Redis. NetBox modules are not stubbed. Webhook queue insertion and outbound HTTP delivery are mocked; the actual rule processor, action dispatch, request copying, job signature and body rendering execute.

| NetBox | Python | Result |
| --- | --- | --- |
| 4.4.0 | 3.12.13 | 19 integration tests passed |
| 4.4.10 | 3.12.13 | 19 integration tests passed |
| 4.5.10 | 3.12.13 | 19 integration tests passed |
| 4.6.10 | 3.12.13 | 19 integration tests passed |
| 4.7.2 | 3.12.13 | 19 integration tests passed |
| 4.7.3 | 3.12.13 | 19 integration tests passed |
| 4.7.3 | 3.14.6 | 19 integration tests passed |

Coverage includes actual plugin loading and daily job registration, event choices, device/VM forms and target validation, 13 page renders, API CRUD and target filters, schedule/complete/cancel actions, invalid dates, successful bulk creation, atomic failed bulk writes, authentication, tags/custom-field data, queued custom events, background/request webhooks, notifications and overdue-alert deduplication.

Upgrade checks migrate databases from 4.4.0 and 4.6.10 to 4.7.3 and compare snapshots of existing IDs, device/VM targets, scheduling fields, tags and completed execution history. The 4.6 check starts with a database created using the original moving migration dependencies, reproduces the failure, then verifies the corrected upgrade without editing that database's migration records.

Fresh migrations and Django system checks pass. `makemigrations netbox_maintenance_device --check --dry-run` reports no model changes. The wheel and source distribution are built and validated, and the installed wheel is exercised on 4.7.3/Python 3.14 with a fresh database.

The committed GitHub Actions workflow repeats the version matrix and the two upgrade paths. These results establish compatibility for the tested releases and flows; they do not certify future 4.7 patches, third-party event actions, deployment-specific SSO or external webhook endpoints.

## Reproducing the tests

Use disposable PostgreSQL and Redis instances and an official NetBox checkout. Install that release's requirements and this plugin in the same Python environment, then run:

```bash
export NETBOX_CONFIGURATION=netbox_maintenance_device.tests.configuration
export NETBOX_TEST_DB=netbox
export NETBOX_TEST_DB_USER=netbox
export NETBOX_TEST_DB_PASSWORD=netbox
export NETBOX_TEST_DB_PORT=5432
export NETBOX_TEST_REDIS_PORT=6379

python /path/to/netbox/netbox/manage.py check
python /path/to/netbox/netbox/manage.py migrate --no-input
python /path/to/netbox/netbox/manage.py test netbox_maintenance_device.tests --no-input
```

The test configuration accepts database and Redis host/port overrides. The upgrade fixture and commands are in `netbox_maintenance_device/tests/upgrade.py` and `.github/workflows/compatibility.yml`.
