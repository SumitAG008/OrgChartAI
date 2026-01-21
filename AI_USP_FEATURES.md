# AI Features - Your USP (Unique Selling Proposition)

## 🎯 Why AI is Always Enabled

**AI-powered org chart generation is the core differentiator of OrgChartAI.**

This is your **Unique Selling Proposition (USP)** - always install and enable AI features!

---

## 🤖 AI Features Included

### **1. Auto Org Chart Generation**
- Generate complete org structures from source data
- Uses GPT-4, Claude, or local models
- Confidence scoring
- Approval workflow

### **2. Team Formation AI**
- Recommend optimal team compositions
- Skill-based matching
- Budget-aware suggestions
- Past collaboration analysis

### **3. Org Design Intelligence**
- Suggest structure improvements
- Span of control optimization
- Hierarchy depth recommendations
- Cost optimization insights

### **4. MCP Integration**
- Model Context Protocol support
- Multiple AI providers
- Unified API for all models
- Cost tracking

---

## 📦 Installation

### **Always Install AI Dependencies**

```cmd
# For Org Service
cd backend\org-service
python -m venv venv
venv\Scripts\activate
pip install -r ..\requirements-core.txt
pip install -r ..\requirements-ai.txt

# For AI Service
cd backend\ai-service
python -m venv venv
venv\Scripts\activate
pip install -r ..\requirements-core.txt
pip install -r ..\requirements-ai.txt
```

### **Or Use Quick Install**

```cmd
install-all.bat
```

This installs everything including all AI features.

---

## 🔑 API Keys Required

### **OpenAI (Recommended)**

Get your key from: https://platform.openai.com/api-keys

```env
OPENAI_API_KEY=sk-...
MCP_API_KEY=sk-...
MCP_PROVIDER=openai
DEFAULT_MODEL=gpt-4-turbo
```

### **Anthropic (Alternative)**

Get your key from: https://console.anthropic.com/

```env
ANTHROPIC_API_KEY=sk-ant-...
MCP_PROVIDER=anthropic
DEFAULT_MODEL=claude-3-opus
```

---

## 🚀 Using AI Features

### **1. Auto-Generate Org Chart**

```bash
POST /api/v1/ai/generate-chart
{
  "name": "Q1 2025 Structure",
  "source_data": {
    "employees": [...],
    "departments": [...]
  },
  "preferences": {
    "layout": "hierarchical"
  }
}
```

### **2. Get Team Recommendations**

```bash
POST /api/v1/ai/recommendations/team-formation
{
  "project_requirements": {
    "skills": ["Python", "React", "ML"],
    "budget": 500000,
    "timeline": "3 months"
  }
}
```

### **3. Get Org Design Suggestions**

```bash
POST /api/v1/ai/recommendations/org-design
{
  "current_org": {...},
  "objectives": {
    "reduce_layers": true,
    "optimize_span": true
  }
}
```

---

## 💰 Pricing & Cost Management

### **AI Model Costs**

- **GPT-4 Turbo**: ~$0.01 per org chart generation
- **Claude 3 Opus**: ~$0.015 per generation
- **Local Models**: Free (but slower)

### **Cost Tracking**

All AI generations are tracked in `ai_generation_history` table:
- Tokens used
- Cost in USD
- Processing time
- Model used

---

## 🎯 Selling Points

### **For Investors**

1. **AI-Powered** - Not just visualization, intelligent generation
2. **Time-Saving** - Auto-generate org charts in seconds
3. **Best Practices** - AI suggests optimal structures
4. **Scalable** - Works for any organization size
5. **Future-Proof** - MCP integration supports new models

### **For Customers**

1. **Instant Setup** - Generate org chart from HRIS data
2. **Smart Recommendations** - AI suggests improvements
3. **Team Formation** - Find best people for projects
4. **Cost Optimization** - AI suggests cost-effective structures
5. **Compliance** - AI ensures best practices

---

## 📊 Competitive Advantage

**Other org chart tools:**
- ❌ Manual creation only
- ❌ No AI recommendations
- ❌ Static visualizations
- ❌ No intelligent insights

**OrgChartAI:**
- ✅ AI-powered generation
- ✅ Intelligent recommendations
- ✅ Dynamic, interactive charts
- ✅ Actionable insights

---

## 🔧 Configuration

### **Enable AI in Both Services**

Both `org-service` and `ai-service` have AI features:

1. **Org Service** - Can use AI for recommendations
2. **AI Service** - Dedicated AI endpoints

### **Set Default Model**

In `.env`:
```env
DEFAULT_MODEL=gpt-4-turbo
MCP_PROVIDER=openai
```

---

## ✅ Verification

Check AI is working:

```bash
# Test AI Service
curl http://localhost:8001/health

# List available models
curl http://localhost:8001/api/v1/ai/mcp/models

# Test generation (with API key)
curl -X POST http://localhost:8001/api/v1/ai/mcp/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello"}'
```

---

## 🎉 Summary

**AI is not optional - it's your USP!**

- Always install AI dependencies
- Always enable AI features
- Always highlight AI in demos
- Always mention AI in pitches

**This is what makes OrgChartAI different!** 🤖✨
