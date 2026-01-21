# AI-Powered SuccessFactors Mapping & Automapping Guide

Complete guide on how data mapping works and how AI/ML/Deep Learning can enable intelligent automapping.

---

## 📊 Current Mapping Architecture

### **How Mapping Works Today**

```
SuccessFactors (Source)
    ↓ OData API
HRIS Service (Port 8002)
    ↓ Data Transformation
    ├─ Field Mapping (Manual Rules)
    ├─ Data Validation
    └─ Format Conversion
    ↓
Org Service (Port 8000)
    ↓ Database Storage
PostgreSQL (Neon)
    ↓ Query & Build
Frontend (React)
    ↓ Visualization
Org Chart Display
```

### **Current Mapping Process**

1. **Fetch Data** from SuccessFactors OData API
2. **Transform** using predefined rules (`DataTransformer`)
3. **Validate** data format and required fields
4. **Store** in PostgreSQL database
5. **Build** org chart hierarchy
6. **Display** in frontend

---

## 🔄 Manual Mapping (Current Implementation)

### **Field-by-Field Mapping**

The `DataTransformer` service maps SuccessFactors fields to internal format:

#### **Org Units Mapping**

```python
# SuccessFactors → OrgChartAI
{
    "orgUnitId": "SF_OU_001",           → hris_id: "SF_OU_001"
    "orgUnitCode": "ENG",               → code: "ENG"
    "orgUnitName": "Engineering",       → name: "Engineering"
    "orgUnitType": "Department",        → type: "Department"
    "parentOrgUnitId": "SF_OU_ROOT",    → parent_hris_id: "SF_OU_ROOT"
    "status": "active"                  → status: "Active"
}
```

#### **Positions Mapping**

```python
# SuccessFactors → OrgChartAI
{
    "positionId": "SF_POS_001",              → hris_id: "SF_POS_001"
    "positionCode": "ENG001",                → position_code: "ENG001"
    "positionTitle": "Senior Engineer",       → position_title: "Senior Engineer"
    "reportsToPositionId": "SF_POS_MGR",     → reports_to_hris_id: "SF_POS_MGR"
    "orgUnitId": "SF_OU_001",                → org_unit_id: (resolved from hris_id)
    "status": "active"                        → status: "Active"
}
```

#### **Employees Mapping**

```python
# SuccessFactors → OrgChartAI
{
    "userId": "SF_USER_001",            → employee_number: "SF_USER_001"
    "firstName": "John",                 → first_name: "John"
    "lastName": "Doe",                   → last_name: "Doe"
    "displayName": "John Doe",           → preferred_name: "John Doe"
    "email": "john@company.com",         → email: "john@company.com"
    "positionId": "SF_POS_001",          → position_id: (resolved from hris_id)
    "status": "active"                   → status: "Active"
}
```

### **Relationship Resolution**

After mapping, the system resolves relationships:

```python
# Step 1: Create/Link Org Units
org_unit = find_or_create_org_unit(hris_id="SF_OU_001")
parent_org_unit = find_or_create_org_unit(hris_id="SF_OU_ROOT")
org_unit.parent_org_unit_id = parent_org_unit.id

# Step 2: Create/Link Positions
position = find_or_create_position(hris_id="SF_POS_001")
position.org_unit_id = org_unit.id  # Link to org unit
position.reports_to_position_id = find_position(hris_id="SF_POS_MGR").id

# Step 3: Create/Link Employees
employee = find_or_create_employee(hris_id="SF_USER_001")
employee.position_id = position.id  # Link to position
```

---

## 🤖 AI-Powered Automapping

### **How AI/ML/Deep Learning Can Enhance Mapping**

AI can automate and improve mapping in several ways:

### **1. Intelligent Field Detection**

**Problem:** Different HRIS systems use different field names for the same concept.

**AI Solution:** Use Natural Language Processing (NLP) to understand field semantics.

```python
# Example: AI detects that these fields mean the same thing
SuccessFactors: "orgUnitName"
Workday: "Organization Name"
BambooHR: "Department Name"
Oracle HCM: "Org Unit Label"

# AI Model learns:
"orgUnitName" ≈ "Organization Name" ≈ "Department Name" ≈ "Org Unit Label"
```

**Implementation:**
- **Word Embeddings** (Word2Vec, GloVe) to understand semantic similarity
- **Transformer Models** (BERT, GPT) to understand context
- **Similarity Matching** using cosine similarity or neural networks

### **2. Automatic Schema Discovery**

**Problem:** New HRIS systems or custom fields require manual mapping configuration.

**AI Solution:** Automatically discover and map schemas.

```python
# AI analyzes SuccessFactors schema
{
    "User": {
        "userId": "string",           # AI detects: Employee ID
        "firstName": "string",         # AI detects: First Name
        "lastName": "string",          # AI detects: Last Name
        "email": "email",              # AI detects: Email Address
        "positionId": "reference"      # AI detects: Position Reference
    }
}

# AI automatically creates mapping:
{
    "userId": "employee_number",
    "firstName": "first_name",
    "lastName": "last_name",
    "email": "email",
    "positionId": "position_id"
}
```

**Implementation:**
- **Schema Analysis:** Parse OData $metadata to understand structure
- **Field Type Detection:** Use ML to classify field types (string, number, date, reference)
- **Semantic Matching:** Match fields based on name, type, and context

### **3. Data Quality & Validation**

**Problem:** Data from HRIS may have inconsistencies, missing values, or format issues.

**AI Solution:** Use ML to detect and fix data quality issues.

```python
# AI detects anomalies:
{
    "email": "john.doe@company",        # Missing TLD - AI suggests: "john.doe@company.com"
    "positionTitle": "Sr. Eng",         # Abbreviation - AI expands: "Senior Engineer"
    "orgUnitName": "ENG",               # Code instead of name - AI suggests: "Engineering"
    "reportsTo": null                   # Missing manager - AI infers from hierarchy
}
```

**Implementation:**
- **Anomaly Detection:** Isolation Forest, Autoencoders
- **Data Imputation:** KNN, Neural Networks for missing value prediction
- **Format Standardization:** NLP models for text normalization

### **4. Relationship Inference**

**Problem:** Some relationships may be missing or incorrect in source data.

**AI Solution:** Infer relationships using graph neural networks.

```python
# Missing relationship in SuccessFactors:
Position A: reportsTo = null
Position B: reportsTo = Position A
Position C: reportsTo = Position A

# AI infers hierarchy:
# Position A is likely a manager (has 2+ direct reports)
# AI suggests: Position A.reportsTo = Root Position
```

**Implementation:**
- **Graph Neural Networks (GNN):** Learn from org structure patterns
- **Hierarchy Detection:** Analyze reporting patterns to infer missing links
- **Anomaly Detection:** Find inconsistent reporting structures

### **5. Intelligent Data Enrichment**

**Problem:** Some fields may be missing or need enhancement.

**AI Solution:** Use ML to enrich data with predictions.

```python
# Missing data:
{
    "positionTitle": "Engineer",
    "grade": null,                      # AI predicts: "P3" based on title
    "level": null,                      # AI predicts: "Individual Contributor"
    "isManagerial": null                # AI predicts: false (no direct reports)
}

# AI enrichment:
{
    "grade": "P3",                      # Predicted from title pattern
    "level": "Individual Contributor",   # Predicted from title
    "isManagerial": false               # Predicted from structure
}
```

**Implementation:**
- **Classification Models:** Predict categorical fields (grade, level, type)
- **Regression Models:** Predict numerical fields (FTE, salary range)
- **Ensemble Methods:** Combine multiple models for better accuracy

---

## 🧠 Deep Learning Models for Mapping

### **1. Transformer-Based Field Matching**

**Architecture:**
```
Input: Field Name + Context
    ↓
BERT/GPT Embedding Layer
    ↓
Attention Mechanism
    ↓
Similarity Scoring
    ↓
Output: Best Match + Confidence Score
```

**Example:**
```python
# Input
field_name = "orgUnitName"
context = "Organizational structure, department hierarchy"

# Model Output
{
    "best_match": "name",
    "confidence": 0.95,
    "alternatives": [
        {"field": "org_unit_name", "confidence": 0.92},
        {"field": "department_name", "confidence": 0.88}
    ]
}
```

### **2. Graph Neural Networks for Hierarchy**

