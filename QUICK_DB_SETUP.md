# Quick Database Setup for Functional Chart

## ⚠️ IMPORTANT: You need to run the database schema before saving data!

The functional chart feature requires database tables to be created. Currently, the backend returns mock data for viewing, but **you cannot save new data** until the tables are created.

## Quick Setup (Windows PowerShell)

### Option 1: Direct psql Command

```powershell
# Connect and run the schema
psql "postgresql://neondb_owner:npg_Mruj0FCPdbT9@ep-falling-dawn-ab3vxbgv-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require" -f database/functional_chart_schema.sql
```

### Option 2: Copy-Paste Method

1. Open PowerShell
2. Connect to database:
```powershell
psql "postgresql://neondb_owner:npg_Mruj0FCPdbT9@ep-falling-dawn-ab3vxbgv-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require"
```

3. Once connected, copy the entire contents of `database/functional_chart_schema.sql` and paste into the psql prompt, then press Enter.

### Option 3: Using Neon Console

1. Go to https://console.neon.tech
2. Select your database
3. Go to SQL Editor
4. Copy contents of `database/functional_chart_schema.sql`
5. Paste and execute

## What Gets Created

- ✅ `function_category` table
- ✅ `function` table  
- ✅ `accountability` table
- ✅ `accountability_assignment` table
- ✅ Sample data (5 categories, 16+ functions)

## Verify Setup

After running the schema, test by:

1. **Check tables exist:**
```sql
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('function_category', 'function', 'accountability', 'accountability_assignment');
```

2. **Check sample data:**
```sql
SELECT name FROM function_category;
```

You should see:
- People and Culture
- Governance
- Brand and Communications
- Account Management
- Commercial, Compliance and Legal

## After Setup

Once the tables are created:
- ✅ You can add new accountabilities (they'll save to database)
- ✅ You can edit accountabilities (changes persist)
- ✅ You can move items between functions/categories
- ✅ All changes are tracked with audit trails

## Current Status

- ❌ **Cannot save** - Tables don't exist
- ✅ **Can view** - Mock data is displayed
- ✅ **Can test UI** - All frontend features work

After running the schema:
- ✅ **Can save** - All operations work with real database
