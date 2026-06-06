# 📚 API Documentation - Data Analytics Dashboard

## 🔗 Base Information

- **Base URL**: `http://localhost:8000`
- **API Version**: `v1`
- **Authentication**: JWT Bearer Token / API Key
- **Content Type**: `application/json`
- **Documentation**: `http://localhost:8000/docs` (Swagger UI)
- **Alternative Docs**: `http://localhost:8000/redoc`

## 🔐 Authentication

### Register User
```http
POST /api/v1/auth/register
```

**Parameters:**
```json
{
  "username": "string",
  "email": "string", 
  "password": "string",
  "full_name": "string (optional)",
  "organization": "string (optional)"
}
```

**Response:**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": "uuid",
    "username": "string",
    "email": "string",
    "role": "user"
  }
}
```

### Login
```http
POST /api/v1/auth/login
```

**Parameters:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "jwt_token",
  "refresh_token": "jwt_token", 
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "username": "string",
    "email": "string",
    "role": "user"
  }
}
```

### Get Current User
```http
GET /api/v1/auth/me
Authorization: Bearer {token}
```

**Response:**
```json
{
  "id": "uuid",
  "username": "string",
  "email": "string",
  "full_name": "string",
  "organization": "string",
  "role": "user",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "last_login": "2024-01-01T00:00:00Z"
}
```

## 📊 Data Management

### Upload Dataset
```http
POST /api/v1/data/upload
Authorization: Bearer {token}
Content-Type: multipart/form-data
```

**Parameters:**
- `file`: CSV or Excel file (max 200MB)

