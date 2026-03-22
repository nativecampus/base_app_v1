# Data Model

## Conventions

All tables use the `AuditMixin` which provides:

| Column | Type | Description |
|--------|------|-------------|
| `created_at` | datetime | Row creation timestamp (UTC) |
| `updated_at` | datetime | Last modification timestamp (UTC) |
| `created_by` | varchar(100) | User who created the row |
| `updated_by` | varchar(100) | User who last modified the row |

## Tables

Add your application tables here as you create models. Each table should document:

- Column name, type, and constraints
- Foreign key relationships
- Indexes
- Any business rules or invariants

## Example Format

```
### table_name

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PK | Auto-increment primary key |
| name | String(200) | NOT NULL, UNIQUE | Display name |
| status | Enum | NOT NULL | Current status |
| parent_id | Integer | FK → parents.id | Parent reference |
| + audit columns | | | Via AuditMixin |

Indexes: parent_id
```
