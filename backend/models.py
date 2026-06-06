"""
Database Models for Data Analytics Dashboard API
SQLAlchemy models for persistent storage
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, JSON, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, Dict, Any
import uuid

Base = declarative_base()

class Dataset(Base):
    """Dataset model for storing uploaded data information"""
    
    __tablename__ = "datasets"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String, nullable=False)
    
    # Data information
    rows_count = Column(Integer, nullable=False)
    columns_count = Column(Integer, nullable=False)
    column_names = Column(JSON, nullable=False)
    data_types = Column(JSON, nullable=False)
    
    # Processing status
    is_processed = Column(Boolean, default=False)
    processing_config = Column(JSON, nullable=True)
    cleaning_report = Column(JSON, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    processed_at = Column(DateTime, nullable=True)
    
    # User information (for multi-user support)
    user_id = Column(String, nullable=True)
    
    # File storage path
    file_path = Column(String, nullable=False)
    processed_file_path = Column(String, nullable=True)

class Visualization(Base):
    """Visualization model for storing chart configurations and results"""
    
    __tablename__ = "visualizations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id = Column(String, nullable=False)  # Foreign key to Dataset
    
    # Visualization configuration
    viz_type = Column(String, nullable=False)  # trend, distribution, categorical, etc.
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    config = Column(JSON, nullable=False)  # Visualization parameters
    
    # Chart data (stored as JSON)
    chart_data = Column(JSON, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # User information
    user_id = Column(String, nullable=True)

class ExportJob(Base):
    """Export job model for tracking data exports"""
    
    __tablename__ = "export_jobs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id = Column(String, nullable=False)
    
    # Export configuration
    export_format = Column(String, nullable=False)  # csv, excel, pdf
    export_config = Column(JSON, nullable=False)
    
    # Job status
    status = Column(String, default="pending")  # pending, processing, completed, failed
    progress = Column(Float, default=0.0)
    error_message = Column(Text, nullable=True)
    
    # File information
    output_filename = Column(String, nullable=True)
    output_file_path = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime, nullable=True)
    
    # User information
    user_id = Column(String, nullable=True)

class User(Base):
    """User model for authentication and authorization"""
    
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # User profile
    full_name = Column(String, nullable=True)
    organization = Column(String, nullable=True)
    role = Column(String, default="user")  # user, admin, analyst
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login = Column(DateTime, nullable=True)

class APIKey(Base):
    """API Key model for API authentication"""
    
    __tablename__ = "api_keys"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    
    # Key information
    key_name = Column(String, nullable=False)
    key_hash = Column(String, nullable=False)
    key_prefix = Column(String, nullable=False)  # First 8 chars for identification
    
    # Permissions
    permissions = Column(JSON, default=list)  # List of allowed operations
    
    # Usage tracking
    usage_count = Column(Integer, default=0)
    last_used = Column(DateTime, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class ProcessingJob(Base):
    """Processing job model for background data processing tasks"""
    
    __tablename__ = "processing_jobs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id = Column(String, nullable=False)
    
    # Job configuration
    job_type = Column(String, nullable=False)  # cleaning, analysis, visualization
    config = Column(JSON, nullable=False)
    
    # Job status
    status = Column(String, default="pending")  # pending, running, completed, failed
    progress = Column(Float, default=0.0)
    result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Timing
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # User information
    user_id = Column(String, nullable=True)

class AuditLog(Base):
    """Audit log model for tracking API usage and changes"""
    
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Action information
    action = Column(String, nullable=False)  # upload, process, visualize, export, delete
    resource_type = Column(String, nullable=False)  # dataset, visualization, user
    resource_id = Column(String, nullable=True)
    
    # Request information
    endpoint = Column(String, nullable=False)
    method = Column(String, nullable=False)
    status_code = Column(Integer, nullable=False)
    
    # User and session information
    user_id = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    
    # Additional data
    request_data = Column(JSON, nullable=True)
    response_data = Column(JSON, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())

# Pydantic models for API requests/responses

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class DatasetCreate(BaseModel):
    """Request model for dataset creation"""
    filename: str
    processing_config: Optional[Dict[str, Any]] = None

class DatasetResponse(BaseModel):
    """Response model for dataset information"""
    id: str
    filename: str
    original_filename: str
    rows_count: int
    columns_count: int
    column_names: List[str]
    data_types: Dict[str, str]
    is_processed: bool
    created_at: datetime
    file_size: int
    
    class Config:
        from_attributes = True

class VisualizationCreate(BaseModel):
    """Request model for visualization creation"""
    viz_type: str = Field(..., description="Type of visualization")
    title: str = Field(..., description="Visualization title")
    description: Optional[str] = None
    config: Dict[str, Any] = Field(..., description="Visualization parameters")

class VisualizationResponse(BaseModel):
    """Response model for visualization"""
    id: str
    dataset_id: str
    viz_type: str
    title: str
    description: Optional[str]
    config: Dict[str, Any]
    chart_data: Optional[Dict[str, Any]]
    created_at: datetime
    
    class Config:
        from_attributes = True

class ExportJobCreate(BaseModel):
    """Request model for export job creation"""
    export_format: str = Field(..., description="Export format (csv, excel, pdf)")
    export_config: Dict[str, Any] = Field(default_factory=dict)

class ExportJobResponse(BaseModel):
    """Response model for export job"""
    id: str
    dataset_id: str
    export_format: str
    status: str
    progress: float
    output_filename: Optional[str]
    file_size: Optional[int]
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    """Request model for user creation"""
    username: str
    email: str
    password: str
    full_name: Optional[str] = None
    organization: Optional[str] = None

class UserResponse(BaseModel):
    """Response model for user information"""
    id: str
    username: str
    email: str
    full_name: Optional[str]
    organization: Optional[str]
    role: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class ProcessingJobResponse(BaseModel):
    """Response model for processing job"""
    id: str
    dataset_id: str
    job_type: str
    status: str
    progress: float
    result: Optional[Dict[str, Any]]
    error_message: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True