# Setup Guide - OrgChartAI

Complete setup instructions for the AI-Powered Organizational Intelligence Platform.

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **PostgreSQL** (Neon account)
- **Neo4j 5.0+** (optional, for graph features)
- **Git**

### 1. Clone Repository

```bash
git clone https://github.com/SumitAG008/OrgChartAI.git
cd OrgChartAI
```

### 2. Database Setup

#### PostgreSQL (Neon)

Your connection string:
```
postgresql://neondb_owner:npg_Mruj0FCPdbT9@ep-falling-dawn-ab3vxbgv-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

**Create schema:**
```bash
cd database
psql 'postgresql://neondb_owner:npg_Mruj0FCPdbT9@ep-falling-dawn-ab3vxbgv-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require' -f schema.sql
```

#### Neo4j (Optional)

```bash
# Install Neo4j Desktop or use Docker
docker run -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:5.0

# Run schema
cypher-shell -u neo4j -p password -f database/neo4j_schema.cypher
```

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cd org-service
cat > .env << EOF
DATABASE_URL=postgresql://neondb_owner:npg_Mruj0FCPdbT9@ep-falling-dawn-ab3vxbgv-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
CORS_ORIGINS=["http://localhost:3000"]
EOF

# Run service
uvicorn main:app --reload --port 8000
```

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
cat > .env << EOF
VITE_API_BASE_URL=http://localhost:8000
EOF

# Run development server
npm run dev
```

### 5. Access Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📁 Project Structure

```
OrgChartAI/
├── backend/
│   ├── org-service/          # Core org chart service
│   │   ├── main.py
│   │   └── app/
│   │       ├── config.py
│   │       ├── database.py
│   │       ├── models.py      # Pydantic models
│   │       ├── models_db.py   # SQLAlchemy models
│   │       └── services/
│   ├── ai-service/            # AI recommendations (TODO)
│   ├── hris-service/          # HRIS integration (TODO)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   └── types/
│   ├── package.json
│   └── vite.config.ts
├── database/
│   ├── schema.sql             # PostgreSQL schema
│   └── neo4j_schema.cypher    # Neo4j schema
└── docs/                      # Complete documentation
```

## 🔧 Configuration

### Environment Variables

**Backend (.env):**
```env
DATABASE_URL=postgresql://...
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
CORS_ORIGINS=["http://localhost:3000"]
```

**Frontend (.env):**
```env
VITE_API_BASE_URL=http://localhost:8000
```

## 🧪 Testing

### Backend

```bash
cd backend/org-service
pytest
```

### Frontend

```bash
cd frontend
npm run test
```

## 🚀 Production Deployment

### Backend

```bash
# Build Docker image
docker build -t orgchartai-backend ./backend/org-service

# Run container
docker run -p 8000:8000 --env-file .env orgchartai-backend
```

### Frontend

```bash
# Build
cd frontend
npm run build

# Serve
npm run preview
```

## 📚 Next Steps

1. **Set up HRIS integration** - Connect to your HRIS system
2. **Configure AI service** - Set up AI recommendation engine
3. **Import data** - Load initial org data from HRIS
4. **Customize UI** - Adjust colors, branding, etc.

## 🆘 Troubleshooting

### Database Connection Issues

- Verify connection string
- Check firewall rules
- Ensure SSL mode is correct

### Frontend Not Loading

- Check API URL in `.env`
- Verify backend is running
- Check browser console for errors

### Import Errors

- Ensure all dependencies are installed
- Check Python/Node versions
- Verify virtual environment is activated

## 📞 Support

For issues or questions:
- Check documentation in `/docs`
- Review API docs at `/docs` endpoint
- Open an issue on GitHub

---

**Ready to build! 🎉**
