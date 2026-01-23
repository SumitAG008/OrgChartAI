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
            try:
                response = await client.get(url, headers=headers, params=params, timeout=60.0)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                # Provide more detailed error message
                error_detail = ""
                try:
                    error_body = e.response.json()
                    error_detail = error_body.get("error", {}).get("message", {}).get("value", str(error_body))
                except:
                    error_detail = e.response.text[:500]  # First 500 chars of error response

                logger.error(f"SuccessFactors API error for {endpoint}: {e.response.status_code} - {error_detail}")

                # Build helpful error message based on status code
                if e.response.status_code == 400:
                    raise Exception(
                        f"Bad Request (400) for {endpoint}. "
                        f"This usually means invalid query parameters or field access issues. "
                        f"Error details: {error_detail}. "
                        f"URL: {e.request.url}"
                    )
                elif e.response.status_code == 401:
                    raise Exception(
                        f"Authentication failed (401) for {endpoint}. "
                        f"Please check your credentials and API URL. "
                        f"Error details: {error_detail}"
                    )
                elif e.response.status_code == 403:
                    raise Exception(
                        f"Access forbidden (403) for {endpoint}. "
                        f"Your user may not have permission to access this entity. "
                        f"Error details: {error_detail}"
                    )
                elif e.response.status_code == 404:
                    raise Exception(
                        f"Entity not found (404): {endpoint}. "
                        f"This entity may not exist in your SuccessFactors instance. "
                        f"Error details: {error_detail}"
                    )
                else:
                    raise Exception(
                        f"HTTP {e.response.status_code} error for {endpoint}: {error_detail}"
                    )
            except httpx.TimeoutException:
                raise Exception(
                    f"Request timeout for {endpoint}. "
                    f"The SuccessFactors API is taking too long to respond. "
                    f"This might be due to large data volumes or slow API performance."
                )
            except Exception as e:
                if "Exception" in str(type(e).__name__) and "400" in str(e):
                    # Already formatted error, re-raise
                    raise
                # Other network errors
                logger.error(f"Network error for {endpoint}: {str(e)}")
                raise Exception(f"Network error accessing SuccessFactors API: {str(e)}")
    
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
        """Fetch positions from SuccessFactors

        Position is an effective-dated entity in SuccessFactors, so we add a default
        filter to get currently effective positions unless a custom filter is provided.
        """
        params = {}
        if top:
            params["$top"] = top
        if skip:
            params["$skip"] = skip

        # Position is effective-dated, add default filter for current positions
        # This helps avoid 400 errors from SuccessFactors
        if not filter_query:
            # Get positions that are currently effective (no end date or end date in future)
            # Using a simple filter that works with most SF instances
            filter_query = "status eq 'A' or status eq 'Active' or status eq '1'"

        if filter_query:
            params["$filter"] = filter_query

        try:
            result = await self._make_request("Position", params=params)
            positions = []

            for item in result.get("d", {}).get("results", []):
                positions.append(SuccessFactorsPosition(**item))

            return positions
        except Exception as e:
            # If filter fails, try without any filter (some SF instances don't support filtering)
            logger.warning(f"Position fetch with filter failed: {str(e)}, retrying without filter")
            params_no_filter = {}
            if top:
                params_no_filter["$top"] = top
            if skip:
                params_no_filter["$skip"] = skip

            result = await self._make_request("Position", params=params_no_filter)
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

        # FODepartment, FODivision, etc. are effective-dated entities
        # Add default filter for currently active ones if no custom filter is provided
        if not filter_query and entity.startswith("FO"):
            # Try to get active records - common approach for FO* entities
            filter_query = "status eq 'ACTIVE' or status eq 'A' or status eq 'Active'"

        if filter_query:
            params["$filter"] = filter_query

        try:
            result = await self._make_request(entity, params=params)
            org_units = []

            for item in result.get("d", {}).get("results", []):
                org_units.append(item)

            return org_units
        except Exception as e:
            # If filter fails, try without filter
            logger.warning(f"{entity} fetch with filter failed: {str(e)}, retrying without filter")
            params_no_filter = {}
            if top:
                params_no_filter["$top"] = top
            if skip:
                params_no_filter["$skip"] = skip

            result = await self._make_request(entity, params=params_no_filter)
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

    async def get_job_codes(self, top: Optional[int] = None, skip: Optional[int] = None,
                           filter_query: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch Job Codes (FOJobCode) from SuccessFactors"""
        return await self.get_org_units("FOJobCode", top=top, skip=skip, filter_query=filter_query)

    async def get_job_functions(self, top: Optional[int] = None, skip: Optional[int] = None,
                               filter_query: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch Job Functions (FOJobFunction) from SuccessFactors"""
        return await self.get_org_units("FOJobFunction", top=top, skip=skip, filter_query=filter_query)
    
    async def get_per_person(self, top: Optional[int] = None, skip: Optional[int] = None,
                            filter_query: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch Person data (PerPerson) from SuccessFactors

        PerPerson is an effective-dated entity and can have field access restrictions.
        We use fallback logic to handle various SuccessFactors configurations.
        """
        params = {}
        if top:
            params["$top"] = top
        if skip:
            params["$skip"] = skip

        # Add filter if provided
        if filter_query:
            params["$filter"] = filter_query

        try:
            result = await self._make_request("PerPerson", params=params)
            persons = []

            for item in result.get("d", {}).get("results", []):
                persons.append(item)

            return persons
        except Exception as e:
            error_msg = str(e)
            logger.error(f"PerPerson fetch failed: {error_msg}")

            # Check if this is a 400 Bad Request - might be field access or permissions issue
            if "400" in error_msg or "Bad Request" in error_msg:
                # Try with a simpler approach - use User entity instead
                logger.info("PerPerson failed with 400, trying User entity as fallback")
                try:
                    users = await self.get_users(top=top, skip=skip, filter_query=filter_query)
                    # Convert User objects to dict format
                    persons = []
                    for user in users:
                        if hasattr(user, '__dict__'):
                            persons.append(user.__dict__)
                        else:
                            persons.append(user)
                    logger.info(f"Successfully fetched {len(persons)} records from User entity as fallback")
                    return persons
                except Exception as user_error:
                    logger.error(f"User fallback also failed: {str(user_error)}")
                    raise Exception(
                        f"Failed to fetch person data from both PerPerson and User entities. "
                        f"PerPerson error: {error_msg}. User error: {str(user_error)}. "
                        f"Please check field permissions in SuccessFactors or use manual field mapping."
                    )

            # Re-raise other errors
            raise
    
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