**Response:**
```json
{
  "id": "uuid",
  "filename": "data.csv",
  "rows_count": 1000,
  "columns_count": 10,
  "column_names": ["col1", "col2", "..."],
  "data_types": {"col1": "int64", "col2": "object"},
  "file_size": 1024000,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Process Dataset
```http
POST /api/v1/data/process/{dataset_id}
Authorization: Bearer {token}
Content-Type: application/json
```

**Parameters:**
```json
{
  "remove_outliers": false,
  "missing_threshold": 0.5,
  "duplicate_strategy": "first"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Dataset processed successfully",
  "cleaning_report": {
    "original_rows": 1000,
    "final_rows": 950,
    "missing_values_handled": 50,
    "duplicates_removed": 25,
    "format_corrections": 100,
    "accuracy_score": 0.98
  },
  "original_rows": 1000,
  "processed_rows": 950
}
```

### List Datasets
```http
GET /api/v1/data/datasets?skip=0&limit=100
Authorization: Bearer {token}
```

**Response:**
```json
[
  {
    "id": "uuid",
    "filename": "data.csv",
    "rows_count": 950,
    "columns_count": 10,
    "is_processed": true,
    "created_at": "2024-01-01T00:00:00Z",
    "file_size": 1024000
  }
]
```

### Get Dataset Info
```http
GET /api/v1/data/datasets/{dataset_id}
Authorization: Bearer {token}
```

**Response:**
```json
{
  "id": "uuid",
  "filename": "data.csv",
  "original_filename": "data.csv",
  "rows_count": 950,
  "columns_count": 10,
  "column_names": ["col1", "col2", "..."],
  "data_types": {"col1": "int64", "col2": "object"},
  "is_processed": true,
  "created_at": "2024-01-01T00:00:00Z",
  "file_size": 1024000
}
```

### Get Dataset Preview
```http
GET /api/v1/data/datasets/{dataset_id}/preview?rows=10
Authorization: Bearer {token}
```

**Response:**
```json
{
  "preview": [
    {"col1": 1, "col2": "value1"},
    {"col1": 2, "col2": "value2"}
  ],
  "summary_stats": {
    "col1": {
      "count": 950,
      "mean": 500.5,
      "std": 274.4,
      "min": 1,
      "max": 1000
    }
  },
  "total_rows": 950,
  "columns": ["col1", "col2", "..."],
  "data_types": {"col1": "int64", "col2": "object"}
}
```

### Delete Dataset
```http
DELETE /api/v1/data/datasets/{dataset_id}
Authorization: Bearer {token}
```

**Response:**
```json
{
  "message": "Dataset deleted successfully"
}
```

## 📈 Visualizations

### Create Visualization
```http
POST /api/v1/visualizations/create/{dataset_id}
Authorization: Bearer {token}
Content-Type: application/json
```

**Parameters:**
```json
{
  "viz_type": "trend|distribution|categorical|correlation|dashboard|comparative",
  "title": "Chart Title",
  "description": "Chart description (optional)",
  "config": {
    "x_column": "date",
    "y_column": "value",
    "category_column": "category",
    "value_columns": ["metric1", "metric2"]
  }
}
```

**Visualization Types & Required Config:**

#### Trend Analysis
```json
{
  "viz_type": "trend",
  "config": {
    "x_column": "date_column",
    "y_column": "numeric_column"
  }
}
```

#### Distribution Analysis
```json
{
  "viz_type": "distribution", 
  "config": {
    "column": "numeric_column"
  }
}
```

#### Categorical Comparison
```json
{
  "viz_type": "categorical",
  "config": {
    "category_column": "categorical_column",
    "value_column": "numeric_column"
  }
}
```

#### Correlation Heatmap
```json
{
  "viz_type": "correlation",
  "config": {}
}
```

#### Performance Dashboard
```json
{
  "viz_type": "dashboard",
  "config": {}
}
```

#### Comparative Analysis
```json
{
  "viz_type": "comparative",
  "config": {
    "group_column": "categorical_column",
    "value_columns": ["metric1", "metric2", "metric3"]
  }
}
```

**Response:**
```json
{
  "id": "uuid",
  "dataset_id": "uuid",
  "viz_type": "trend",
  "title": "Chart Title",
  "description": "Chart description",
  "config": {...},
  "chart_data": {
    "data": [...],
    "layout": {...},
    "config": {...}
  },
  "created_at": "2024-01-01T00:00:00Z"
}
```

### List Visualizations
```http
GET /api/v1/visualizations/dataset/{dataset_id}
Authorization: Bearer {token}
```

**Response:**
```json
[
  {
    "id": "uuid",
    "dataset_id": "uuid", 
    "viz_type": "trend",
    "title": "Chart Title",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

### Get Visualization
```http
GET /api/v1/visualizations/{viz_id}
Authorization: Bearer {token}
```

**Response:**
```json
{
  "id": "uuid",
  "dataset_id": "uuid",
  "viz_type": "trend", 
  "title": "Chart Title",
  "description": "Chart description",
  "config": {...},
  "chart_data": {
    "data": [...],
    "layout": {...},
    "config": {...}
  },
  "created_at": "2024-01-01T00:00:00Z"
}
```

## 📤 Export & Reports

### Create Export Job
```http
POST /api/v1/export/create/{dataset_id}
Authorization: Bearer {token}
Content-Type: application/json
```

**Parameters:**
```json
{
  "export_format": "csv|excel|pdf",
  "export_config": {
    "include_report": true,
    "include_visualizations": false
  }
}
```

**Response:**
```json
{
  "id": "uuid",
  "dataset_id": "uuid",
  "export_format": "excel",
  "status": "pending",
  "progress": 0.0,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Get Export Status
```http
GET /api/v1/export/jobs/{job_id}
Authorization: Bearer {token}
```

**Response:**
```json
{
  "id": "uuid",
  "dataset_id": "uuid",
  "export_format": "excel",
  "status": "completed",
  "progress": 100.0,
  "output_filename": "export_20240101_120000.xlsx",
  "file_size": 2048000,
  "created_at": "2024-01-01T00:00:00Z",
  "completed_at": "2024-01-01T00:01:00Z"
}
```

### Download Export File
```http
GET /api/v1/export/download/{filename}
Authorization: Bearer {token}
```

**Response:** Binary file download

## 🎲 Sample Data

### Generate Sample Data
```http
POST /api/v1/sample-data
Authorization: Bearer {token}
Content-Type: application/json
```

**Parameters:**
```json
{
  "type": "academic|business|healthcare|financial",
  "rows": 1000
}
```

**Response:**
```json
{
  "success": true,
  "message": "Sample data generated successfully",
  "data": {
    "dataset_id": "uuid",
    "data_type": "academic",
    "rows": 1000,
    "columns": 12,
    "column_names": ["student_id", "name", "gpa", "..."]
  }
}
```

## 👑 Administration (Admin Only)

### List All Users
```http
GET /api/v1/admin/users?skip=0&limit=100
Authorization: Bearer {admin_token}
```

**Response:**
```json
[
  {
    "id": "uuid",
    "username": "user1",
    "email": "user1@example.com",
    "full_name": "User One",
    "role": "user",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "last_login": "2024-01-01T00:00:00Z"
  }
]
```

### Get System Statistics
```http
GET /api/v1/admin/stats
Authorization: Bearer {admin_token}
```

**Response:**
```json
{
  "total_users": 100,
  "total_datasets": 500,
  "total_visualizations": 1200,
  "processed_datasets": 450,
  "processing_rate": 0.9
}
```

## 🔍 System Endpoints

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "version": "1.0.0",
  "components": {
    "database": {"status": "healthy"},
    "filesystem": {
      "uploads_dir": true,
      "exports_dir": true,
      "temp_dir": true
    },
    "api": "operational"
  }
}
```

### API Information
```http
GET /info
```

**Response:**
```json
{
  "api": {
    "name": "Data Analytics Dashboard API",
    "version": "1.0.0",
    "description": "REST API for data processing and visualization"
  },
  "database": {
    "type": "PostgreSQL",
    "tables": ["users", "datasets", "visualizations", "..."]
  },
  "features": {
    "data_processing": {
      "max_file_size": "200MB",
      "supported_formats": ["CSV", "Excel"],
      "cleaning_accuracy": "98%",
      "max_rows": "15,000+"
    },
    "visualizations": {
      "types": ["trend", "distribution", "categorical", "correlation", "dashboard", "comparative"],
      "export_formats": ["PNG", "PDF", "SVG", "JSON"]
    }
  }
}
```

## 🚨 Error Responses

### Standard Error Format
```json
{
  "error": true,
  "message": "Error description",
  "status_code": 400,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Common HTTP Status Codes

- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid request parameters
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **413 Payload Too Large**: File too large (>200MB)
- **422 Unprocessable Entity**: Validation error
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server error

### Error Examples

**Authentication Error:**
```json
{
  "error": true,
  "message": "Could not validate credentials",
  "status_code": 401,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

**Validation Error:**
```json
{
  "error": true,
  "message": "Invalid visualization type",
  "status_code": 400,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

**Rate Limit Error:**
```json
{
  "error": true,
  "message": "Rate limit exceeded",
  "status_code": 429,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## 📝 Usage Examples

### Python Client Example
```python
import requests
import json

class AnalyticsAPI:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None
    
    def login(self, username, password):
        response = self.session.post(
            f"{self.base_url}/api/v1/auth/login",
            params={"username": username, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            self.token = data["access_token"]
            self.session.headers.update({
                "Authorization": f"Bearer {self.token}"
            })
            return True
        return False
    
    def upload_data(self, file_path):
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = self.session.post(
                f"{self.base_url}/api/v1/data/upload",
                files=files
            )
        return response.json() if response.status_code == 200 else None
    
    def process_data(self, dataset_id, config=None):
        response = self.session.post(
            f"{self.base_url}/api/v1/data/process/{dataset_id}",
            json=config or {}
        )
        return response.json() if response.status_code == 200 else None
    
    def create_visualization(self, dataset_id, viz_config):
        response = self.session.post(
            f"{self.base_url}/api/v1/visualizations/create/{dataset_id}",
            json=viz_config
        )
        return response.json() if response.status_code == 200 else None

# Usage
api = AnalyticsAPI()
api.login("username", "password")

# Upload and process data
dataset = api.upload_data("data.csv")
if dataset:
    processed = api.process_data(dataset["id"])
    
    # Create visualization
    viz = api.create_visualization(dataset["id"], {
        "viz_type": "trend",
        "title": "Sales Trend",
        "config": {"x_column": "date", "y_column": "sales"}
    })
```

### JavaScript/Node.js Example
```javascript
const axios = require('axios');

class AnalyticsAPI {
    constructor(baseURL = 'http://localhost:8000') {
        this.client = axios.create({ baseURL });
        this.token = null;
    }
    
    async login(username, password) {
        try {
            const response = await this.client.post('/api/v1/auth/login', null, {
                params: { username, password }
            });
            
            this.token = response.data.access_token;
            this.client.defaults.headers.common['Authorization'] = `Bearer ${this.token}`;
            return true;
        } catch (error) {
            console.error('Login failed:', error.response?.data);
            return false;
        }
    }
    
    async uploadData(filePath) {
        const FormData = require('form-data');
        const fs = require('fs');
        
        const form = new FormData();
        form.append('file', fs.createReadStream(filePath));
        
        try {
            const response = await this.client.post('/api/v1/data/upload', form, {
                headers: form.getHeaders()
            });
            return response.data;
        } catch (error) {
            console.error('Upload failed:', error.response?.data);
            return null;
        }
    }
    
    async createVisualization(datasetId, config) {
        try {
            const response = await this.client.post(
                `/api/v1/visualizations/create/${datasetId}`,
                config
            );
            return response.data;
        } catch (error) {
            console.error('Visualization failed:', error.response?.data);
            return null;
        }
    }
}

// Usage
const api = new AnalyticsAPI();
await api.login('username', 'password');

const dataset = await api.uploadData('./data.csv');
if (dataset) {
    const viz = await api.createVisualization(dataset.id, {
        viz_type: 'distribution',
        title: 'Data Distribution',
        config: { column: 'value' }
    });
}
```

### cURL Examples
```bash
# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -d "username=testuser&password=testpass"

# Upload file
curl -X POST "http://localhost:8000/api/v1/data/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@data.csv"

# Create visualization
curl -X POST "http://localhost:8000/api/v1/visualizations/create/DATASET_ID" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "viz_type": "trend",
    "title": "Sales Trend",
    "config": {"x_column": "date", "y_column": "sales"}
  }'
```

## 🔄 Rate Limiting

- **Default Limit**: 100 requests per hour per user
- **Upload Limit**: 5 uploads per hour per user
- **Headers**: 
  - `X-RateLimit-Limit`: Request limit
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Reset timestamp

## 🔒 Security Notes

- Always use HTTPS in production
- Store JWT tokens securely
- Implement proper CORS policies
- Use API keys for service-to-service communication
- Validate all file uploads
- Monitor for suspicious activity

---

## 📞 Support

- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **GitHub Issues**: For bug reports and feature requests
- **API Status**: Monitor at http://localhost:8000/health