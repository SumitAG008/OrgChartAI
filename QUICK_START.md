# Quick Start Guide - OrgChartAI

Get up and running in 5 minutes!

## ⚡ Fast Setup

### 1. Database (PostgreSQL - Neon)

```bash
# Run this once to create all tables
cd database
psql 'postgresql://neondb_owner:npg_Mruj0FCPdbT9@ep-falling-dawn-ab3vxbgv-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require' -f schema.sql
```

### 2. Backend

```bash
cd backend/org-service

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r ../requirements.txt

# Create .env file
echo 'DATABASE_URL=postgresql://neondb_owner:npg_Mruj0FCPdbT9@ep-falling-dawn-ab3vxbgv-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require' > .env
echo 'CORS_ORIGINS=["http://localhost:3000"]' >> .env

# Run server
uvicorn main:app --reload --port 8000
```

### 3. Frontend

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
echo 'VITE_API_BASE_URL=http://localhost:8000' > .env

# Run dev server
npm run dev
```

### 4. Open Browser

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

## 🎯 What You'll See

1. **Modern UI** with header, sidebar, and org chart canvas
2. **Interactive org chart** (once data is loaded)
3. **Multiple views** (Org Chart, People & Positions, etc.)
4. **Zoom and pan** controls
5. **Professional design** ready for investors

## 📝 Next Steps

1. **Add Sample Data** - Create some org units, positions, and employees
2. **Connect HRIS** - Set up HRIS integration service
3. **Enable AI** - Configure AI recommendation service
4. **Customize** - Adjust colors, branding, features

## 🐛 Troubleshooting

**Backend won't start?**
- Check Python version (3.11+)
- Verify database connection string
- Ensure all dependencies installed

**Frontend won't load?**
- Check Node version (18+)
- Verify API URL in .env
- Check browser console for errors

**Database errors?**
- Verify schema was created
- Check connection string
- Ensure SSL mode is correct

## 📚 Full Documentation

See `/docs` folder for complete documentation:
- Database schema details
- API reference
- UI/UX specifications
- AI architecture
- HRIS integration

---

**Ready to build! 🚀**