**Architecture:**
```
Org Structure Graph
    ↓
GNN Layers (GCN, GraphSAGE)
    ↓
Node Embeddings
    ↓
Relationship Prediction
    ↓
Hierarchy Validation
```

**Use Cases:**
- Detect circular references
- Infer missing parent-child relationships
- Validate org structure integrity
- Suggest optimal reporting structures

### **3. Sequence Models for Data Transformation**

**Architecture:**
```
Source Data Sequence
    ↓
LSTM/Transformer Encoder
    ↓
Transformation Rules
    ↓
LSTM/Transformer Decoder
    ↓
Target Data Format
```

**Use Cases:**
- Learn transformation patterns from examples
- Generate mapping rules automatically
- Handle complex nested data structures

---

## 🚀 AI-Powered Automapping Implementation

### **Phase 1: Field Matching AI**

```python
# backend/ai-service/app/services/field_matcher.py

from transformers import AutoModel, AutoTokenizer
import torch
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class FieldMatcherAI:
    """AI-powered field matching using NLP"""
    
    def __init__(self):
        self.model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
        self.tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
        self.target_fields = self._load_target_schema()
    
    def _load_target_schema(self):
        """Load target schema fields"""
        return {
            "employee_number": "Unique identifier for employee",
            "first_name": "Employee's first name",
            "last_name": "Employee's last name",
            "email": "Email address",
            "position_code": "Position identifier code",
            "position_title": "Job title or position name",
            "org_unit_name": "Organizational unit name",
            # ... more fields
        }
    
    def find_best_match(self, source_field: str, source_context: str = "") -> dict:
        """Find best matching target field using semantic similarity"""
        # Encode source field
        source_text = f"{source_field} {source_context}"
        source_embedding = self._encode(source_text)
        
        # Find best match
        best_match = None
        best_score = 0
        
        for target_field, target_desc in self.target_fields.items():
            target_text = f"{target_field} {target_desc}"
            target_embedding = self._encode(target_text)
            
            similarity = cosine_similarity(
                source_embedding.reshape(1, -1),
                target_embedding.reshape(1, -1)
            )[0][0]
            
            if similarity > best_score:
                best_score = similarity
                best_match = {
                    "field": target_field,
                    "confidence": float(similarity),
                    "description": target_desc
                }
        
        return best_match
    
    def _encode(self, text: str) -> np.ndarray:
        """Encode text to embedding"""
        inputs = self.tokenizer(text, return_tensors='pt', truncation=True, max_length=128)
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).numpy()[0]
```

### **Phase 2: Schema Discovery AI**

```python
# backend/ai-service/app/services/schema_discoverer.py

class SchemaDiscovererAI:
    """Automatically discover and map HRIS schemas"""
    
    async def discover_schema(self, api_url: str, credentials: dict) -> dict:
        """Discover schema from HRIS API"""
        # Fetch $metadata
        metadata = await self._fetch_metadata(api_url, credentials)
        
        # Analyze entities
        entities = {}
        for entity in metadata.get('EntityTypes', []):
            entity_name = entity['Name']
            fields = {}
            
            for prop in entity.get('Properties', []):
                field_name = prop['Name']
                field_type = prop['Type']
                
                # AI predicts field purpose
                field_purpose = self._predict_field_purpose(field_name, field_type)
                
                fields[field_name] = {
                    "type": field_type,
                    "purpose": field_purpose,
                    "suggested_mapping": self._suggest_mapping(field_purpose)
                }
            
            entities[entity_name] = fields
        
        return {
            "entities": entities,
            "suggested_mappings": self._generate_mapping_suggestions(entities)
        }
    
    def _predict_field_purpose(self, field_name: str, field_type: str) -> str:
        """Use ML to predict what a field represents"""
        # Use NLP model to classify field purpose
        # Categories: employee_id, name, email, position, org_unit, date, etc.
        pass
    
    def _suggest_mapping(self, purpose: str) -> str:
        """Suggest target field based on purpose"""
        mapping_rules = {
            "employee_id": "employee_number",
            "first_name": "first_name",
            "last_name": "last_name",
            "email": "email",
            "position_id": "position_id",
            "org_unit_name": "org_unit_name",
            # ... more rules
        }
        return mapping_rules.get(purpose, "unknown")
```

### **Phase 3: Data Quality AI**

