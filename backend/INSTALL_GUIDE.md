# Installation Guide - Backend Services

## 📦 Dependency Management

We've split dependencies into separate files for better management:

### **1. Core Dependencies** (`requirements-core.txt`)
- Required for `org-service`
- No AI/ML dependencies
- Lightweight and fast
- Works with Python 3.11+

### **2. AI Dependencies** (`requirements-ai.txt`)
- Required for `ai-service`
- Includes PyTorch, transformers, etc.
- Only install if you need AI features

### **3. Full Requirements** (`requirements.txt`)
- All dependencies combined
- Use if you want everything

---

## 🚀 Installation Options

### **Option 1: Org Service Only (Recommended for Start)**

```cmd
cd backend\org-service
python -m venv venv
venv\Scripts\activate
pip install -r ..\requirements-core.txt
```

**No AI dependencies** - faster installation, smaller footprint.

### **Option 2: AI Service (Full Stack)**

```cmd
cd backend\ai-service
python -m venv venv
venv\Scripts\activate
pip install -r ..\requirements-core.txt
pip install -r ..\requirements-ai.txt
```

**Includes AI dependencies** - for AI-powered features.

### **Option 3: Everything**

```cmd
cd backend\org-service
python -m venv venv
venv\Scripts\activate
pip install -r ..\requirements.txt
```

**Note:** This may fail on Python 3.12+ due to torch version. Use Option 1 or 2 instead.

---

## 🐍 Python Version Compatibility

### **Python 3.11**
- ✅ All packages work
- ✅ torch==2.1.1 available

### **Python 3.12+**
- ✅ Core packages work
- ⚠️ torch>=2.2.0 required (not 2.1.1)
- ✅ Use `requirements-core.txt` for org-service
- ✅ Use `requirements-ai.txt` for ai-service (has compatible torch)

---

## 🔧 Troubleshooting

### **Error: "No matching distribution found for torch==2.1.1"**

**Cause:** Python 3.12+ doesn't support torch 2.1.1

**Solution:**
1. Use `requirements-core.txt` for org-service (no torch needed)
2. Or use `requirements-ai.txt` for ai-service (has compatible torch>=2.2.0)

### **Error: "torch installation takes too long"**

**Solution:** 
- Skip AI dependencies if you don't need them
- Use `requirements-core.txt` for org-service

### **Error: "CUDA not available"**

**Solution:**
- Install CPU-only torch: `pip install torch --index-url https://download.pytorch.org/whl/cpu`
- Or skip AI features for now

---

## 📋 What Each Service Needs

### **org-service**
- ✅ FastAPI, SQLAlchemy, PostgreSQL drivers
- ✅ Neo4j driver
- ❌ No AI/ML dependencies needed

### **ai-service**
- ✅ Everything from org-service
- ✅ PyTorch, transformers, scikit-learn
- ✅ OpenAI/Anthropic clients

---

## ✅ Quick Start

### **Just Org Service (Fastest)**

```cmd
cd backend\org-service
python -m venv venv
venv\Scripts\activate
pip install -r ..\requirements-core.txt
uvicorn main:app --reload --port 8000
```

### **With AI Service**

```cmd
# Terminal 1 - Org Service
cd backend\org-service
python -m venv venv
venv\Scripts\activate
pip install -r ..\requirements-core.txt
uvicorn main:app --reload --port 8000

# Terminal 2 - AI Service
cd backend\ai-service
python -m venv venv
venv\Scripts\activate
pip install -r ..\requirements-core.txt
pip install -r ..\requirements-ai.txt
uvicorn main:app --reload --port 8001
```

---

**Choose the right dependencies for your needs!** 🎯
