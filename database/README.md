# Database Setup Guide

## PostgreSQL (Neon) Setup

### Connection String

```
postgresql://neondb_owner:npg_Mruj0FCPdbT9@ep-falling-dawn-ab3vxbgv-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

### Running Migrations

```bash
# Install Alembic
pip install alembic

# Initialize (if first time)
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

### Manual Schema Creation

Run `schema.sql` to create all tables:

```bash
psql 'postgresql://neondb_owner:npg_Mruj0FCPdbT9@ep-falling-dawn-ab3vxbgv-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require' -f schema.sql
```

## Neo4j Setup

### Connection

```python
from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "your_password")
)
```

### Schema Creation

Run `neo4j_schema.cypher` to create constraints and indexes:

```bash
cypher-shell -u neo4j -p your_password -f neo4j_schema.cypher
```

## Database URLs

- **PostgreSQL**: See connection string above
- **Neo4j**: Configure in `.env` files
