# AI Service - Auto Org Chart Generation

AI-powered service for automatically generating organizational charts using AI/ML models and MCP (Model Context Protocol).

## Features

- **Auto Org Chart Generation** - Generate org charts from source data (HRIS, CSV, manual input)
- **MCP Integration** - Use Model Context Protocol for AI model access
- **Multiple AI Models** - Support for OpenAI, Anthropic, and local models
- **Confidence Scoring** - AI provides confidence scores for generated charts
- **Approval Workflow** - Review and approve AI-generated charts before use

## API Endpoints

### Generate Org Chart
```
POST /api/v1/ai/generate-chart
```

**Request:**
```json
{
  "name": "Q1 2025 Org Structure",
  "description": "Generated from HRIS export",
  "source_data": {
    "employees": [...],
    "positions": [...],
    "departments": [...]
  },
  "preferences": {
    "layout": "hierarchical",
    "max_depth": 5
  }
}
```

**Response:**
```json
{
  "id": "chart-uuid",
  "name": "Q1 2025 Org Structure",
  "generated_chart": {
    "tree": {...}
  },
  "confidence_score": 0.85,
  "processing_time_ms": 2500,
  "model_used": "gpt-4-turbo"
}
```

### List Generated Charts
```
GET /api/v1/ai/generated-charts?status=Draft&limit=50
```

### Approve Chart
```
POST /api/v1/ai/generated-charts/{chart_id}/approve?user_id=user-uuid
```

## MCP Configuration

Set in `.env`:
```env
MCP_BASE_URL=https://api.openai.com
MCP_API_KEY=your-api-key
MCP_PROVIDER=openai
```

## Usage

```python
from app.services.ai_chart_generator import AIChartGenerator

generator = AIChartGenerator()

# Generate chart from HRIS data
result = await generator.generate_chart(
    source_data={
        "employees": [...],
        "positions": [...]
    },
    preferences={"layout": "hierarchical"},
    user_id="user-uuid"
)
```
