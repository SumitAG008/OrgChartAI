# AI Auto Org Chart Generation
## MCP Integration and AI-Powered Visualization

---

## 🎯 Overview

The AI Auto Org Chart Generation feature uses AI/ML models and MCP (Model Context Protocol) to automatically create organizational charts from source data. This eliminates manual chart creation and provides intelligent structure recommendations.

---

## 🤖 How It Works

### **1. Source Data Input**

The system accepts multiple data sources:

- **HRIS Export** (JSON/CSV)
- **Manual Input** (structured data)
- **Existing Org Structure** (for regeneration)
- **HRIS API** (direct connection)

### **2. AI Analysis**

Using MCP and AI models, the system:

1. **Analyzes** source data structure
2. **Identifies** hierarchy patterns
3. **Extracts** reporting relationships
4. **Detects** department/function groupings
5. **Recognizes** key roles and positions

### **3. Structure Generation**

AI generates optimal org structure:

- **Org Units** (divisions, departments, teams)
- **Positions** with reporting lines
- **Job Profiles** and classifications
- **Recommended hierarchy depth**
- **Span of control optimization**

### **4. Visualization Creation**

Generated structure is converted to:

- **React-compatible tree format**
- **Compatible with react-org-chart**
- **Ready for @unicef/react-org-chart**
- **Interactive visualization**

### **5. Confidence Scoring**

AI provides confidence scores based on:

- Data completeness
- Structure coherence
- Hierarchy depth
- Position coverage

---

## 🔧 MCP Integration

### **What is MCP?**

Model Context Protocol (MCP) is a standardized way to interact with AI models, providing:

- **Unified API** for different AI providers
- **Context management** for better prompts
- **Model selection** and switching
- **Cost tracking** and usage monitoring

### **Supported Models**

1. **OpenAI** (GPT-4 Turbo, GPT-4)
2. **Anthropic** (Claude 3 Opus, Claude 3 Sonnet)
3. **Local Models** (Llama 2, Mistral)
4. **Custom Models** (via MCP)

### **MCP Configuration**

```python
# In .env
MCP_BASE_URL=https://api.openai.com
MCP_API_KEY=your-api-key
MCP_PROVIDER=openai
DEFAULT_MODEL=gpt-4-turbo
```

---

## 📊 API Usage

### **Generate Org Chart**

```bash
POST /api/v1/ai/generate-chart
```

**Request:**
```json
{
  "name": "Q1 2025 Org Structure",
  "description": "Auto-generated from HRIS",
  "source_data": {
    "employees": [
      {
        "id": "emp-1",
        "name": "John Doe",
        "title": "CEO",
        "department": "Executive"
      }
    ],
    "departments": [...],
    "reporting_lines": [...]
  },
  "preferences": {
    "layout": "hierarchical",
    "max_depth": 5,
    "include_vacancies": true
  },
  "model_config_id": "gpt-4-turbo"
}
```

**Response:**
```json
{
  "id": "chart-uuid",
  "name": "Q1 2025 Org Structure",
  "generated_chart": {
    "tree": {
      "id": "pos-1",
      "person": {
        "name": "John Doe",
        "title": "CEO"
      },
      "children": [...]
    }
  },
  "confidence_score": 0.85,
  "processing_time_ms": 2500,
  "model_used": "gpt-4-turbo",
  "created_at": "2025-01-15T10:30:00Z"
}
```

---

## 🎨 AI Chart Builder Library

### **Source Code Structure**

```
backend/ai-service/
├── app/
│   ├── services/
│   │   ├── ai_chart_generator.py    # Main generator
│   │   └── mcp_client.py            # MCP integration
│   └── config.py                    # AI model config
```

### **Key Functions**

1. **`generate_chart()`** - Main generation function
2. **`_analyze_source_data()`** - AI data analysis
3. **`_generate_structure_with_ai()`** - Structure generation
4. **`_build_chart_tree()`** - Tree format conversion
5. **`_calculate_confidence()`** - Confidence scoring

### **Usage Example**

```python
from app.services.ai_chart_generator import AIChartGenerator

generator = AIChartGenerator()

# Generate from HRIS data
result = await generator.generate_chart(
    source_data={
        "employees": employees_data,
        "positions": positions_data
    },
    preferences={
        "layout": "hierarchical",
        "max_depth": 5
    },
    user_id="user-uuid"
)

# Use generated chart
chart_tree = result["generated_chart"]["tree"]
confidence = result["confidence_score"]
```

---

## 🔄 Workflow

### **1. Data Input**
- User uploads HRIS export or connects HRIS API
- System validates and parses data

### **2. AI Processing**
- MCP client sends data to AI model
- AI analyzes and generates structure
- System processes AI response

### **3. Chart Generation**
- Structure converted to tree format
- Visualization data prepared
- Confidence score calculated

### **4. Review & Approval**
- Chart saved as "Draft"
- User reviews generated structure
- User can edit before approval
- On approval, chart becomes active

### **5. Integration**
- Approved chart integrated into system
- Can be used in scenarios
- Can be exported or shared

---

## 📈 Confidence Scoring

Confidence score (0-1) based on:

1. **Data Completeness** (40%)
   - Missing fields
   - Incomplete relationships
   - Data quality

2. **Structure Coherence** (30%)
   - Logical hierarchy
   - Consistent reporting lines
   - Proper department grouping

3. **Coverage** (20%)
   - All employees included
   - All positions mapped
   - No orphaned records

4. **Best Practices** (10%)
   - Optimal span of control
   - Appropriate hierarchy depth
   - Industry standards alignment

---

## 🎯 Use Cases

### **1. New Company Setup**
- Import initial org data
- AI generates complete structure
- Review and approve

### **2. Restructuring**
- Input new requirements
- AI suggests optimal structure
- Compare with current state

### **3. M&A Integration**
- Combine two org structures
- AI suggests merged structure
- Review integration points

### **4. Rapid Scaling**
- Add new departments/teams
- AI suggests positions and structure
- Maintain consistency

---

## 🔐 Security & Audit

All AI generations are:

- **Logged** with user ID and timestamp
- **Versioned** for audit trail
- **Tracked** for cost and usage
- **Stored** with full metadata

---

## 📚 Related Documentation

- `AI_RECOMMENDATION_ENGINE.md` - AI architecture
- `TECHNICAL_IMPLEMENTATION_GUIDE.md` - Implementation details
- `HRIS_INTEGRATION_ARCHITECTURE.md` - Data integration

---

## 🚀 Future Enhancements

- **Multi-model ensemble** - Combine multiple AI models
- **Learning from feedback** - Improve based on user approvals
- **Custom model training** - Train on company-specific data
- **Real-time generation** - Generate as data changes
- **Visual preview** - Show chart before approval

---

**AI-powered org chart generation - making org design effortless!** 🤖✨
