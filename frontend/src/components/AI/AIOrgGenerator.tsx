import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Sparkles, CheckCircle, XCircle, Save, 
  RefreshCw, AlertCircle, TrendingUp, Users,
  Layers, Target, Zap
} from 'lucide-react';

interface Recommendation {
  type: string;
  severity: 'info' | 'warning' | 'error';
  message: string;
  suggestion: string;
}

interface GeneratedStructure {
  structure: any;
  metrics: {
    total_positions: number;
    hierarchy_levels: number;
    average_span_of_control: number;
    max_span_of_control: number;
    min_span_of_control: number;
  };
  recommendations: Recommendation[];
  confidence_score: number;
}

const AIOrgGenerator: React.FC = () => {
  const [requirements, setRequirements] = useState({
    headcount: 100,
    departments: ['Engineering', 'Sales', 'Marketing', 'Operations'],
    hierarchy_levels: 4,
    span_of_control: '5-8',
    budget: 5000000
  });
  const [generating, setGenerating] = useState(false);
  const [generatedStructure, setGeneratedStructure] = useState<GeneratedStructure | null>(null);
  const [saving, setSaving] = useState(false);
  const [draftName, setDraftName] = useState('');

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      const response = await fetch('http://localhost:8001/api/v1/ai/org/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          requirements: requirements,
          constraints: {
            max_layers: 5,
            min_span: 3,
            max_span: 10
          }
        })
      });
      
      const result = await response.json();
      setGeneratedStructure(result);
    } catch (error) {
      console.error('Error generating structure:', error);
      alert('Error generating structure. Please try again.');
    } finally {
      setGenerating(false);
    }
  };

  const handleSaveDraft = async () => {
    if (!draftName.trim()) {
      alert('Please enter a name for the draft');
      return;
    }

    if (!generatedStructure) return;

    setSaving(true);
    try {
      const response = await fetch('http://localhost:8001/api/v1/ai/org/save-draft', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          structure: generatedStructure.structure,
          name: draftName,
          description: `Generated structure with ${generatedStructure.metrics.total_positions} positions`
        })
      });
      
      const result = await response.json();
      if (result.success) {
        alert('Draft saved successfully!');
        setDraftName('');
        // Optionally reset or navigate
      }
    } catch (error) {
      console.error('Error saving draft:', error);
      alert('Error saving draft. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="p-6 bg-white rounded-lg shadow-lg">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-12 h-12 bg-gradient-to-r from-green-600 to-emerald-600 rounded-lg flex items-center justify-center">
          <Sparkles className="w-6 h-6 text-white" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-gray-900">AI Org Structure Generator</h2>
          <p className="text-gray-600">Generate and recommend optimal organizational structures</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Requirements Input */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
            <Target className="w-5 h-5 text-green-600" />
            Requirements
          </h3>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Total Headcount
            </label>
            <input
              type="number"
              value={requirements.headcount}
              onChange={(e) => setRequirements({...requirements, headcount: parseInt(e.target.value) || 0})}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
              min="1"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Departments (comma-separated)
            </label>
            <input
              type="text"
              value={requirements.departments.join(', ')}
              onChange={(e) => setRequirements({
                ...requirements, 
                departments: e.target.value.split(',').map(d => d.trim()).filter(d => d)
              })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
              placeholder="Engineering, Sales, Marketing"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Hierarchy Levels
            </label>
            <input
              type="number"
              value={requirements.hierarchy_levels}
              onChange={(e) => setRequirements({...requirements, hierarchy_levels: parseInt(e.target.value) || 3})}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
              min="2"
              max="6"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Target Span of Control
            </label>
            <input
              type="text"
              value={requirements.span_of_control}
              onChange={(e) => setRequirements({...requirements, span_of_control: e.target.value})}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
              placeholder="5-8"
            />
          </div>

          <button
            onClick={handleGenerate}
            disabled={generating}
            className="w-full px-4 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-lg hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
          >
            {generating ? (
              <>
                <RefreshCw className="w-5 h-5 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Zap className="w-5 h-5" />
                Generate Structure
              </>
            )}
          </button>
        </div>

        {/* Generated Structure & Recommendations */}
        <div className="space-y-4">
          {generatedStructure ? (
            <>
              <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-lg p-4 border border-green-200">
                <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-green-600" />
                  Generated Structure
                </h3>
                
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div className="bg-white rounded-lg p-3">
                    <div className="text-sm text-gray-600">Total Positions</div>
                    <div className="text-2xl font-bold text-gray-900">{generatedStructure.metrics.total_positions}</div>
                  </div>
                  <div className="bg-white rounded-lg p-3">
                    <div className="text-sm text-gray-600">Hierarchy Levels</div>
                    <div className="text-2xl font-bold text-gray-900">{generatedStructure.metrics.hierarchy_levels}</div>
                  </div>
                  <div className="bg-white rounded-lg p-3">
                    <div className="text-sm text-gray-600">Avg Span</div>
                    <div className="text-2xl font-bold text-gray-900">
                      {generatedStructure.metrics.average_span_of_control.toFixed(1)}
                    </div>
                  </div>
                  <div className="bg-white rounded-lg p-3">
                    <div className="text-sm text-gray-600">Confidence</div>
                    <div className="text-2xl font-bold text-green-600">
                      {(generatedStructure.confidence_score * 100).toFixed(0)}%
                    </div>
                  </div>
                </div>
              </div>

              {/* Recommendations */}
              {generatedStructure.recommendations.length > 0 && (
                <div className="space-y-2">
                  <h4 className="font-semibold text-gray-900 flex items-center gap-2">
                    <AlertCircle className="w-5 h-5 text-amber-500" />
                    Recommendations
                  </h4>
                  {generatedStructure.recommendations.map((rec, idx) => (
                    <div
                      key={idx}
                      className={`p-3 rounded-lg border ${
                        rec.severity === 'warning' ? 'bg-amber-50 border-amber-200' :
                        rec.severity === 'error' ? 'bg-red-50 border-red-200' :
                        'bg-blue-50 border-blue-200'
                      }`}
                    >
                      <div className="font-medium text-sm mb-1">{rec.message}</div>
                      <div className="text-xs text-gray-600">{rec.suggestion}</div>
                    </div>
                  ))}
                </div>
              )}

              {/* Save as Draft */}
              <div className="border-t border-gray-200 pt-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Save as Draft
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={draftName}
                    onChange={(e) => setDraftName(e.target.value)}
                    placeholder="Enter draft name..."
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                  />
                  <button
                    onClick={handleSaveDraft}
                    disabled={saving || !draftName.trim()}
                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                  >
                    {saving ? (
                      <RefreshCw className="w-4 h-4 animate-spin" />
                    ) : (
                      <Save className="w-4 h-4" />
                    )}
                    Save
                  </button>
                </div>
              </div>
            </>
          ) : (
            <div className="text-center py-12 border-2 border-dashed border-gray-300 rounded-lg">
              <Sparkles className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-700 mb-2">No Structure Generated</h3>
              <p className="text-gray-500">Fill in requirements and click "Generate Structure" to get started</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AIOrgGenerator;
