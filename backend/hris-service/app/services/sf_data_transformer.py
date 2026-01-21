"""
SuccessFactors Data Transformer
Transforms SF OData responses to OrgChartAI data model
Handles actual SF field names and structures
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, date
import logging
from app.models_successfactors import (
    FOBusinessUnit, FODepartment, FODivision, FOCostCenter, FOLegalEntity, FOLocation,
    User, EmpJob, Position, PerPerson,
    SF_TO_ORGCHART_MAPPINGS, STATUS_MAPPINGS
)

logger = logging.getLogger(__name__)

class SFDataTransformer:
    """Transform SuccessFactors data to OrgChartAI format"""

    def __init__(self):
        self.mappings = SF_TO_ORGCHART_MAPPINGS
        self.lookup_cache = {
            "org_units": {},  # externalCode -> id
            "positions": {},  # code -> id
            "employees": {},  # userId -> id
            "cost_centers": {},  # externalCode -> id
            "legal_entities": {},  # externalCode -> id
        }

    # ============================================
    # Generic Transformation
    # ============================================

    def transform_entity(
        self,
        sf_data: Dict[str, Any],
        entity_type: str,
        additional_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generic entity transformation based on mapping configuration

        Args:
            sf_data: Raw data from SuccessFactors
            entity_type: SF entity type (e.g., "FOBusinessUnit", "User", "Position")
            additional_context: Additional context for lookups

        Returns:
            Transformed data ready for OrgChartAI
        """
        if entity_type not in self.mappings:
            logger.warning(f"No mapping found for entity type: {entity_type}")
            return {}

        mapping_config = self.mappings[entity_type]
        field_mappings = mapping_config["fields"]
        target_entity_type = mapping_config.get("entity_type")

        transformed = {
            "hris_source": "successfactors",
            "hris_entity_type": entity_type,
        }

        # Add type if specified in mapping
        if "type" in mapping_config:
            transformed["type"] = mapping_config["type"]

        # Transform each field
        for sf_field, orgchart_field in field_mappings.items():
            if sf_field in sf_data and sf_data[sf_field] is not None:
                value = sf_data[sf_field]

                # Apply transformations
                if sf_field == "status":
                    value = self._transform_status(value)
                elif sf_field.endswith("Date"):
                    value = self._transform_date(value)
                elif sf_field.endswith("DateTime"):
                    value = self._transform_datetime(value)

                transformed[orgchart_field] = value

        # Add HRIS ID (for tracking original source)
        if "externalCode" in sf_data:
            transformed["hris_id"] = sf_data["externalCode"]
        elif "userId" in sf_data:
            transformed["hris_id"] = sf_data["userId"]
        elif "code" in sf_data:
            transformed["hris_id"] = sf_data["code"]

        return transformed

    # ============================================
    # Specific Entity Transformations
    # ============================================

    def transform_fo_business_unit(self, sf_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform FOBusinessUnit to org_unit"""
        transformed = self.transform_entity(sf_data, "FOBusinessUnit")

        # Get name from either name_defaultValue or name_en_US
        if "name" not in transformed or not transformed["name"]:
            if "name_en_US" in sf_data:
                transformed["name"] = sf_data["name_en_US"]
            elif "name_defaultValue" in sf_data:
                transformed["name"] = sf_data["name_defaultValue"]

        # Store parent reference for later resolution
        if "parent" in sf_data and sf_data["parent"]:
            transformed["parent_hris_id"] = sf_data["parent"]

        # Set default status if not present
        if "status" not in transformed:
            transformed["status"] = "Active"

        return transformed

    def transform_fo_department(self, sf_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform FODepartment to org_unit"""
        transformed = self.transform_entity(sf_data, "FODepartment")

        # Get name
        if "name" not in transformed or not transformed["name"]:
            if "name_en_US" in sf_data:
                transformed["name"] = sf_data["name_en_US"]
            elif "name_defaultValue" in sf_data:
                transformed["name"] = sf_data["name_defaultValue"]

        # Parent hierarchy (priority: parent > businessUnit > division)
        if "parent" in sf_data and sf_data["parent"]:
            transformed["parent_hris_id"] = sf_data["parent"]
        elif "businessUnit" in sf_data and sf_data["businessUnit"]:
            transformed["parent_hris_id"] = sf_data["businessUnit"]
            transformed["parent_type"] = "BusinessUnit"
        elif "division" in sf_data and sf_data["division"]:
            transformed["parent_hris_id"] = sf_data["division"]
            transformed["parent_type"] = "Division"

        if "status" not in transformed:
            transformed["status"] = "Active"

        return transformed

    def transform_fo_division(self, sf_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform FODivision to org_unit"""
        transformed = self.transform_entity(sf_data, "FODivision")

        if "name" not in transformed or not transformed["name"]:
            if "name_en_US" in sf_data:
                transformed["name"] = sf_data["name_en_US"]
            elif "name_defaultValue" in sf_data:
                transformed["name"] = sf_data["name_defaultValue"]

        if "parent" in sf_data and sf_data["parent"]:
            transformed["parent_hris_id"] = sf_data["parent"]

        if "status" not in transformed:
            transformed["status"] = "Active"

        return transformed

    def transform_user(self, sf_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform User to employee"""
        transformed = self.transform_entity(sf_data, "User")

        # Determine employee number (priority: custom01 > empId > userId)
        if "custom01" in sf_data and sf_data["custom01"]:
            transformed["employee_number"] = sf_data["custom01"]
        elif "empId" in sf_data and sf_data["empId"]:
            transformed["employee_number"] = sf_data["empId"]
        elif "userId" in sf_data:
            transformed["employee_number"] = sf_data["userId"]

        # Build full name for display
        name_parts = []
        if "firstName" in sf_data and sf_data["firstName"]:
            name_parts.append(sf_data["firstName"])
        if "middleName" in sf_data and sf_data["middleName"]:
            name_parts.append(sf_data["middleName"])
        if "lastName" in sf_data and sf_data["lastName"]:
            name_parts.append(sf_data["lastName"])

        if name_parts:
            transformed["display_name"] = " ".join(name_parts)

        # Store department reference for later org unit lookup
        if "department" in sf_data and sf_data["department"]:
            transformed["department_hris_id"] = sf_data["department"]

        # Store manager reference for later lookup
        if "manager" in sf_data and sf_data["manager"]:
            transformed["manager_hris_id"] = sf_data["manager"]

        # Default employment type
        if "employment_type" not in transformed:
            transformed["employment_type"] = "Permanent"

        # Transform status (SuccessFactors uses "t"/"f")
        if "status" in transformed:
            if transformed["status"] in ["t", "T", "true", "True"]:
                transformed["status"] = "Active"
            elif transformed["status"] in ["f", "F", "false", "False"]:
                transformed["status"] = "Terminated"

        return transformed

    def transform_position(self, sf_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform Position to position"""
        transformed = self.transform_entity(sf_data, "Position")

        # Get position title from either externalName_defaultValue or externalName_en_US
        if "position_title" not in transformed or not transformed["position_title"]:
            if "externalName_en_US" in sf_data:
                transformed["position_title"] = sf_data["externalName_en_US"]
            elif "externalName_defaultValue" in sf_data:
                transformed["position_title"] = sf_data["externalName_defaultValue"]

        # Store references for later lookup
        if "department" in sf_data and sf_data["department"]:
            transformed["department_hris_id"] = sf_data["department"]

        if "parentPosition" in sf_data and sf_data["parentPosition"]:
            transformed["parent_position_hris_id"] = sf_data["parentPosition"]

        if "incumbent" in sf_data and sf_data["incumbent"]:
            transformed["incumbent_hris_id"] = sf_data["incumbent"]

        # Default FTE
        if "fte" not in transformed:
            transformed["fte"] = 1.0

        # Default status
        if "status" not in transformed:
            # Check if incumbent exists
            if "incumbent" in sf_data and sf_data["incumbent"]:
                transformed["status"] = "Active"
            else:
                transformed["status"] = "Vacant"

        return transformed

    def transform_emp_job(self, sf_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform EmpJob to assignment"""
        transformed = self.transform_entity(sf_data, "EmpJob")

        # Store references for later lookup
        if "userId" in sf_data:
            transformed["employee_hris_id"] = sf_data["userId"]

        if "position" in sf_data and sf_data["position"]:
            transformed["position_hris_id"] = sf_data["position"]

        if "department" in sf_data and sf_data["department"]:
            transformed["department_hris_id"] = sf_data["department"]

        if "managerId" in sf_data and sf_data["managerId"]:
            transformed["manager_hris_id"] = sf_data["managerId"]

        # Determine assignment type
        if "isPrimary" in sf_data and sf_data.get("isPrimary"):
            transformed["assignment_type"] = "Primary"
        else:
            transformed["assignment_type"] = "Secondary"

        # FTE from standardHours (assuming 40 hour week)
        if "standardHours" in sf_data and sf_data["standardHours"]:
            transformed["fte"] = sf_data["standardHours"] / 40.0

        return transformed

    # ============================================
    # Batch Transformations
    # ============================================

    def transform_org_units(
        self,
        sf_data_list: List[Dict[str, Any]],
        entity_type: str = "FOBusinessUnit"
    ) -> List[Dict[str, Any]]:
        """Transform list of org units"""
        transformed_list = []

        for sf_data in sf_data_list:
            try:
                if entity_type == "FOBusinessUnit":
                    transformed = self.transform_fo_business_unit(sf_data)
                elif entity_type == "FODepartment":
                    transformed = self.transform_fo_department(sf_data)
                elif entity_type == "FODivision":
                    transformed = self.transform_fo_division(sf_data)
                else:
                    logger.warning(f"Unknown org unit entity type: {entity_type}")
                    continue

                transformed_list.append(transformed)

                # Cache for lookups
                if "code" in transformed and "id" in transformed:
                    self.lookup_cache["org_units"][transformed["code"]] = transformed["id"]

            except Exception as e:
                logger.error(f"Error transforming org unit: {e}")
                logger.error(f"SF Data: {sf_data}")
                continue

        return transformed_list

    def transform_employees(self, sf_data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform list of users/employees"""
        transformed_list = []

        for sf_data in sf_data_list:
            try:
                transformed = self.transform_user(sf_data)
                transformed_list.append(transformed)

                # Cache for lookups
                if "employee_number" in transformed and "id" in transformed:
                    self.lookup_cache["employees"][transformed["employee_number"]] = transformed["id"]

            except Exception as e:
                logger.error(f"Error transforming employee: {e}")
                logger.error(f"SF Data: {sf_data}")
                continue

        return transformed_list

    def transform_positions(self, sf_data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform list of positions"""
        transformed_list = []

        for sf_data in sf_data_list:
            try:
                transformed = self.transform_position(sf_data)
                transformed_list.append(transformed)

                # Cache for lookups
                if "position_code" in transformed and "id" in transformed:
                    self.lookup_cache["positions"][transformed["position_code"]] = transformed["id"]

            except Exception as e:
                logger.error(f"Error transforming position: {e}")
                logger.error(f"SF Data: {sf_data}")
                continue

        return transformed_list

    # ============================================
    # Helper Methods
    # ============================================

    def _transform_status(self, status: Any) -> str:
        """Transform status codes to standard values"""
        if isinstance(status, bool):
            return "Active" if status else "Inactive"

        status_str = str(status).strip()
        return STATUS_MAPPINGS.get(status_str, status_str)

    def _transform_date(self, date_value: Any) -> Optional[date]:
        """Transform date value to date object"""
        if isinstance(date_value, date):
            return date_value
        if isinstance(date_value, datetime):
            return date_value.date()
        if isinstance(date_value, str):
            try:
                # Try ISO format
                return datetime.fromisoformat(date_value.replace('Z', '+00:00')).date()
            except:
                try:
                    # Try common date formats
                    return datetime.strptime(date_value, "%Y-%m-%d").date()
                except:
                    logger.warning(f"Could not parse date: {date_value}")
                    return None
        return None

    def _transform_datetime(self, datetime_value: Any) -> Optional[datetime]:
        """Transform datetime value to datetime object"""
        if isinstance(datetime_value, datetime):
            return datetime_value
        if isinstance(datetime_value, str):
            try:
                # Try ISO format
                return datetime.fromisoformat(datetime_value.replace('Z', '+00:00'))
            except:
                try:
                    # Try common datetime formats
                    return datetime.strptime(datetime_value, "%Y-%m-%dT%H:%M:%S")
                except:
                    logger.warning(f"Could not parse datetime: {datetime_value}")
                    return None
        return None

    def extract_odata_results(self, odata_response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract results array from OData response"""
        # SuccessFactors OData response format: {"d": {"results": [...]}}
        if "d" in odata_response:
            d_value = odata_response["d"]
            if "results" in d_value:
                return d_value["results"]
            elif isinstance(d_value, list):
                return d_value
            elif isinstance(d_value, dict):
                # Single entity response
                return [d_value]
        elif "results" in odata_response:
            return odata_response["results"]
        elif isinstance(odata_response, list):
            return odata_response
        else:
            logger.warning(f"Unexpected OData response format: {list(odata_response.keys())}")
            return []

    def resolve_references(self, transformed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve HRIS IDs to internal IDs using lookup cache"""
        resolved = transformed_data.copy()

        # Resolve parent org unit
        if "parent_hris_id" in resolved:
            parent_hris_id = resolved["parent_hris_id"]
            if parent_hris_id in self.lookup_cache["org_units"]:
                resolved["parent_org_unit_id"] = self.lookup_cache["org_units"][parent_hris_id]

        # Resolve department to org unit
        if "department_hris_id" in resolved:
            dept_hris_id = resolved["department_hris_id"]
            if dept_hris_id in self.lookup_cache["org_units"]:
                resolved["org_unit_id"] = self.lookup_cache["org_units"][dept_hris_id]

        # Resolve manager
        if "manager_hris_id" in resolved:
            manager_hris_id = resolved["manager_hris_id"]
            if manager_hris_id in self.lookup_cache["employees"]:
                resolved["manager_id"] = self.lookup_cache["employees"][manager_hris_id]

        # Resolve position
        if "position_hris_id" in resolved:
            position_hris_id = resolved["position_hris_id"]
            if position_hris_id in self.lookup_cache["positions"]:
                resolved["position_id"] = self.lookup_cache["positions"][position_hris_id]

        # Resolve parent position
        if "parent_position_hris_id" in resolved:
            parent_position_hris_id = resolved["parent_position_hris_id"]
            if parent_position_hris_id in self.lookup_cache["positions"]:
                resolved["reports_to_position_id"] = self.lookup_cache["positions"][parent_position_hris_id]

        return resolved