```python
# backend/ai-service/app/services/data_quality_ai.py

class DataQualityAI:
    """AI-powered data quality detection and improvement"""
    
    def detect_issues(self, data: dict) -> list:
        """Detect data quality issues"""
        issues = []
        
        # Email validation
        if 'email' in data:
            if not self._is_valid_email(data['email']):
                issues.append({
                    "field": "email",
                    "issue": "invalid_format",
                    "severity": "high",
                    "suggestion": self._suggest_email_fix(data['email'])
                })
        
        # Missing required fields
        required_fields = ['employee_number', 'first_name', 'last_name']
        for field in required_fields:
            if field not in data or not data[field]:
                issues.append({
                    "field": field,
                    "issue": "missing",
                    "severity": "critical"
                })
        
        # Anomaly detection
        anomalies = self._detect_anomalies(data)
        issues.extend(anomalies)
        
        return issues
    
    def enrich_data(self, data: dict) -> dict:
        """Enrich data with AI predictions"""
        enriched = data.copy()
        
        # Predict missing grade
        if 'grade' not in data and 'position_title' in data:
            enriched['grade'] = self._predict_grade(data['position_title'])
        
        # Predict level
        if 'level' not in data:
            enriched['level'] = self._predict_level(data)
        
        # Infer managerial status
        if 'is_managerial' not in data:
            enriched['is_managerial'] = self._predict_managerial(data)
        
        return enriched
    
    def _predict_grade(self, position_title: str) -> str:
        """Predict job grade from title using ML"""
        # Use trained model to predict grade
        # Example: "Senior Engineer" → "P4"
        pass
    
    def _predict_level(self, data: dict) -> str:
        """Predict organizational level"""
        # Analyze position in hierarchy
        # Example: Has direct reports → "Manager"
        pass
```

---

## 📈 ML Model Training Pipeline

### **Training Data Collection**

```python
# Collect mapping examples
training_data = [
    {
        "source": {"field": "orgUnitName", "type": "string", "context": "org structure"},
        "target": {"field": "name", "confidence": 1.0}
    },
    {
        "source": {"field": "userId", "type": "string", "context": "user account"},
        "target": {"field": "employee_number", "confidence": 1.0}
    },
    # ... more examples
]

# Train model
model = train_field_matcher(training_data)
```

### **Model Architecture**

```python
# Field Matching Model
class FieldMatchingModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.encoder = AutoModel.from_pretrained('bert-base-uncased')
        self.similarity_layer = nn.Linear(768, 1)
    
    def forward(self, source_field, target_field):
        source_emb = self.encoder(source_field).pooler_output
        target_emb = self.encoder(target_field).pooler_output
        similarity = self.similarity_layer(torch.cat([source_emb, target_emb], dim=1))
        return similarity
```

---

## 🎯 Use Cases for AI/ML in Mapping

### **1. Multi-HRIS Support**

**Challenge:** Different HRIS systems have different schemas.

**AI Solution:**
- Automatically detect HRIS system type
- Load appropriate mapping model
- Apply intelligent field matching

```python
# Detect HRIS type
hris_type = ai_detector.detect_system(api_response)

# Load appropriate model
mapper = load_mapper_model(hris_type)  # successfactors, workday, bamboohr

# Apply mapping
mapped_data = mapper.map(data)
```

### **2. Custom Field Mapping**

**Challenge:** Organizations have custom fields in SuccessFactors.

**AI Solution:**
- Discover custom fields automatically
- Suggest mappings based on field names and types
- Learn from user corrections

```python
# Discover custom fields
custom_fields = discoverer.find_custom_fields(metadata)

# AI suggests mappings
for field in custom_fields:
    suggestion = ai_matcher.suggest_mapping(field)
    # User confirms or corrects
    # AI learns from feedback
```

### **3. Data Migration**

**Challenge:** Migrating from one HRIS to another requires complex mapping.

**AI Solution:**
- Learn mapping patterns from historical migrations
- Suggest optimal mappings
- Validate data consistency

### **4. Real-time Sync Intelligence**

**Challenge:** Data changes in SuccessFactors need intelligent handling.

**AI Solution:**
- Detect significant changes (promotions, transfers)
- Predict impact on org structure
- Suggest optimizations

---

## 🔧 Implementation Roadmap

