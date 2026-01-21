# Database Setup Required

## ⚠️ Error: Tables Don't Exist

The error `relation "position" does not exist` means the database tables haven't been created yet.

## 🚀 Quick Fix

### **Option 1: Use Batch Script (Easiest)**

From project root, run:
```cmd
setup-database-quick.bat
```

### **Option 2: Manual Setup**

```cmd
cd database
psql "postgresql://neondb_owner:npg_Mruj0FCPdbT9@ep-falling-dawn-ab3vxbgv-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require" -f schema.sql
psql "postgresql://neondb_owner:npg_Mruj0FCPdbT9@ep-falling-dawn-ab3vxbgv-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require" -f triggers.sql
```

### **Option 3: Using pgAdmin**

1. Open pgAdmin
2. Connect to your Neon database
3. Open Query Tool
4. Copy and paste contents of `database/schema.sql`
5. Execute
6. Copy and paste contents of `database/triggers.sql`
7. Execute

## ✅ What Gets Created

The schema creates:
- ✅ All core tables (org_unit, position, employee, job, etc.)
- ✅ Skills tables
- ✅ AI/ML tables
- ✅ Audit tables (change_history, version_history)
- ✅ Analytics tables
- ✅ All indexes and constraints

## 🔍 Verify Setup

After running the schema, verify tables exist:

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
```

You should see tables like:
- `org_unit`
- `position`
- `employee`
- `job`
- `skill`
- etc.

## 🎯 After Setup

Once tables are created, restart your backend:

```cmd
cd backend\org-service
.\venv\Scripts\activate
uvicorn main:app --reload --port 8000
```

The server should now work without errors!
