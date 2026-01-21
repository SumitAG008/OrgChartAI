"""
SQLAlchemy database models
"""

from sqlalchemy import Column, String, Integer, Boolean, Date, DECIMAL, ForeignKey, Text, JSON, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid

class OrgUnit(Base):
    __tablename__ = "org_unit"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    parent_org_unit_id = Column(UUID(as_uuid=True), ForeignKey("org_unit.id"))
    type = Column(String, nullable=False)
    cost_center_id = Column(UUID(as_uuid=True), ForeignKey("cost_center.id"))
    location_id = Column(UUID(as_uuid=True), ForeignKey("location.id"))
    legal_entity_id = Column(UUID(as_uuid=True), ForeignKey("legal_entity.id"))
    scope = Column(String)
    tree_id = Column(String)
    effective_start_date = Column(Date, nullable=False)
    effective_end_date = Column(Date)
    status = Column(String, nullable=False, default="Active")
    
    # Relationships
    parent = relationship("OrgUnit", remote_side=[id], backref="children")
    positions = relationship("Position", back_populates="org_unit")

class Position(Base):
    __tablename__ = "position"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_unit_id = Column(UUID(as_uuid=True), ForeignKey("org_unit.id"), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey("job.id"))
    position_code = Column(String, unique=True, nullable=False)
    position_title = Column(String, nullable=False)
    position_type = Column(String, nullable=False)
    reports_to_position_id = Column(UUID(as_uuid=True), ForeignKey("position.id"))
    fte = Column(DECIMAL(3, 2), default=1.0)
    grade = Column(String)
    level = Column(Integer)
    is_managerial = Column(Boolean, default=False)
    is_mass_position_template = Column(Boolean, default=False)
    status = Column(String, nullable=False, default="Active")
    effective_start_date = Column(Date, nullable=False)
    effective_end_date = Column(Date)
    
    # Relationships
    org_unit = relationship("OrgUnit", back_populates="positions")
    job = relationship("Job", back_populates="positions")
    reports_to = relationship("Position", remote_side=[id], backref="direct_reports")
    employees = relationship("Employee", back_populates="primary_position")
    accountability_assignments = relationship("AccountabilityAssignment", back_populates="position")

class Job(Base):
    __tablename__ = "job"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_code = Column(String, unique=True, nullable=False)
    job_title = Column(String, nullable=False)
    job_family = Column(String)
    job_sub_family = Column(String)
    default_grade = Column(String)
    default_position_type = Column(String)
    description = Column(Text)
    
    # Relationships
    positions = relationship("Position", back_populates="job")

class Employee(Base):
    __tablename__ = "employee"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_number = Column(String, unique=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    preferred_name = Column(String)
    email = Column(String, unique=True, nullable=False)
    photo_url = Column(String)
    employment_type = Column(String, nullable=False)
    legal_entity_id = Column(UUID(as_uuid=True), ForeignKey("legal_entity.id"))
    primary_position_id = Column(UUID(as_uuid=True), ForeignKey("position.id"))
    hire_date = Column(Date, nullable=False)
    termination_date = Column(Date)
    status = Column(String, nullable=False, default="Active")
    
    # Relationships
    primary_position = relationship("Position", back_populates="employees")
    accountability_assignments = relationship("AccountabilityAssignment", back_populates="employee")

# Functional Chart Models

class FunctionCategory(Base):
    __tablename__ = "function_category"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    icon = Column(String)  # Emoji or icon identifier
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), nullable=False)
    updated_by = Column(UUID(as_uuid=True))
    version = Column(Integer, nullable=False, default=1)
    
    # Relationships
    functions = relationship("Function", back_populates="category", cascade="all, delete-orphan")

class Function(Base):
    __tablename__ = "function"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id = Column(UUID(as_uuid=True), ForeignKey("function_category.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    icon = Column(String)  # Emoji or icon identifier
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), nullable=False)
    updated_by = Column(UUID(as_uuid=True))
    version = Column(Integer, nullable=False, default=1)
    
    # Relationships
    category = relationship("FunctionCategory", back_populates="functions")
    accountabilities = relationship("Accountability", back_populates="function", cascade="all, delete-orphan")

class Accountability(Base):
    __tablename__ = "accountability"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    function_id = Column(UUID(as_uuid=True), ForeignKey("function.id", ondelete="CASCADE"), nullable=False)
    accountability_code = Column(String)  # Optional accountability ID
    objective = Column(Text, nullable=False)  # The accountability description/objective
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), nullable=False)
    updated_by = Column(UUID(as_uuid=True))
    version = Column(Integer, nullable=False, default=1)
    
    # Relationships
    function = relationship("Function", back_populates="accountabilities")
    assignments = relationship("AccountabilityAssignment", back_populates="accountability", cascade="all, delete-orphan")

class AccountabilityAssignment(Base):
    __tablename__ = "accountability_assignment"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    accountability_id = Column(UUID(as_uuid=True), ForeignKey("accountability.id", ondelete="CASCADE"), nullable=False)
    position_id = Column(UUID(as_uuid=True), ForeignKey("position.id", ondelete="SET NULL"))
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employee.id", ondelete="SET NULL"))
    assignment_type = Column(String, nullable=False)  # Primary, Secondary, Shared
    start_date = Column(TIMESTAMP, nullable=False, server_default=func.now())
    end_date = Column(TIMESTAMP)
    status = Column(String, nullable=False, default="Active")
    notes = Column(Text)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), nullable=False)
    updated_by = Column(UUID(as_uuid=True))
    version = Column(Integer, nullable=False, default=1)
    
    # Relationships
    accountability = relationship("Accountability", back_populates="assignments")
    position = relationship("Position", back_populates="accountability_assignments")
    employee = relationship("Employee", back_populates="accountability_assignments")

# Scenario Models

class Scenario(Base):
    __tablename__ = "scenario"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text)
    tree_id = Column(String, unique=True, nullable=False)
    base_scenario_id = Column(UUID(as_uuid=True), ForeignKey("scenario.id"))
    status = Column(String, nullable=False, default="Draft")  # Draft, Active, Archived
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True))
    
    # Relationships
    base_scenario = relationship("Scenario", remote_side=[id], backref="variants")