### **Phase 1: Basic AI Matching (Current)**
- ✅ Manual mapping rules
- ✅ Basic field transformation
- ✅ Relationship resolution

### **Phase 2: Intelligent Matching (Next)**
- 🔄 NLP-based field matching
- 🔄 Schema discovery
- 🔄 Confidence scoring

### **Phase 3: Deep Learning (Future)**
- 📋 Transformer models for field matching
- 📋 Graph neural networks for hierarchy
- 📋 Sequence models for transformation

### **Phase 4: Continuous Learning (Advanced)**
- 📋 Learn from user corrections
- 📋 Improve mappings over time
- 📋 Predictive data enrichment

---

## 📚 Technical Stack for AI Mapping

### **NLP & Embeddings**
- **Models:** BERT, GPT, Sentence Transformers
- **Libraries:** Hugging Face Transformers, spaCy
- **Use Case:** Field name semantic matching

### **Graph Neural Networks**
- **Models:** GCN, GraphSAGE, GAT
- **Libraries:** PyTorch Geometric, DGL
- **Use Case:** Org hierarchy analysis

### **Classification & Prediction**
- **Models:** Random Forest, XGBoost, Neural Networks
- **Libraries:** scikit-learn, TensorFlow, PyTorch
- **Use Case:** Data enrichment, quality prediction

### **Anomaly Detection**
- **Models:** Isolation Forest, Autoencoders
- **Libraries:** scikit-learn, PyOD
- **Use Case:** Data quality issues

---

## 🎓 Example: AI-Powered Mapping Flow

```
1. User connects SuccessFactors
   ↓
2. AI discovers schema automatically
   ├─ Fetches $metadata
   ├─ Analyzes entities and fields
   └─ Predicts field purposes
   ↓
3. AI suggests mappings
   ├─ Field matching (NLP similarity)
   ├─ Confidence scores
   └─ Alternative suggestions
   ↓
4. User reviews and confirms
   ├─ Accepts high-confidence mappings
   ├─ Corrects low-confidence mappings
   └─ AI learns from corrections
   ↓
5. AI applies mappings
   ├─ Transforms data
   ├─ Validates quality
   └─ Enriches missing data
   ↓
6. Data synced to database
   ↓
7. Org chart built and displayed
```

---

## 🚀 Quick Start: Enable AI Mapping

### **Step 1: Install AI Dependencies**

```bash
cd backend/ai-service
pip install transformers torch sentence-transformers scikit-learn
```

### **Step 2: Enable AI Matching**

```python
# In HRIS service
from ai_service.field_matcher import FieldMatcherAI

matcher = FieldMatcherAI()
best_match = matcher.find_best_match("orgUnitName", "organizational structure")
# Returns: {"field": "name", "confidence": 0.95}
```

### **Step 3: Use in Data Transformation**

```python
# Enhanced transformer with AI
class AIDataTransformer(DataTransformer):
    def __init__(self):
        self.ai_matcher = FieldMatcherAI()
    
    def transform_with_ai(self, source_data: dict) -> dict:
        mapped = {}
        for source_field, value in source_data.items():
            match = self.ai_matcher.find_best_match(source_field)
            if match['confidence'] > 0.8:
                mapped[match['field']] = value
        return mapped
```

---

## 📊 Current vs AI-Powered Mapping

| Feature | Current (Manual) | AI-Powered |
|---------|-----------------|------------|
| **Field Matching** | Hardcoded rules | Semantic similarity (NLP) |
| **Schema Discovery** | Manual configuration | Automatic discovery |
| **Data Quality** | Basic validation | ML-based anomaly detection |
| **Missing Data** | Left empty | AI prediction/enrichment |
| **Custom Fields** | Manual mapping | Auto-suggestions |
| **Learning** | Static rules | Continuous improvement |

---

## 🎯 Next Steps

1. **Implement Basic AI Matching** - Start with NLP-based field matching
2. **Add Schema Discovery** - Automatically discover SuccessFactors schema
3. **Enable Data Enrichment** - Use ML to fill missing fields
4. **Build Learning System** - Learn from user corrections
5. **Add Predictive Features** - Predict org changes and optimizations

---

**The foundation is in place. Now we can add AI intelligence to make mapping automatic and intelligent!** 🚀
