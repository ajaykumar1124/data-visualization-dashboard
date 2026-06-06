"""
API Routes for Data Analytics Dashboard
Organized route handlers with authentication and validation
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks, Query
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import pandas as pd
import numpy as np
import json
import io
import os
from datetime import datetime, timedelta

# Import dependencies
from database import get_db, DatasetRepository, VisualizationRepository
from auth import (
    get_current_active_user, get_admin_user, get_analyst_user,
    PermissionChecker, check_rate_limit
)
from models import (
    User, Dataset, Visualization, ExportJob,
    DatasetResponse, VisualizationCreate, VisualizationResponse,
    ExportJobCreate, ExportJobResponse
)

# Import processing modules
import sys
sys.path.append('..')
from data_pipeline import DataCleaningPipeline
from visualization_engine import VisualizationEngine
from sample_data_generator import SampleDataGenerator

# Initialize processing engines
pipeline = DataCleaningPipeline()
viz_engine = VisualizationEngine()
data_generator = SampleDataGenerator()

# Create routers
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])
data_router = APIRouter(prefix="/data", tags=["Data Management"])
viz_router = APIRouter(prefix="/visualizations", tags=["Visualizations"])
export_router = APIRouter(prefix="/export", tags=["Export"])
admin_router = APIRouter(prefix="/admin", tags=["Administration"])

# Authentication Routes
@auth_router.post("/login")
async def login(
    username: str,
    password: str,
    db: Session = Depends(get_db)
):
    """User login endpoint"""
    from auth import verify_password, create_access_token, create_refresh_token
    
    # Find user
    user = db.query(User).filter(User.username == username).first()
    
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=400,
            detail="Inactive user account"
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
    }

@auth_router.post("/register")
async def register(
    username: str,
    email: str,
    password: str,
    full_name: Optional[str] = None,
    organization: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """User registration endpoint"""
    from auth import get_password_hash
    
    # Check if user exists
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )
    
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(password)
    user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        full_name=full_name,
        organization=organization,
        role="user",
        is_active=True
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {
        "message": "User registered successfully",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
    }

@auth_router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "organization": current_user.organization,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
        "last_login": current_user.last_login
    }

# Data Management Routes
@data_router.post("/upload", response_model=DatasetResponse)
async def upload_dataset(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    _: None = Depends(check_rate_limit)
):
    """Upload and store dataset"""
    
    # Check permissions
    if not PermissionChecker.can_upload_data(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Validate file
    max_size = 200 * 1024 * 1024  # 200MB
    file_content = await file.read()
    
    if len(file_content) > max_size:
        raise HTTPException(status_code=413, detail="File too large")
    
    allowed_extensions = ['.csv', '.xlsx', '.xls']
    if not any(file.filename.endswith(ext) for ext in allowed_extensions):
        raise HTTPException(status_code=400, detail="Unsupported file format")
    
    try:
        # Read file
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(file_content))
        else:
            df = pd.read_excel(io.BytesIO(file_content))
        
        # Save file to disk
        os.makedirs("uploads", exist_ok=True)
        file_path = f"uploads/{current_user.id}_{file.filename}"
        
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # Create dataset record
        dataset = Dataset(
            filename=file.filename,
            original_filename=file.filename,
            file_size=len(file_content),
            file_type=file.filename.split('.')[-1],
            rows_count=len(df),
            columns_count=len(df.columns),
            column_names=df.columns.tolist(),
            data_types=df.dtypes.astype(str).to_dict(),
            user_id=current_user.id,
            file_path=file_path
        )
        
        db.add(dataset)
        db.commit()
        db.refresh(dataset)
        
        return dataset
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@data_router.post("/process/{dataset_id}")
async def process_dataset(
    dataset_id: str,
    processing_config: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Process dataset through cleaning pipeline"""
    
    # Get dataset
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Check permissions
    if not PermissionChecker.can_access_dataset(current_user, dataset.user_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    try:
        # Load data
        if dataset.file_type == 'csv':
            df = pd.read_csv(dataset.file_path)
        else:
            df = pd.read_excel(dataset.file_path)
        
        # Process data
        cleaned_df = pipeline.clean_dataset(df, processing_config)
        cleaning_report = pipeline.get_cleaning_report()
        
        # Save processed data
        processed_file_path = f"uploads/processed_{dataset.id}.csv"
        cleaned_df.to_csv(processed_file_path, index=False)
        
        # Update dataset record
        dataset.is_processed = True
        dataset.processing_config = processing_config or {}
        dataset.cleaning_report = cleaning_report
        dataset.processed_at = datetime.utcnow()
        dataset.processed_file_path = processed_file_path
        dataset.rows_count = len(cleaned_df)
        dataset.columns_count = len(cleaned_df.columns)
        
        db.commit()
        
        return {
            "success": True,
            "message": "Dataset processed successfully",
            "cleaning_report": cleaning_report,
            "original_rows": len(df),
            "processed_rows": len(cleaned_df)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@data_router.get("/datasets", response_model=List[DatasetResponse])
async def list_datasets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List user's datasets"""
    
    repo = DatasetRepository(db)
    
    if current_user.role == "admin":
        datasets = repo.get_all(skip, limit)
    else:
        datasets = repo.get_by_user(current_user.id, skip, limit)
    
    return datasets

@data_router.get("/datasets/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(
    dataset_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get dataset information"""
    
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Check permissions
    if not PermissionChecker.can_access_dataset(current_user, dataset.user_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return dataset

@data_router.get("/datasets/{dataset_id}/preview")
async def get_dataset_preview(
    dataset_id: str,
    rows: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get dataset preview"""
    
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Check permissions
    if not PermissionChecker.can_access_dataset(current_user, dataset.user_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    try:
        # Load data
        file_path = dataset.processed_file_path if dataset.is_processed else dataset.file_path
        
        if dataset.file_type == 'csv' or dataset.is_processed:
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        
        # Get preview
        preview = df.head(rows).to_dict('records')
        
        # Get summary statistics
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        summary_stats = {}
        if len(numeric_cols) > 0:
            summary_stats = df[numeric_cols].describe().to_dict()
        
        return {
            "preview": preview,
            "summary_stats": summary_stats,
            "total_rows": len(df),
            "columns": df.columns.tolist(),
            "data_types": df.dtypes.astype(str).to_dict()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Preview failed: {str(e)}")

@data_router.delete("/datasets/{dataset_id}")
async def delete_dataset(
    dataset_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete dataset"""
    
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Check permissions
    if not PermissionChecker.can_delete_dataset(current_user, dataset.user_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    try:
        # Delete files
        if os.path.exists(dataset.file_path):
            os.remove(dataset.file_path)
        
        if dataset.processed_file_path and os.path.exists(dataset.processed_file_path):
            os.remove(dataset.processed_file_path)
        
        # Delete database record
        db.delete(dataset)
        db.commit()
        
        return {"message": "Dataset deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")

# Visualization Routes
@viz_router.post("/create/{dataset_id}", response_model=VisualizationResponse)
async def create_visualization(
    dataset_id: str,
    viz_request: VisualizationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create visualization for dataset"""
    
    # Get dataset
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Check permissions
    if not PermissionChecker.can_access_dataset(current_user, dataset.user_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    try:
        # Load data
        file_path = dataset.processed_file_path if dataset.is_processed else dataset.file_path
        
        if dataset.file_type == 'csv' or dataset.is_processed:
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        
        # Create visualization
        viz_params = viz_request.config
        
        if viz_request.viz_type == 'trend':
            fig = viz_engine.create_trend_analysis(
                df, 
                viz_params.get('x_column'), 
                viz_params.get('y_column'),
                viz_request.title
            )
        elif viz_request.viz_type == 'distribution':
            fig = viz_engine.create_distribution_analysis(
                df,
                viz_params.get('column'),
                viz_request.title
            )
        elif viz_request.viz_type == 'categorical':
            fig = viz_engine.create_categorical_comparison(
                df,
                viz_params.get('category_column'),
                viz_params.get('value_column'),
                viz_request.title
            )
        elif viz_request.viz_type == 'correlation':
            fig = viz_engine.create_correlation_heatmap(df, viz_request.title)
        elif viz_request.viz_type == 'dashboard':
            fig = viz_engine.create_performance_dashboard(df, viz_request.title)
        elif viz_request.viz_type == 'comparative':
            fig = viz_engine.create_comparative_analysis(
                df,
                viz_params.get('group_column'),
                viz_params.get('value_columns', []),
                viz_request.title
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid visualization type")
        
        # Convert to JSON
        chart_data = json.loads(fig.to_json())
        
        # Save visualization
        visualization = Visualization(
            dataset_id=dataset_id,
            viz_type=viz_request.viz_type,
            title=viz_request.title,
            description=viz_request.description,
            config=viz_request.config,
            chart_data=chart_data,
            user_id=current_user.id
        )
        
        db.add(visualization)
        db.commit()
        db.refresh(visualization)
        
        return visualization
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Visualization creation failed: {str(e)}")

@viz_router.get("/dataset/{dataset_id}", response_model=List[VisualizationResponse])
async def list_visualizations(
    dataset_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List visualizations for dataset"""
    
    # Check dataset access
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    if not PermissionChecker.can_access_dataset(current_user, dataset.user_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    repo = VisualizationRepository(db)
    visualizations = repo.get_by_dataset(dataset_id)
    
    return visualizations

@viz_router.get("/{viz_id}", response_model=VisualizationResponse)
async def get_visualization(
    viz_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific visualization"""
    
    visualization = db.query(Visualization).filter(Visualization.id == viz_id).first()
    if not visualization:
        raise HTTPException(status_code=404, detail="Visualization not found")
    
    # Check dataset access
    dataset = db.query(Dataset).filter(Dataset.id == visualization.dataset_id).first()
    if not PermissionChecker.can_access_dataset(current_user, dataset.user_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return visualization

# Export Routes
@export_router.post("/create/{dataset_id}", response_model=ExportJobResponse)
async def create_export_job(
    dataset_id: str,
    export_request: ExportJobCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create export job for dataset"""
    
    # Get dataset
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Check permissions
    if not PermissionChecker.can_access_dataset(current_user, dataset.user_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Create export job
    export_job = ExportJob(
        dataset_id=dataset_id,
        export_format=export_request.export_format,
        export_config=export_request.export_config,
        user_id=current_user.id
    )
    
    db.add(export_job)
    db.commit()
    db.refresh(export_job)
    
    # Add background task
    background_tasks.add_task(process_export_job, export_job.id, db)
    
    return export_job

async def process_export_job(job_id: str, db: Session):
    """Background task to process export job"""
    # Implementation for background export processing
    pass

# Admin Routes
@admin_router.get("/users")
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """List all users (admin only)"""
    
    users = db.query(User).offset(skip).limit(limit).all()
    return [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "last_login": user.last_login
        }
        for user in users
    ]

@admin_router.get("/stats")
async def get_system_stats(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get system statistics (admin only)"""
    
    total_users = db.query(User).count()
    total_datasets = db.query(Dataset).count()
    total_visualizations = db.query(Visualization).count()
    processed_datasets = db.query(Dataset).filter(Dataset.is_processed == True).count()
    
    return {
        "total_users": total_users,
        "total_datasets": total_datasets,
        "total_visualizations": total_visualizations,
        "processed_datasets": processed_datasets,
        "processing_rate": processed_datasets / total_datasets if total_datasets > 0 else 0
    }