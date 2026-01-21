"""
MCP (Model Context Protocol) Client
Integration with AI models via MCP for org chart generation
"""

from typing import Dict, Any, Optional, List
import httpx
import json
from app.config import settings

class MCPClient:
    """Client for MCP (Model Context Protocol) integration"""
    
    def __init__(self):
        self.base_url = getattr(settings, 'MCP_BASE_URL', 'http://localhost:8002')
        self.api_key = getattr(settings, 'MCP_API_KEY', None)
    
    async def list_available_models(self) -> List[Dict[str, Any]]:
        """List all available MCP models"""
        # MCP models for org chart generation
        return [
            {
                "id": "gpt-4-turbo",
                "name": "GPT-4 Turbo",
                "provider": "OpenAI",
                "capabilities": ["org_generation", "team_formation", "org_design"],
                "max_tokens": 4096
            },
            {
                "id": "claude-3-opus",
                "name": "Claude 3 Opus",
                "provider": "Anthropic",
                "capabilities": ["org_generation", "team_formation", "org_design"],
                "max_tokens": 4096
            },
            {
                "id": "local-llama",
                "name": "Llama 2 (Local)",
                "provider": "Local",
                "capabilities": ["org_generation"],
                "max_tokens": 2048
            }
        ]
    
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate response using MCP
        
        Args:
            prompt: Input prompt
            model: Model ID (default: gpt-4-turbo)
            context: Additional context for the model
        
        Returns:
            Response with generated content
        """
        model = model or "gpt-4-turbo"
        
        # MCP request format
        request_data = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": self._get_system_prompt(context)
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 4096
        }
        
        # If MCP server is available, use it
        # Otherwise, use direct API calls
        if self.api_key:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    json=request_data,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=60.0
                )
                response.raise_for_status()
                return response.json()
        else:
            # Fallback: Return structured response
            return {
                "id": "mock-response",
                "model": model,
                "content": self._mock_generate(prompt, context),
                "usage": {
                    "prompt_tokens": len(prompt.split()),
                    "completion_tokens": 100,
                    "total_tokens": len(prompt.split()) + 100
                }
            }
    
    def _get_system_prompt(self, context: Optional[Dict[str, Any]]) -> str:
        """Get system prompt based on context"""
        base_prompt = """You are an expert organizational design consultant specializing in creating optimal organizational structures.
        
        Your task is to analyze organizational data and generate well-structured, efficient org charts.
        Always return valid JSON responses matching the requested schema.
        """
        
        if context:
            task = context.get("task", "")
            if task == "org_data_analysis":
                return base_prompt + "\nAnalyze the provided data and extract organizational structure information."
            elif task == "org_structure_generation":
                return base_prompt + "\nGenerate a complete organizational structure based on the analysis."
            elif task == "team_formation":
                return base_prompt + "\nRecommend optimal team compositions for projects."
            elif task == "org_design":
                return base_prompt + "\nRecommend organizational design improvements."
        
        return base_prompt
    
    def _mock_generate(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Mock generation for development/testing"""
        # Return sample JSON structure
        return json.dumps({
            "org_units": [
                {
                    "id": "ou-1",
                    "name": "Engineering",
                    "type": "Department"
                }
            ],
            "positions": [
                {
                    "id": "pos-1",
                    "title": "VP Engineering",
                    "reports_to": None
                }
            ],
            "jobs": [],
            "hierarchy": {}
        }, indent=2)
