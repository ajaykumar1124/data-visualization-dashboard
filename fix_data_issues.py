"""
Data Fix Script - Resolves timestamp and data type conversion issues
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def fix_timestamp_columns(df):
    """
    Fix timestamp columns that are stored as strings
    Converts them to proper datetime format
    """
    for column in df.columns:
        # Check if column name suggests it's a date/time column
        if any(keyword in column.lower() for keyword in ['date', 'time', 'created', 'updated', 'hire', 'birth', 'start', 'end']):
            try:
                # Try to convert to datetime
                df[column] = pd.to_datetime(df[column], errors='coerce', utc=True)
                print(f"✅ Fixed column: {column} -> converted to datetime")
            except Exception as e:
                print(f"⚠️  Could not convert {column}: {e}")
    
    return df

def fix_object_dtype_issues(df):
    """
    Fix object dtype columns that should be numeric or datetime
    """
    for column in df.select_dtypes(include=['object']).columns:
        # Try numeric conversion first
        try:
            temp = pd.to_numeric(df[column], errors='coerce')
            if temp.notna().sum() / len(df) > 0.8:  # If 80%+ can be converted
                df[column] = temp
                print(f"✅ Fixed column: {column} -> converted to numeric")
                continue
        except:
            pass
        
        # Try datetime conversion for date-like columns
        if any(keyword in column.lower() for keyword in ['date', 'time', 'created', 'updated', 'hire', 'birth']):
            try:
                df[column] = pd.to_datetime(df[column], errors='coerce', utc=True)
                print(f"✅ Fixed column: {column} -> converted to datetime")
                continue
            except:
                pass
    
    return df

def clean_timestamp_values(df):
    """
    Clean invalid timestamp values (like future dates or impossible timestamps)
    """
    current_year = datetime.now().year
    
    for column in df.select_dtypes(include=['datetime64']).columns:
        # Check for future dates (beyond current year + 10)
        future_mask = df[column].dt.year > (current_year + 10)
        if future_mask.any():
            print(f"⚠️  Found {future_mask.sum()} future dates in {column}")
            # Replace with reasonable default (current date)
            df.loc[future_mask, column] = datetime.now()
            print(f"✅ Fixed future dates in {column}")
        
        # Check for very old dates (before 1950)
        old_mask = df[column].dt.year < 1950
        if old_mask.any():
            print(f"⚠️  Found {old_mask.sum()} very old dates in {column}")
            # Replace with NaT
            df.loc[old_mask, column] = pd.NaT
            print(f"✅ Cleaned old dates in {column}")
    
    return df

def apply_arrow_compatible_formatting(df):
    """
    Ensure all data types are compatible with PyArrow serialization
    """
    for column in df.columns:
        # Convert object dtype strings to string type if possible
        if df[column].dtype == 'object':
            try:
                # Check if all values are strings or NaN
                if all(isinstance(x, str) or pd.isna(x) for x in df[column]):
                    df[column] = df[column].astype('string')
                    print(f"✅ Fixed column: {column} -> converted to string type")
            except:
                pass
    
    return df

def create_clean_sample_data():
    """
    Generate clean sample data that won't cause Arrow conversion errors
    """
    np.random.seed(42)
    n_records = 100
    
    # Create base data with proper dtypes from the start
    data = {
        'employee_id': np.arange(1, n_records + 1),
        'name': [f'Employee_{i}' for i in range(1, n_records + 1)],
        'department': np.random.choice(['Sales', 'HR', 'IT', 'Finance'], n_records),
        'salary': np.random.randint(30000, 150000, n_records),
        'hire_date': pd.date_range(start='2015-01-01', periods=n_records, freq='D'),  # Proper datetime
        'performance_score': np.random.uniform(2.0, 5.0, n_records),
        'tenure_years': np.random.randint(0, 15, n_records),
    }
    
    df = pd.DataFrame(data)
    
    # Ensure correct dtypes
    df['hire_date'] = pd.to_datetime(df['hire_date'])
    df['department'] = df['department'].astype('string')
    df['name'] = df['name'].astype('string')
    
    return df

if __name__ == "__main__":
    print("🔧 Data Fix Script")
    print("=" * 50)
    
    # Test with clean sample data
    print("\n📊 Creating clean sample data...")
    clean_df = create_clean_sample_data()
    print(f"✅ Created sample data with {len(clean_df)} rows")
    print(f"Data types:\n{clean_df.dtypes}")
    
    # Save for verification
    clean_df.to_csv('sample_data/clean_academic_data.csv', index=False)
    print("✅ Saved to sample_data/clean_academic_data.csv")
