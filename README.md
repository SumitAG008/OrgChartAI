# OrgChartAI

**Part of the [meldra](https://github.com/SumitAG008) library** · by [SumitAG008](https://github.com/SumitAG008)

AI-powered organizational intelligence platform with SuccessFactors sync, HRIS integration, and advanced visualization. Part of the **meldra** suite.

## 🚀 Features

- **26+ Org Structure Visualizations** - Hierarchical, Matrix, Network, Radial, and more
- **AI-Powered Auto Generation** - MCP integration for automatic org chart creation
- **AI-Powered Recommendations** - Team formation, org design, skill gap analysis
- **HRIS Integration** - Direct connection to Workday, SAP, BambooHR, and more
- **Real-Time Analytics** - Headcount, vacancies, span of control, org health metrics
- **Scenario Planning** - Compare current vs future states, M&A simulations
- **Skills Engine** - Skill-based team formation and gap analysis
- **Complete Audit Trail** - Every change tracked with timestamps and user info
- **Version History** - Time-travel queries and version restoration
- **Modern UI/UX** - Beautiful, responsive, investor-ready interface

## 🏗️ Architecture

```
OrgChartAI/
├── backend/              # FastAPI microservices
│   ├── org-service/      # Core org chart service
│   ├── ai-service/       # AI/ML recommendations
│   ├── hris-service/     # HRIS integration
│   └── graph-service/    # Neo4j graph operations
├── frontend/             # React/TypeScript UI
├── database/             # Database schemas and migrations
└── docs/                # Complete documentation
```

## 🛠️ Tech Stack

- **Frontend**: React 18, TypeScript, Tailwind CSS, D3.js
- **Backend**: Python 3.11+, FastAPI, Pydantic
- **Databases**: PostgreSQL (Neon), Neo4j
- **AI/ML**: scikit-learn, transformers, MCP (Model Context Protocol)
- **Integration**: REST APIs, WebSockets, OAuth 2.0
- **Audit & Versioning**: Complete timestamp tracking, change history, version control

## 📦 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL (Neon)
- Neo4j 5.0+

### **Windows Users**

See [SETUP_WINDOWS.md](SETUP_WINDOWS.md) for Windows-specific instructions.

**Quick start scripts:**
- `start-backend.bat` - Start org service
- `start-ai-service.bat` - Start AI service  
- `start-frontend.bat` - Start frontend
- `start-all.ps1` - Start all services (PowerShell)
- `setup-database.bat` - Setup database

### **Installation (With AI Features - USP)**

**Quick Install (All AI Features):**
```cmd
# Windows
install-all.bat

# Or manually
cd backend\org-service
python -m venv venv
venv\Scripts\activate
pip install -r ..\requirements-core.txt
pip install -r ..\requirements-ai.txt
```

**Note:** AI features are always installed - this is our USP!

### Installation

```bash
# Clone repository
git clone https://github.com/SumitAG008/OrgChartAI.git
cd OrgChartAI

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install

# Database setup
cd ../database
# Run migrations (see database/README.md)
```

### Environment Variables

Create `.env` files in each service directory:

```env
# PostgreSQL
DATABASE_URL=postgresql://neondb_owner:npg_Mruj0FCPdbT9@ep-falling-dawn-ab3vxbgv-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# HRIS Integration
HRIS_API_KEY=your_api_key
HRIS_BASE_URL=https://api.hris.com
```

### Run Services

```bash
# Start backend services
cd backend/org-service
uvicorn main:app --reload --port 8000

cd ../ai-service
uvicorn main:app --reload --port 8001

cd ../hris-service
uvicorn main:app --reload --port 8002

# Start frontend
cd frontend
npm run dev
```

## 📚 Documentation

Complete documentation available in `/docs`:

- [Product Overview](docs/ORG_CHART_INTELLIGENCE_PRODUCT.md)
- [Database Schema](docs/DATABASE_SCHEMA.md)
- [API Documentation](docs/API_REFERENCE.md)
- [UI/UX Requirements](docs/UI_UX_REQUIREMENTS.md)
- [AI Architecture](docs/AI_RECOMMENDATION_ENGINE.md)

## 🎯 Roadmap

- [x] Core data model
- [x] Database schemas
- [ ] HRIS integration
- [ ] AI recommendation engine
- [ ] Frontend implementation
- [ ] Production deployment

## 📄 License

Proprietary - All rights reserved.  
**meldra library** © [SumitAG008](https://github.com/SumitAG008)

## 🤝 Contributing

This is a private project under the **meldra** library. For access, contact [SumitAG008](https://github.com/SumitAG008).

---

**meldra · Built for modern organizational intelligence**
