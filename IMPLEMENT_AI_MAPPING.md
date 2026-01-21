# How to Implement AI-Powered Automapping

## 🎯 Quick Implementation Guide

### **Step 1: Install AI Dependencies**

```bash
cd backend/ai-service
pip install transformers torch sentence-transformers scikit-learn numpy
```

### **Step 2: Enable AI Matching in Data Transformer**

```python
# backend/hris-service/app/services/data_transformer.py

from ai_service.field_matcher_ai import FieldMatcherAI

class AIDataTransformer(DataTransformer):
    def __init__(self):
        self.ai_matcher = FieldMatcherAI()
        self.use_ai_mapping = True  # Toggle AI on/off
    
    def transform_with_ai(self, source_data: dict, entity_type: str) -> dict:
        """Transform using AI-powered field matching"""
        if not self.use_ai_mapping:
            return self.transform_successfactors_org_unit(source_data)  # Fallback to manual
        
        # Get AI mapping suggestions
        mappings = self.ai_matcher.discover_schema_mappings(
            source_schema={k: {"type": "string"} for k in source_data.keys()},
            entity_category=entity_type
        )
        
        # Apply mappings
        transformed = {}
        for source_field, value in source_data.items():
            if source_field in mappings:
                match = mappings[source_field]
                if match["confidence"] > 0.7:  # High confidence
                    transformed[match["best_match"]] = value
                else:
                    # Low confidence - use manual fallback
                    transformed[source_field] = value
        
        return transformed
```

### **Step 3: Add AI Mapping UI**

```typescript
// frontend/src/components/HRIS/AIMappingSuggestions.tsx

interface MappingSuggestion {
  sourceField: string;
  targetField: string;
  confidence: number;
  alternatives: Array<{field: string; confidence: number}>;
}

const AIMappingSuggestions: React.FC<{
  suggestions: MappingSuggestion[];
  onConfirm: (mappings: Record<string, string>) => void;
}> = ({ suggestions, onConfirm }) => {
  // Display AI suggestions
  // User can accept/reject/modify
  // Send confirmed mappings to backend
};
```

---

## 🧠 How AI Models Work for Mapping

### **1. Semantic Field Matching (NLP)**

**Technology:** Sentence Transformers, BERT

**How it works:**
```
"orgUnitName" → Embedding Vector → Compare with "name" → Similarity: 0.95
```

**Example:**
```python
# AI understands these mean the same thing:
"orgUnitName" ≈ "Organization Name" ≈ "Department Name" ≈ "name"
```

### **2. Graph Neural Networks (Hierarchy)**

**Technology:** GCN, GraphSAGE

**How it works:**
```
Org Structure Graph → GNN → Learn Patterns → Infer Missing Links
```

**Use Case:**
- Detect missing parent-child relationships
- Validate org structure integrity
- Suggest optimal reporting structures

### **3. Classification Models (Data Enrichment)**

**Technology:** Random Forest, Neural Networks

**How it works:**
```
Position Title → ML Model → Predict Grade, Level, Type
```

**Example:**
```python
Input: "Senior Software Engineer"
Output: {
    "grade": "P4",
    "level": "Individual Contributor",
    "isManagerial": false
}
```

---

## 📊 Current Mapping vs AI Mapping

### **Current (Manual)**
```python
# Hardcoded rules
"orgUnitName" → "name"  # Manual rule
"orgUnitCode" → "code"  # Manual rule
```

### **AI-Powered (Automatic)**
```python
# AI discovers automatically
"orgUnitName" → AI suggests "name" (confidence: 0.95) ✅
"customField01" → AI suggests "notes" (confidence: 0.72) ⚠️ Review
```

---

**The AI mapping foundation is ready. You can now enable it to automatically discover and map SuccessFactors fields!** 🚀
