"""
Apache Arrow Service for High-Performance Data Transfer

Benefits:
- 10-100x faster serialization than JSON for large datasets
- Zero-copy reads (no memory duplication)
- Native datetime/timestamp support (fixes serialization issues)
- Cross-language compatibility (Python, JS, Java, etc.)
"""

import pyarrow as pa
import pyarrow.ipc as ipc
from typing import List, Dict, Any, Optional
from datetime import datetime
import io
import logging
import json

logger = logging.getLogger(__name__)


class ArrowService:
    """Convert HRIS data to/from Apache Arrow format"""

    # Schema definitions for each entity type
    SCHEMAS = {
        "position": pa.schema([
            ("hris_id", pa.string()),
            ("code", pa.string()),
            ("title", pa.string()),
            ("job_code", pa.string()),
            ("org_unit_id", pa.string()),
            ("status", pa.string()),
            ("hris_source", pa.string()),
            ("hris_type", pa.string()),
            ("created_at", pa.timestamp("ms")),
            ("updated_at", pa.timestamp("ms")),
        ]),
        "employee": pa.schema([
            ("hris_id", pa.string()),
            ("employee_number", pa.string()),
            ("first_name", pa.string()),
            ("last_name", pa.string()),
            ("email", pa.string()),
            ("status", pa.string()),
            ("position_id", pa.string()),
            ("department_id", pa.string()),
            ("hris_source", pa.string()),
            ("hris_type", pa.string()),
            ("hire_date", pa.timestamp("ms")),
            ("created_at", pa.timestamp("ms")),
        ]),
        "org_unit": pa.schema([
            ("hris_id", pa.string()),
            ("code", pa.string()),
            ("name", pa.string()),
            ("org_type", pa.string()),
            ("parent_id", pa.string()),
            ("status", pa.string()),
            ("hris_source", pa.string()),
            ("hris_type", pa.string()),
            ("created_at", pa.timestamp("ms")),
        ]),
    }

    @classmethod
    def records_to_arrow(
        cls,
        records: List[Dict[str, Any]],
        entity_type: str
    ) -> pa.Table:
        """
        Convert list of dicts to Arrow Table

        ~10-100x faster than JSON for large datasets
        """
        if not records:
            schema = cls.SCHEMAS.get(entity_type)
            if schema:
                return pa.Table.from_pydict({}, schema=schema)
            return pa.table({})

        # Normalize records to match schema
        schema = cls.SCHEMAS.get(entity_type)
        if schema:
            normalized = []
            for record in records:
                norm_record = {}
                for field in schema:
                    value = record.get(field.name)
                    # Convert datetime strings to datetime objects
                    if pa.types.is_timestamp(field.type) and isinstance(value, str):
                        try:
                            value = datetime.fromisoformat(value.replace("Z", "+00:00"))
                        except (ValueError, AttributeError):
                            value = None
                    norm_record[field.name] = value
                normalized.append(norm_record)
            records = normalized

        # Convert to Arrow table
        try:
            table = pa.Table.from_pylist(records, schema=schema)
            logger.info(f"Created Arrow table: {len(records)} rows, {table.nbytes} bytes")
            return table
        except Exception as e:
            logger.warning(f"Schema conversion failed, using inference: {e}")
            return pa.Table.from_pylist(records)

    @classmethod
    def arrow_to_records(cls, table: pa.Table) -> List[Dict[str, Any]]:
        """Convert Arrow Table back to list of dicts"""
        return table.to_pylist()

    @classmethod
    def table_to_ipc_bytes(cls, table: pa.Table) -> bytes:
        """
        Serialize Arrow Table to IPC format (for network transfer)

        This is the format that can be read by Arrow libraries in any language
        """
        sink = io.BytesIO()
        with ipc.RecordBatchFileWriter(sink, table.schema) as writer:
            writer.write_table(table)
        return sink.getvalue()

    @classmethod
    def ipc_bytes_to_table(cls, data: bytes) -> pa.Table:
        """Deserialize IPC bytes back to Arrow Table"""
        reader = ipc.open_file(io.BytesIO(data))
        return reader.read_all()

    @classmethod
    def table_to_json(cls, table: pa.Table) -> str:
        """Convert Arrow Table to JSON (for UI compatibility)"""
        records = table.to_pylist()
        # Handle datetime serialization
        def serialize(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return obj

        return json.dumps(records, default=serialize)

    @classmethod
    def get_table_stats(cls, table: pa.Table) -> Dict[str, Any]:
        """Get statistics about an Arrow table"""
        return {
            "num_rows": table.num_rows,
            "num_columns": table.num_columns,
            "column_names": table.column_names,
            "memory_bytes": table.nbytes,
            "memory_mb": round(table.nbytes / (1024 * 1024), 3),
            "schema": str(table.schema),
        }


class ArrowDataStore:
    """
    In-memory Arrow data store for fast access

    Stores data as Arrow tables for:
    - Zero-copy access
    - Efficient filtering/querying
    - Fast serialization
    """

    def __init__(self):
        self._tables: Dict[str, pa.Table] = {}

    def store(self, key: str, records: List[Dict], entity_type: str) -> Dict[str, Any]:
        """Store records as Arrow table"""
        table = ArrowService.records_to_arrow(records, entity_type)
        self._tables[key] = table
        return ArrowService.get_table_stats(table)

    def get(self, key: str) -> Optional[pa.Table]:
        """Get Arrow table by key"""
        return self._tables.get(key)

    def get_as_records(self, key: str) -> List[Dict[str, Any]]:
        """Get data as list of dicts"""
        table = self._tables.get(key)
        if table is None:
            return []
        return ArrowService.arrow_to_records(table)

    def get_as_ipc(self, key: str) -> Optional[bytes]:
        """Get data as IPC bytes (for Arrow-compatible clients)"""
        table = self._tables.get(key)
        if table is None:
            return None
        return ArrowService.table_to_ipc_bytes(table)

    def filter(self, key: str, column: str, value: Any) -> List[Dict[str, Any]]:
        """Filter data using Arrow's efficient filtering"""
        table = self._tables.get(key)
        if table is None:
            return []

        # Use Arrow's compute functions for fast filtering
        import pyarrow.compute as pc
        mask = pc.equal(table.column(column), value)
        filtered = table.filter(mask)
        return ArrowService.arrow_to_records(filtered)

    def keys(self) -> List[str]:
        """List all stored keys"""
        return list(self._tables.keys())

    def stats(self) -> Dict[str, Any]:
        """Get stats for all stored tables"""
        total_bytes = sum(t.nbytes for t in self._tables.values())
        return {
            "num_tables": len(self._tables),
            "total_memory_mb": round(total_bytes / (1024 * 1024), 3),
            "tables": {
                key: ArrowService.get_table_stats(table)
                for key, table in self._tables.items()
            }
        }


# Global Arrow data store
arrow_store = ArrowDataStore()
