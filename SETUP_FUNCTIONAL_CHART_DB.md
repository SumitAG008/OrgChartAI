# Setup Functional Chart Database Tables

The functional chart feature requires additional database tables. Follow these steps to set them up:

## Quick Setup (Windows)

### Option 1: Using psql Command Line

1. Open PowerShell or Command Prompt

2. Run the SQL file:
```powershell
psql "postgresql://neondb_owner:npg_Mruj0FCPdbT9@ep-falling-dawn-ab3vxbgv-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require" -f database/functional_chart_schema.sql
```

### Option 2: Using psql Interactive Mode

1. Connect to your database:
```powershell
psql "postgresql://neondb_owner:npg_Mruj0FCPdbT9@ep-falling-dawn-ab3vxbgv-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require"
```

2. Once connected, run:
```sql
\i database/functional_chart_schema.sql
```

Or copy and paste the contents of `database/functional_chart_schema.sql` directly into the psql prompt.

### Option 3: Using Neon Console

1. Go to your Neon dashboard
2. Navigate to SQL Editor
3. Copy the contents of `database/functional_chart_schema.sql`
4. Paste and execute

## What Gets Created

The schema creates:

1. **function_category** - Top-level categories (People and Culture, Governance, etc.)
2. **function** - Functions within categories (Compensation, Recruitment, etc.)
3. **accountability** - Specific responsibilities within functions
4. **accountability_assignment** - Links accountabilities to positions/employees

Plus:
- Indexes for performance
- Triggers for automatic `updated_at` timestamps
- Sample data (5 categories, 16 functions, 1 sample accountability)

## Verify Setup

After running the schema, you can verify it worked by:

1. Checking the tables exist:
```sql
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('function_category', 'function', 'accountability', 'accountability_assignment');
```

2. Checking sample data:
```sql
SELECT name FROM function_category;
```

You should see:
- People and Culture
- Governance
- Brand and Communications
- Account Management
- Commercial, Compliance and Legal

## Troubleshooting

### Error: "relation already exists"
- The tables are already created. You can skip this step or drop and recreate them.

### Error: "permission denied"
- Make sure you're using the correct database credentials.

### Error: "uuid-ossp extension does not exist"
- Run this first:
```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

## Note

The backend will return **mock data** if the tables don't exist, so the frontend will still work for testing. However, to save data permanently, you need to run the schema.
