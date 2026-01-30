# Configuration Directory

This directory contains configuration files for the application.

## seed_data.yaml

Default seed data for database initialization. This file contains default data that will be synchronized with the database on application startup.

### Synchronization Behavior

The seed data synchronization follows these rules:

- **In YAML, not in DB**: Creates new records if the ID doesn't exist, or updates/restores if the ID exists (even if logically deleted)
- **In both YAML and DB**: Updates if values changed, leaves unchanged if values match
- **In DB, not in YAML**: Performs logical deletion (marks with `deleted_at` timestamp)

The YAML file supports multiple data types and can include multiline string fields (like descriptions) using YAML's literal block scalar syntax (`|`).

For complete documentation about database initialization, seed data synchronization logic, and configuration details, see the [Database section in the Development Guide](../docs/DEVELOPMENT.md#database).
