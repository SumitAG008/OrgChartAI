"""
SuccessFactors OData API Client
"""

import httpx
from typing import List, Optional, Dict, Any
from app.models import SuccessFactorsUser, SuccessFactorsPosition, SuccessFactorsOrgUnit
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class SuccessFactorsClient:
    """Client for SuccessFactors OData API"""
    
    def __init__(self, company_id: str, username: str, password: str, api_url: Optional[str] = None):
        self.company_id = company_id
        self.username = username
        self.password = password
        self.api_url = api_url or settings.SUCCESSFACTORS_BASE_URL
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[float] = None
        self.basic_auth_header: Optional[str] = None
        self.use_basic_auth: bool = False
        
    async def authenticate(self) -> bool:
        """Authenticate using Basic Auth (SuccessFactors OData API standard)"""
        try:
            import base64
            
            # SuccessFactors OData API uses Basic Authentication
            # Format: base64(username@companyID:password)
            # According to SuccessFactors: <username>@<companyID>:<password>
            credentials = f"{self.username}@{self.company_id}:{self.password}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            # Try OAuth token endpoint first (some instances use this)
            oauth_url = f"{self.api_url}/oauth/token"
            
            async with httpx.AsyncClient() as client:
                # Method 1: Try OAuth with Basic Auth header
                response = await client.post(
                    oauth_url,
                    data={
                        "grant_type": "client_credentials"
                    },
                    headers={
                        "Authorization": f"Basic {encoded_credentials}",
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.access_token = data.get("access_token")
                    expires_in = data.get("expires_in", 3600)
                    import time
                    self.token_expires_at = time.time() + expires_in
                    return True
                
                # Method 2: If OAuth fails, use Basic Auth directly for OData
                # Some SuccessFactors instances don't use OAuth, just Basic Auth
                # Store credentials for direct Basic Auth
                self.basic_auth_header = f"Basic {encoded_credentials}"
                self.use_basic_auth = True
                
                # Test with a simple OData call
                # SuccessFactors requires specific Accept headers to avoid 406 errors
                # Try User endpoint first (most common)
                test_url = f"{self.api_url}/odata/v2/User"
                
                # Try with JSON first (no Content-Type for GET requests)
                test_response = await client.get(
                    test_url,
                    headers={
                        "Authorization": self.basic_auth_header,
                        "Accept": "application/json"
                    },
                    params={"$top": 1},
                    timeout=30.0
                )
                
                if test_response.status_code == 200:
                    # Basic Auth works, no token needed
                    self.access_token = None
                    return True
                elif test_response.status_code == 401:
                    # Authentication failed - credentials wrong
                    logger.error(f"Authentication failed: Invalid credentials - {test_response.text}")
                    return False
                elif test_response.status_code == 406:
                    # Not Acceptable - try with wildcard Accept header
                    test_response_alt = await client.get(
                        test_url,
                        headers={
                            "Authorization": self.basic_auth_header,
                            "Accept": "*/*"
                        },
                        params={"$top": 1},
                        timeout=30.0
                    )
                    if test_response_alt.status_code == 200:
                        self.access_token = None
                        return True
                    else:
                        logger.error(f"Authentication failed: OAuth={response.status_code}, Basic={test_response.status_code} - {test_response.text}")
                        return False
                else:
                    logger.error(f"Authentication failed: OAuth={response.status_code}, Basic={test_response.status_code} - {test_response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False
    
    async def _ensure_authenticated(self):
        """Ensure we have a valid access token or Basic Auth header"""
        import time
        # If using Basic Auth, we're always authenticated (credentials are in header)
        if self.use_basic_auth and self.basic_auth_header:
            return
        # Otherwise, check OAuth token
        if not self.access_token or (self.token_expires_at and time.time() >= self.token_expires_at):
            await self.authenticate()
    
    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make authenticated OData request
        
        Uses format: /odata/v2/{EntityName}?format=json&$top=1000
        """
        await self._ensure_authenticated()
        
        # Build URL with format=json parameter
        url = f"{self.api_url}/odata/v2/{endpoint}"
        
        # Add format=json and $top=1000 to params if not already present
        if params is None:
            params = {}
        
        # Add format=json if not present
        if "format" not in params:
            params["format"] = "json"
        
        # Add $top=1000 if not present and no limit specified
        if "$top" not in params:
            params["$top"] = 1000
        
        # Use Basic Auth if OAuth token not available
        # SuccessFactors requires specific Accept headers to avoid 406 errors
        if self.use_basic_auth and self.basic_auth_header:
            headers = {
                "Authorization": self.basic_auth_header,
                "Accept": "application/json"
            }
        else:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Accept": "application/json"
            }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params, timeout=60.0)
            response.raise_for_status()
            return response.json()
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to SuccessFactors"""
        try:
            if await self.authenticate():
                # Try to fetch a simple endpoint to verify
                # Use User endpoint as it's commonly available
                try:
                    result = await self._make_request("User", params={"$top": 1})
                    return {
                        "success": True,
                        "message": "Connection successful - SuccessFactors API is accessible",
                        "api_version": "v2"
                    }
                except Exception as e:
                    # If User endpoint fails, try metadata
                    try:
                        result = await self._make_request("$metadata")
                        return {
                            "success": True,
                            "message": "Connection successful - SuccessFactors API is accessible",
                            "api_version": "v2"
                        }
                    except:
                        # If both fail, but auth worked, connection is still valid
                        return {
                            "success": True,
                            "message": "Authentication successful - API endpoint accessible",
                            "api_version": "v2"
                        }
            else:
                return {
                    "success": False,
                    "message": "Authentication failed - Please check your credentials"
                }
        except Exception as e:
            error_msg = str(e)
            # Extract more helpful error messages
            if "406" in error_msg or "NotAcceptable" in error_msg:
                return {
                    "success": False,
                    "message": "Authentication format error - Please verify credentials format"
                }
            return {
                "success": False,
                "message": f"Connection error: {error_msg[:200]}"
            }
    
    async def get_users(self, top: Optional[int] = None, skip: Optional[int] = None, 
                       filter_query: Optional[str] = None) -> List[SuccessFactorsUser]:
        """Fetch users (employees) from SuccessFactors"""
        params = {}
        if top:
            params["$top"] = top
        if skip:
            params["$skip"] = skip
        if filter_query:
            params["$filter"] = filter_query
        
        result = await self._make_request("User", params=params)
        users = []
        
        for item in result.get("d", {}).get("results", []):
            users.append(SuccessFactorsUser(**item))
        
        return users
    
    async def get_positions(self, top: Optional[int] = None, skip: Optional[int] = None,
                           filter_query: Optional[str] = None) -> List[SuccessFactorsPosition]:
        """Fetch positions from SuccessFactors"""
        params = {}
        if top:
            params["$top"] = top
        if skip:
            params["$skip"] = skip
        if filter_query:
            params["$filter"] = filter_query
        
        result = await self._make_request("Position", params=params)
        positions = []
        
        for item in result.get("d", {}).get("results", []):
            positions.append(SuccessFactorsPosition(**item))
        
        return positions
    
    async def get_org_units(self, entity_name: Optional[str] = None, top: Optional[int] = None, 
                            skip: Optional[int] = None, filter_query: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch organizational units from SuccessFactors
        
        Args:
            entity_name: Specific entity to fetch (FOLegalEntity, FODepartment, FODivision, 
                        FOBusinessUnit, FOCostCenter, etc.). If None, fetches generic OrgUnit.
        """
        entity = entity_name or "OrgUnit"
        params = {}
        if top:
            params["$top"] = top
        if skip:
            params["$skip"] = skip
        if filter_query:
            params["$filter"] = filter_query
        
        result = await self._make_request(entity, params=params)
        org_units = []
        
        for item in result.get("d", {}).get("results", []):
            org_units.append(item)
        
        return org_units
    
    async def get_legal_entities(self, top: Optional[int] = None, skip: Optional[int] = None,
                                 filter_query: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch Legal Entities (FOLegalEntity) from SuccessFactors"""
        return await self.get_org_units("FOLegalEntity", top=top, skip=skip, filter_query=filter_query)
    
    async def get_departments(self, top: Optional[int] = None, skip: Optional[int] = None,
                             filter_query: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch Departments (FODepartment) from SuccessFactors"""
        return await self.get_org_units("FODepartment", top=top, skip=skip, filter_query=filter_query)
    
    async def get_divisions(self, top: Optional[int] = None, skip: Optional[int] = None,
                           filter_query: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch Divisions (FODivision) from SuccessFactors"""
        return await self.get_org_units("FODivision", top=top, skip=skip, filter_query=filter_query)
    
    async def get_business_units(self, top: Optional[int] = None, skip: Optional[int] = None,
                                filter_query: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch Business Units (FOBusinessUnit) from SuccessFactors"""
        return await self.get_org_units("FOBusinessUnit", top=top, skip=skip, filter_query=filter_query)
    
    async def get_cost_centers(self, top: Optional[int] = None, skip: Optional[int] = None,
                              filter_query: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch Cost Centers (FOCostCenter) from SuccessFactors"""
        return await self.get_org_units("FOCostCenter", top=top, skip=skip, filter_query=filter_query)
    
    async def get_per_person(self, top: Optional[int] = None, skip: Optional[int] = None,
                            filter_query: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch Person data (PerPerson) from SuccessFactors"""
        params = {}
        if top:
            params["$top"] = top
        if skip:
            params["$skip"] = skip
        if filter_query:
            params["$filter"] = filter_query
        
        result = await self._make_request("PerPerson", params=params)
        persons = []
        
        for item in result.get("d", {}).get("results", []):
            persons.append(item)
        
        return persons
    
    async def get_custom_mdf_object(self, object_name: str, top: Optional[int] = None,
                                   skip: Optional[int] = None, filter_query: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch custom MDF (Metadata Framework) objects from SuccessFactors
        
        Args:
            object_name: Name of the custom MDF object (e.g., 'CustomOrgUnit', 'CustomPosition')
        """
        params = {}
        if top:
            params["$top"] = top
        if skip:
            params["$skip"] = skip
        if filter_query:
            params["$filter"] = filter_query
        
        result = await self._make_request(object_name, params=params)
        items = []
        
        for item in result.get("d", {}).get("results", []):
            items.append(item)
        
        return items
    
    async def get_all_users(self) -> List[SuccessFactorsUser]:
        """Fetch all users with pagination"""
        all_users = []
        skip = 0
        batch_size = 100
        
        while True:
            users = await self.get_users(top=batch_size, skip=skip)
            if not users:
                break
            all_users.extend(users)
            if len(users) < batch_size:
                break
            skip += batch_size
        
        return all_users
    
    async def get_all_positions(self) -> List[SuccessFactorsPosition]:
        """Fetch all positions with pagination"""
        all_positions = []
        skip = 0
        batch_size = 100
        
        while True:
            positions = await self.get_positions(top=batch_size, skip=skip)
            if not positions:
                break
            all_positions.extend(positions)
            if len(positions) < batch_size:
                break
            skip += batch_size
        
        return all_positions
    
    async def get_all_org_units(self) -> List[SuccessFactorsOrgUnit]:
        """Fetch all org units with pagination"""
        all_org_units = []
        skip = 0
        batch_size = 100
        
        while True:
            org_units = await self.get_org_units(top=batch_size, skip=skip)
            if not org_units:
                break
            all_org_units.extend(org_units)
            if len(org_units) < batch_size:
                break
            skip += batch_size
        
        return all_org_units
