"""
Audit Middleware
Tracks all changes with timestamps and user information
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
from typing import Callable
import json

class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware to track all API requests and changes"""
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """Process request and log audit trail"""
        
        # Get user ID from headers or token
        user_id = request.headers.get("X-User-ID", "system")
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("User-Agent")
        
        # Add to request state for use in routes
        request.state.user_id = user_id
        request.state.ip_address = ip_address
        request.state.user_agent = user_agent
        
        # Process request
        start_time = datetime.now()
        response = await call_next(request)
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Log audit trail for POST/PUT/DELETE
        if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
            # Audit logging is handled by database triggers
            # But we can log API access here if needed
            pass
        
        return response
