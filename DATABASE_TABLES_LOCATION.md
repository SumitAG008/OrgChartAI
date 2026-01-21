# Database Tables Location & Query Guide

## 📍 Where Are the Mapping Tables?

The HRIS field mapping tables are stored in your **Neon PostgreSQL database**.

### Database Connection
- **Type**: PostgreSQL (Neon)
- **Connection**: Configured in `backend/hris-service/app/config.py`
- **URL**: Stored in `DATABASE_URL` environment variable

### Table Names

1. **`hris_field_mapping`** - Stores individual field mappings
2. **`hris_mapping_config`** - Stores mapping configuration metadata

Both tables are in the **`public` schema** of your PostgreSQL database.

---

## 🔍 How to Query the Tables

### 1. Using SQL (Direct Database Access)

#### View All Mappings for a Connection
```sql
SELECT 
    id,
    connection_id,
    entity_type,
    source_field,
    target_field,
    mapping_type,
    transform_function,
    is_active,
    created_at,
    updated_at
FROM hris_field_mapping
WHERE connection_id = 'conn-1768850167009'
AND is_active = TRUE
ORDER BY entity_type, source_field;
```

#### Count Mappings by Entity Type
```sql
SELECT 
    entity_type,
    COUNT(*) as mapping_count,
    COUNT(CASE WHEN transform_function IS NOT NULL THEN 1 END) as with_transforms
FROM hris_field_mapping
WHERE connection_id = 'conn-1768850167009'
AND is_active = TRUE
GROUP BY entity_type
ORDER BY entity_type;
```

#### View Mapping Configuration
```sql
SELECT 
    id,
    connection_id,
    target_entity_type,
    source_entity_name,
    hris_source,
    is_active,
    last_synced_at,
    created_at,
    updated_at
FROM hris_mapping_config
WHERE connection_id = 'conn-1768850167009'
AND is_active = TRUE;
```

#### Find Mappings with Transformations
```sql
SELECT 
    entity_type,
    source_field,
    target_field,
    transform_function
FROM hris_field_mapping
WHERE connection_id = 'conn-1768850167009'
AND is_active = TRUE
AND transform_function IS NOT NULL
ORDER BY entity_type, source_field;
```

#### Check if Tables Exist
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('hris_field_mapping', 'hris_mapping_config');
```

### 2. Using API Endpoints

#### Get All Mappings
```bash
GET http://localhost:8002/api/v1/hris/connections/{connection_id}/mapping
```

#### Verify Mappings
```bash
GET http://localhost:8002/api/v1/hris/connections/{connection_id}/mapping/verify
```

#### Get Mappings for Specific Entity Type
```bash
GET http://localhost:8002/api/v1/hris/connections/{connection_id}/mapping?entity_type=org_unit
```

### 3. Using Python (Direct Database Access)

```python
import asyncpg
import os
from urllib.parse import urlparse
import ssl

async def query_mappings(connection_id: str):
    # Parse DATABASE_URL
    db_url = os.getenv("DATABASE_URL")
    parsed = urlparse(db_url)
    
    # Create SSL context for Neon
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    # Connect
    conn = await asyncpg.connect(
        host=parsed.hostname,
        port=parsed.port or 5432,
        user=parsed.username,
        password=parsed.password,
        database=parsed.path[1:],  # Remove leading /
        ssl=ssl_context
    )
    
    try:
        # Query mappings
        rows = await conn.fetch("""
            SELECT * FROM hris_field_mapping
            WHERE connection_id = $1 AND is_active = TRUE
        """, connection_id)
        
        for row in rows:
            print(f"{row['source_field']} -> {row['target_field']}")
    
    finally:
        await conn.close()
```

---

## 🗂️ Table Schema

### `hris_field_mapping` Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `connection_id` | TEXT | HRIS connection ID |
| `entity_type` | TEXT | Target entity type (org_unit, position, employee) |
| `source_field` | TEXT | SuccessFactors field name |
| `target_field` | TEXT | OrgChartAI field name |
| `mapping_type` | TEXT | 'direct', 'transform', 'custom' |
| `transform_function` | TEXT | Transformation function (e.g., 'date_format(...)') |
| `is_active` | BOOLEAN | Whether mapping is active |
| `created_at` | TIMESTAMP | Creation timestamp |
| `updated_at` | TIMESTAMP | Last update timestamp |
| `created_by` | TEXT | Creator (optional) |
| `updated_by` | TEXT | Last updater (optional) |

**Unique Constraint**: `(connection_id, entity_type, source_field)`

### `hris_mapping_config` Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `connection_id` | TEXT | HRIS connection ID (unique) |
| `target_entity_type` | TEXT | Target entity type |
| `source_entity_name` | TEXT | SuccessFactors entity name (e.g., 'FOBusinessUnit') |
| `hris_source` | TEXT | HRIS system ('successfactors', 'workday', etc.) |
| `is_active` | BOOLEAN | Whether config is active |
| `last_synced_at` | TIMESTAMP | Last sync timestamp |
| `created_at` | TIMESTAMP | Creation timestamp |
| `updated_at` | TIMESTAMP | Last update timestamp |

---

## 🔧 Troubleshooting

### Issue: "Table does not exist"

**Solution**: Run the setup script:
```bash
python backend/hris-service/setup_mapping_tables.py
```

### Issue: "Connection is closed"

**Solution**: This is a database connection pooling issue. The fix has been applied in the code to use proper transaction handling.

### Issue: Can't see data in Neon DB

**Check**:
1. Correct `connection_id`?
2. `is_active = TRUE`?
3. Tables exist? Run: `SELECT * FROM hris_field_mapping LIMIT 1;`

### Issue: Field types not showing

**Check**:
1. Metadata is being fetched correctly from SuccessFactors
2. Field types are parsed from XML metadata
3. UI is displaying the `type` field from the API response

---

## 📊 Sample Queries

### Find All Transformations
```sql
SELECT DISTINCT transform_function
FROM hris_field_mapping
WHERE transform_function IS NOT NULL
AND is_active = TRUE;
```

### Count Mappings by Type
```sql
SELECT 
    mapping_type,
    COUNT(*) as count
FROM hris_field_mapping
WHERE is_active = TRUE
GROUP BY mapping_type;
```

### Find Unmapped Required Fields
```sql
-- This would require joining with target entity schema
-- Example: Find org_unit fields that should be mapped but aren't
SELECT 'code' as target_field, 'Required' as status
WHERE NOT EXISTS (
    SELECT 1 FROM hris_field_mapping
    WHERE target_field = 'code'
    AND entity_type = 'org_unit'
    AND is_active = TRUE
);
```

---

## 🎯 Quick Reference

| Task | Query/Endpoint |
|------|---------------|
| View all mappings | `SELECT * FROM hris_field_mapping WHERE connection_id = '...'` |
| Verify mappings | `GET /api/v1/hris/connections/{id}/mapping/verify` |
| Check table exists | `SELECT * FROM hris_field_mapping LIMIT 1;` |
| Find transformations | `SELECT * FROM hris_field_mapping WHERE transform_function IS NOT NULL` |
| Count by entity | `SELECT entity_type, COUNT(*) FROM hris_field_mapping GROUP BY entity_type` |

---

## 📝 Notes

- **Database**: Neon PostgreSQL (cloud-hosted)
- **Schema**: `public`
- **Tables**: `hris_field_mapping`, `hris_mapping_config`
- **Connection**: Managed via SQLAlchemy async engine
- **SSL**: Required for Neon connections
