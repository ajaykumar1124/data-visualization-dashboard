"""
FastAPI Backend Server for Data Analytics Dashboard
Provides REST API endpoints for data processing and visualization
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
import pandas as pd
import numpy as np
import json
import io
import base64
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import os
import uuid
from pathlib import Path
import logging

# Import our custom modules
import sys
sys.path.append('..')
from data_pipeline import DataCleaningPipeline
from visualization_engine import VisualizationEngine
from sample_data_generator import SampleDataGenerator
from config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Data Analytics Dashboard API",
    description="REST API for automated data processing and visualization",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Global instances
pipeline = DataCleaningPipeline()
viz_engine = VisualizationEngine()
data_generator = SampleDataGenerator()

# In-memory storage for demo (use Redis/Database in production)
data_store = {}
job_store = {}

# Create directories
os.makedirs("uploads", exist_ok=True)
os.makedirs("exports", exist_ok=True)
os.makedirs("temp", exist_ok=True)

class DataProcessor:
    """Handles data processing operations"""
    
    @staticmethod
    def process_uploaded_file(file_content: bytes, filename: str) -> Dict[str, Any]:
        """Process uploaded file and return metadata"""
        try:
            # Determine file type and read accordingly
            if filename.endswith('.csv'):
                from file_utils import FileHandler
                handler = FileHandler()
                df = handler.read_csv_robust(io.BytesIO(file_content))
            elif filename.endswith(('.xlsx', '.xls')):
                from file_utils import FileHandler
                handler = FileHandler()
                df = handler.read_excel_robust(io.BytesIO(file_content))
            else:
                raise ValueError("Unsupported file format")
            
            # Generate unique ID for this dataset
            dataset_id = str(uuid.uuid4())
            
            # Store raw data
            data_store[dataset_id] = {
                'raw_data': df,
                'filename': filename,
                'uploaded_at': datetime.now(),
                'processed': False
            }
            
            return {
                'dataset_id': dataset_id,
                'filename': filename,
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': df.columns.tolist(),
                'data_types': df.dtypes.astype(str).to_dict(),
                'memory_usage': df.memory_usage(deep=True).sum(),
                'upload_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing file {filename}: {e}")
            raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")

# API Endpoints

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Data Analytics Dashboard API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "health": "/health",
            "upload": "/api/v1/data/upload",
            "process": "/api/v1/data/process/{dataset_id}",
            "visualize": "/api/v1/visualizations/{dataset_id}",
            "export": "/api/v1/export/{dataset_id}",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "components": {
            "data_pipeline": "operational",
            "visualization_engine": "operational",
            "storage": "operational"
        }
    }

@app.post("/api/v1/data/upload")
async def upload_data(file: UploadFile = File(...)):
    """Upload and process data file"""
    try:
        # Validate file size (200MB limit)
        max_size = 200 * 1024 * 1024  # 200MB
        file_content = await file.read()
        
        if len(file_content) > max_size:
            raise HTTPException(status_code=413, detail="File too large. Maximum size is 200MB")
        
        # Validate file type
        allowed_extensions = ['.csv', '.xlsx', '.xls']
        if not any(file.filename.endswith(ext) for ext in allowed_extensions):
            raise HTTPException(status_code=400, detail="Unsupported file format. Use CSV or Excel files")
        
        # Process the file
        result = DataProcessor.process_uploaded_file(file_content, file.filename)
        
        logger.info(f"File uploaded successfully: {file.filename} ({len(file_content)} bytes)")
        
        return {
            "success": True,
            "message": "File uploaded successfully",
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/api/v1/data/process/{dataset_id}")
async def process_data(dataset_id: str, processing_config: Optional[Dict] = None):
    """Process uploaded data through cleaning pipeline"""
    try:
        if dataset_id not in data_store:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        dataset = data_store[dataset_id]
        raw_data = dataset['raw_data']
        
        # Process data through cleaning pipeline
        cleaned_data = pipeline.clean_dataset(raw_data, processing_config)
        cleaning_report = pipeline.get_cleaning_report()
        
        # Update stored data
        data_store[dataset_id].update({
            'cleaned_data': cleaned_data,
            'cleaning_report': cleaning_report,
            'processed': True,
            'processed_at': datetime.now()
        })
        
        logger.info(f"Data processed successfully: {dataset_id}")
        
        return {
            "success": True,
            "message": "Data processed successfully",
            "data": {
                "dataset_id": dataset_id,
                "original_rows": len(raw_data),
                "cleaned_rows": len(cleaned_data),
                "cleaning_report": cleaning_report,
                "processing_time": datetime.now().isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Processing error for {dataset_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.get("/api/v1/data/{dataset_id}")
async def get_dataset_info(dataset_id: str):
    """Get dataset information and preview"""
    try:
        if dataset_id not in data_store:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        dataset = data_store[dataset_id]
        data = dataset.get('cleaned_data', dataset['raw_data'])
        
        # Generate preview
        preview = data.head(10).to_dict('records')
        
        # Generate summary statistics
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        summary_stats = {}
        if len(numeric_cols) > 0:
            summary_stats = data[numeric_cols].describe().to_dict()
        
        return {
            "success": True,
            "data": {
                "dataset_id": dataset_id,
                "filename": dataset['filename'],
                "rows": len(data),
                "columns": len(data.columns),
                "column_names": data.columns.tolist(),
                "data_types": data.dtypes.astype(str).to_dict(),
                "processed": dataset.get('processed', False),
                "preview": preview,
                "summary_stats": summary_stats,
                "cleaning_report": dataset.get('cleaning_report', {}),
                "uploaded_at": dataset['uploaded_at'].isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting dataset info {dataset_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get dataset info: {str(e)}")

@app.post("/api/v1/visualizations/{dataset_id}")
async def create_visualization(dataset_id: str, viz_config: Dict[str, Any]):
    """Create visualization for dataset"""
    try:
        if dataset_id not in data_store:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        dataset = data_store[dataset_id]
        data = dataset.get('cleaned_data', dataset['raw_data'])
        
        viz_type = viz_config.get('type')
        viz_params = viz_config.get('parameters', {})
        
        # Create visualization based on type
        if viz_type == 'trend':
            fig = viz_engine.create_trend_analysis(
                data, 
                viz_params.get('x_column'), 
                viz_params.get('y_column'),
                viz_params.get('title', 'Trend Analysis')
            )
        elif viz_type == 'distribution':
            fig = viz_engine.create_distribution_analysis(
                data,
                viz_params.get('column'),
                viz_params.get('title', 'Distribution Analysis')
            )
        elif viz_type == 'categorical':
            fig = viz_engine.create_categorical_comparison(
                data,
                viz_params.get('category_column'),
                viz_params.get('value_column'),
                viz_params.get('title', 'Categorical Comparison')
            )
        elif viz_type == 'correlation':
            fig = viz_engine.create_correlation_heatmap(
                data,
                viz_params.get('title', 'Correlation Analysis')
            )
        elif viz_type == 'dashboard':
            fig = viz_engine.create_performance_dashboard(
                data,
                viz_params.get('title', 'Performance Dashboard')
            )
        elif viz_type == 'comparative':
            fig = viz_engine.create_comparative_analysis(
                data,
                viz_params.get('group_column'),
                viz_params.get('value_columns', []),
                viz_params.get('title', 'Comparative Analysis')
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid visualization type")
        
        # Convert to JSON for API response
        fig_json = fig.to_json()
        
        return {
            "success": True,
            "message": "Visualization created successfully",
            "data": {
                "visualization_type": viz_type,
                "chart_data": json.loads(fig_json),
                "created_at": datetime.now().isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Visualization error for {dataset_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Visualization failed: {str(e)}")

@app.get("/api/v1/visualizations/{dataset_id}/types")
async def get_available_visualizations(dataset_id: str):
    """Get available visualization types for dataset"""
    try:
        if dataset_id not in data_store:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        dataset = data_store[dataset_id]
        data = dataset.get('cleaned_data', dataset['raw_data'])
        
        numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = data.select_dtypes(include=['object']).columns.tolist()
        datetime_cols = data.select_dtypes(include=['datetime64']).columns.tolist()
        
        available_types = []
        
        # Trend analysis (needs numeric + time/sequential)
        if len(numeric_cols) > 0:
            available_types.append({
                "type": "trend",
                "name": "Trend Analysis",
                "description": "Time series and sequential data patterns",
                "required_columns": {"x_column": datetime_cols + ["index"], "y_column": numeric_cols}
            })
        
        # Distribution analysis (needs numeric)
        if len(numeric_cols) > 0:
            available_types.append({
                "type": "distribution",
                "name": "Distribution Analysis",
                "description": "Data spread, outliers, and statistical summaries",
                "required_columns": {"column": numeric_cols}
            })
        
        # Categorical comparison (needs categorical + numeric)
        if len(categorical_cols) > 0 and len(numeric_cols) > 0:
            available_types.append({
                "type": "categorical",
                "name": "Categorical Comparison",
                "description": "Performance across different groups",
                "required_columns": {"category_column": categorical_cols, "value_column": numeric_cols}
            })
        
        # Correlation heatmap (needs multiple numeric)
        if len(numeric_cols) > 1:
            available_types.append({
                "type": "correlation",
                "name": "Correlation Heatmap",
                "description": "Variable relationships and dependencies",
                "required_columns": {}
            })
        
        # Performance dashboard (general)
        available_types.append({
            "type": "dashboard",
            "name": "Performance Dashboard",
            "description": "Multi-metric KPI overview",
            "required_columns": {}
        })
        
        # Comparative analysis (needs categorical + multiple numeric)
        if len(categorical_cols) > 0 and len(numeric_cols) > 1:
            available_types.append({
                "type": "comparative",
                "name": "Comparative Analysis",
                "description": "Side-by-side metric comparisons",
                "required_columns": {"group_column": categorical_cols, "value_columns": numeric_cols}
            })
        
        return {
            "success": True,
            "data": {
                "dataset_id": dataset_id,
                "available_visualizations": available_types,
                "column_info": {
                    "numeric_columns": numeric_cols,
                    "categorical_columns": categorical_cols,
                    "datetime_columns": datetime_cols
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting visualization types for {dataset_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get visualization types: {str(e)}")

@app.post("/api/v1/export/{dataset_id}")
async def export_data(dataset_id: str, export_config: Dict[str, Any]):
    """Export processed data and reports"""
    try:
        if dataset_id not in data_store:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        dataset = data_store[dataset_id]
        data = dataset.get('cleaned_data', dataset['raw_data'])
        
        export_format = export_config.get('format', 'csv')
        include_report = export_config.get('include_report', False)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"export_{dataset_id[:8]}_{timestamp}"
        
        if export_format == 'csv':
            filename = f"{base_filename}.csv"
            filepath = f"exports/{filename}"
            data.to_csv(filepath, index=False)
            
        elif export_format == 'excel':
            filename = f"{base_filename}.xlsx"
            filepath = f"exports/{filename}"
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                data.to_excel(writer, sheet_name='Data', index=False)
                
                if include_report and 'cleaning_report' in dataset:
                    report_df = pd.DataFrame([dataset['cleaning_report']])
                    report_df.to_excel(writer, sheet_name='Cleaning_Report', index=False)
                
                # Add summary statistics
                numeric_data = data.select_dtypes(include=[np.number])
                if len(numeric_data.columns) > 0:
                    numeric_data.describe().to_excel(writer, sheet_name='Summary_Stats')
        
        else:
            raise HTTPException(status_code=400, detail="Unsupported export format")
        
        return {
            "success": True,
            "message": "Export completed successfully",
            "data": {
                "filename": filename,
                "format": export_format,
                "file_size": os.path.getsize(filepath),
                "download_url": f"/api/v1/download/{filename}",
                "created_at": datetime.now().isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Export error for {dataset_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@app.get("/api/v1/download/{filename}")
async def download_file(filename: str):
    """Download exported file"""
    try:
        filepath = f"exports/{filename}"
        
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            path=filepath,
            filename=filename,
            media_type='application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download error for {filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

@app.post("/api/v1/sample-data")
async def generate_sample_data(data_config: Dict[str, Any]):
    """Generate sample dataset for testing"""
    try:
        data_type = data_config.get('type', 'academic')
        n_rows = data_config.get('rows', 1000)
        
        # Generate sample data
        if data_type == 'academic':
            df = data_generator.generate_academic_dataset(n_rows)
        elif data_type == 'business':
            df = data_generator.generate_business_dataset(n_rows)
        elif data_type == 'healthcare':
            df = data_generator.generate_healthcare_dataset(n_rows)
        elif data_type == 'financial':
            df = data_generator.generate_financial_dataset(n_rows)
        else:
            raise HTTPException(status_code=400, detail="Invalid data type")
        
        # Store the generated data
        dataset_id = str(uuid.uuid4())
        data_store[dataset_id] = {
            'raw_data': df,
            'filename': f'sample_{data_type}_data.csv',
            'uploaded_at': datetime.now(),
            'processed': False
        }
        
        return {
            "success": True,
            "message": "Sample data generated successfully",
            "data": {
                "dataset_id": dataset_id,
                "data_type": data_type,
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": df.columns.tolist()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sample data generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Sample data generation failed: {str(e)}")

@app.get("/api/v1/datasets")
async def list_datasets():
    """List all available datasets"""
    try:
        datasets = []
        
        for dataset_id, dataset in data_store.items():
            data = dataset.get('cleaned_data', dataset['raw_data'])
            
            datasets.append({
                "dataset_id": dataset_id,
                "filename": dataset['filename'],
                "rows": len(data),
                "columns": len(data.columns),
                "processed": dataset.get('processed', False),
                "uploaded_at": dataset['uploaded_at'].isoformat(),
                "size_mb": round(data.memory_usage(deep=True).sum() / 1024 / 1024, 2)
            })
        
        return {
            "success": True,
            "data": {
                "datasets": datasets,
                "total_count": len(datasets)
            }
        }
        
    except Exception as e:
        logger.error(f"Error listing datasets: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list datasets: {str(e)}")

@app.delete("/api/v1/data/{dataset_id}")
async def delete_dataset(dataset_id: str):
    """Delete a dataset"""
    try:
        if dataset_id not in data_store:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        del data_store[dataset_id]
        
        return {
            "success": True,
            "message": "Dataset deleted successfully",
            "data": {
                "dataset_id": dataset_id,
                "deleted_at": datetime.now().isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting dataset {dataset_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete dataset: {str(e)}")

# Background task for cleanup
@app.on_event("startup")
async def startup_event():
    """Initialize application"""
    logger.info("Data Analytics Dashboard API starting up...")
    
    # Create necessary directories
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("exports", exist_ok=True)
    os.makedirs("temp", exist_ok=True)
    
    logger.info("API startup completed successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Data Analytics Dashboard API shutting down...")
    
    # Cleanup temporary files
    import shutil
    if os.path.exists("temp"):
        shutil.rmtree("temp")
    
    logger.info("API shutdown completed")

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )