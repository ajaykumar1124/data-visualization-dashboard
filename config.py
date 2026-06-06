"""
Configuration Settings for Data Analytics Dashboard
Centralized configuration management
"""

import os
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class DataProcessingConfig:
    """Configuration for data processing pipeline"""
    
    # Missing value handling
    missing_value_threshold: float = 0.5  # Drop columns with >50% missing
    numeric_fill_strategy: str = "median"  # median, mean, mode
    categorical_fill_strategy: str = "mode"  # mode, unknown
    datetime_fill_strategy: str = "forward_fill"  # forward_fill, backward_fill
    
    # Duplicate handling
    duplicate_strategy: str = "first"  # first, last, all
    duplicate_subset: List[str] = None  # Columns to check for duplicates
    
    # Outlier detection
    remove_outliers: bool = False
    outlier_method: str = "iqr"  # iqr, zscore, isolation_forest
    outlier_threshold: float = 1.5  # IQR multiplier or Z-score threshold
    
    # Data type validation
    auto_convert_types: bool = True
    date_format: str = "auto"  # auto, or specific format like "%Y-%m-%d"
    
    # Performance settings
    chunk_size: int = 10000  # For large file processing
    memory_limit_mb: int = 1000  # Memory usage limit

@dataclass
class VisualizationConfig:
    """Configuration for visualization engine"""
    
    # Chart styling
    color_palette: List[str] = None
    figure_size: tuple = (12, 8)
    template: str = "plotly_white"  # plotly_white, plotly_dark, seaborn
    font_family: str = "Arial"
    font_size: int = 12
    
    # Chart limits
    max_categories: int = 20  # Maximum categories in bar charts
    max_points: int = 10000  # Maximum points in scatter plots
    
    # Export settings
    export_format: str = "png"  # png, jpg, pdf, svg
    export_dpi: int = 300
    
    def __post_init__(self):
        if self.color_palette is None:
            self.color_palette = [
                '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', 
                '#9467bd', '#8c564b', '#e377c2', '#7f7f7f'
            ]

@dataclass
class DashboardConfig:
    """Configuration for Streamlit dashboard"""
    
    # Page settings
    page_title: str = "Data Analytics & Visualization Dashboard"
    page_icon: str = "📊"
    layout: str = "wide"  # wide, centered
    
    # File upload settings
    max_file_size_mb: int = 200
    allowed_file_types: List[str] = None
    
    # Performance settings
    cache_ttl: int = 3600  # Cache time-to-live in seconds
    max_cached_datasets: int = 5
    
    # UI settings
    show_sidebar: bool = True
    show_footer: bool = True
    theme: str = "light"  # light, dark, auto
    
    def __post_init__(self):
        if self.allowed_file_types is None:
            self.allowed_file_types = ['csv', 'xlsx', 'xls', 'json', 'parquet']

@dataclass
class DatabaseConfig:
    """Configuration for database connections"""
    
    # Connection settings
    host: str = "localhost"
    port: int = 5432
    database: str = ""
    username: str = ""
    password: str = ""
    
    # Connection pool settings
    max_connections: int = 10
    connection_timeout: int = 30
    
    # Query settings
    query_timeout: int = 300  # 5 minutes
    max_rows: int = 100000

class Config:
    """Main configuration class"""
    
    def __init__(self):
        self.data_processing = DataProcessingConfig()
        self.visualization = VisualizationConfig()
        self.dashboard = DashboardConfig()
        self.database = DatabaseConfig()
        
        # Load environment variables
        self._load_from_env()
    
    def _load_from_env(self):
        """Load configuration from environment variables"""
        
        # Data processing settings
        if os.getenv('MISSING_THRESHOLD'):
            self.data_processing.missing_value_threshold = float(os.getenv('MISSING_THRESHOLD'))
        
        if os.getenv('REMOVE_OUTLIERS'):
            self.data_processing.remove_outliers = os.getenv('REMOVE_OUTLIERS').lower() == 'true'
        
        # Dashboard settings
        if os.getenv('MAX_FILE_SIZE_MB'):
            self.dashboard.max_file_size_mb = int(os.getenv('MAX_FILE_SIZE_MB'))
        
        if os.getenv('DASHBOARD_THEME'):
            self.dashboard.theme = os.getenv('DASHBOARD_THEME')
        
        # Database settings
        if os.getenv('DB_HOST'):
            self.database.host = os.getenv('DB_HOST')
        
        if os.getenv('DB_PORT'):
            self.database.port = int(os.getenv('DB_PORT'))
        
        if os.getenv('DB_NAME'):
            self.database.database = os.getenv('DB_NAME')
        
        if os.getenv('DB_USER'):
            self.database.username = os.getenv('DB_USER')
        
        if os.getenv('DB_PASSWORD'):
            self.database.password = os.getenv('DB_PASSWORD')
    
    def update_config(self, section: str, **kwargs):
        """Update configuration values"""
        if section == 'data_processing':
            for key, value in kwargs.items():
                if hasattr(self.data_processing, key):
                    setattr(self.data_processing, key, value)
        
        elif section == 'visualization':
            for key, value in kwargs.items():
                if hasattr(self.visualization, key):
                    setattr(self.visualization, key, value)
        
        elif section == 'dashboard':
            for key, value in kwargs.items():
                if hasattr(self.dashboard, key):
                    setattr(self.dashboard, key, value)
        
        elif section == 'database':
            for key, value in kwargs.items():
                if hasattr(self.database, key):
                    setattr(self.database, key, value)
    
    def get_config_dict(self) -> Dict[str, Any]:
        """Get configuration as dictionary"""
        return {
            'data_processing': self.data_processing.__dict__,
            'visualization': self.visualization.__dict__,
            'dashboard': self.dashboard.__dict__,
            'database': self.database.__dict__
        }
    
    def save_config(self, filepath: str = "config.json"):
        """Save configuration to JSON file"""
        import json
        
        config_dict = self.get_config_dict()
        
        with open(filepath, 'w') as f:
            json.dump(config_dict, f, indent=2, default=str)
    
    def load_config(self, filepath: str = "config.json"):
        """Load configuration from JSON file"""
        import json
        
        try:
            with open(filepath, 'r') as f:
                config_dict = json.load(f)
            
            # Update configurations
            for section, values in config_dict.items():
                self.update_config(section, **values)
                
        except FileNotFoundError:
            print(f"Configuration file {filepath} not found. Using defaults.")
        except Exception as e:
            print(f"Error loading configuration: {e}. Using defaults.")

# Global configuration instance
config = Config()

# Predefined configuration presets
PRESETS = {
    'academic': {
        'data_processing': {
            'missing_value_threshold': 0.3,
            'remove_outliers': False,
            'numeric_fill_strategy': 'median'
        },
        'visualization': {
            'template': 'plotly_white',
            'color_palette': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        }
    },
    
    'business': {
        'data_processing': {
            'missing_value_threshold': 0.2,
            'remove_outliers': True,
            'numeric_fill_strategy': 'mean'
        },
        'visualization': {
            'template': 'plotly_white',
            'color_palette': ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']
        }
    },
    
    'research': {
        'data_processing': {
            'missing_value_threshold': 0.1,
            'remove_outliers': False,
            'auto_convert_types': False
        },
        'visualization': {
            'template': 'plotly_white',
            'font_family': 'Times New Roman',
            'export_format': 'pdf'
        }
    }
}

def apply_preset(preset_name: str):
    """Apply a predefined configuration preset"""
    if preset_name not in PRESETS:
        raise ValueError(f"Unknown preset: {preset_name}. Available: {list(PRESETS.keys())}")
    
    preset = PRESETS[preset_name]
    
    for section, values in preset.items():
        config.update_config(section, **values)
    
    print(f"Applied '{preset_name}' configuration preset")

def get_available_presets() -> List[str]:
    """Get list of available configuration presets"""
    return list(PRESETS.keys())

# Environment-specific settings
if os.getenv('ENVIRONMENT') == 'development':
    config.dashboard.cache_ttl = 60  # Shorter cache in development
    config.data_processing.chunk_size = 1000  # Smaller chunks for testing

elif os.getenv('ENVIRONMENT') == 'production':
    config.dashboard.cache_ttl = 7200  # Longer cache in production
    config.data_processing.memory_limit_mb = 2000  # More memory in production