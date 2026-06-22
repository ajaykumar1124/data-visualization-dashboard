"""
Regenerate all sample data files with proper datetime handling
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)

def generate_academic_data():
    """Generate clean academic data"""
    n = 1000
    data = {
        'student_id': np.arange(1, n + 1),
        'name': [f'Student_{i}' for i in range(1, n + 1)],
        'gpa': np.random.uniform(2.0, 4.0, n),
        'enrollment_date': pd.date_range(start='2019-01-01', periods=n, freq='D'),
        'graduation_year': np.random.choice([2023, 2024, 2025, 2026], n),
        'department': np.random.choice(['Engineering', 'Business', 'Arts', 'Science'], n),
        'credits_completed': np.random.randint(0, 130, n),
    }
    df = pd.DataFrame(data)
    df['enrollment_date'] = pd.to_datetime(df['enrollment_date'])
    return df

def generate_business_data():
    """Generate clean business data"""
    n = 1000
    data = {
        'transaction_id': np.arange(1, n + 1),
        'customer_name': [f'Customer_{i}' for i in range(1, n + 1)],
        'sales_amount': np.random.uniform(100, 10000, n),
        'transaction_date': pd.date_range(start='2024-01-01', periods=n, freq='h'),
        'region': np.random.choice(['North', 'South', 'East', 'West'], n),
        'product_category': np.random.choice(['Electronics', 'Clothing', 'Food', 'Books'], n),
        'units_sold': np.random.randint(1, 50, n),
    }
    df = pd.DataFrame(data)
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    return df

def generate_financial_data():
    """Generate clean financial data"""
    n = 1000
    data = {
        'account_id': np.arange(1, n + 1),
        'account_holder': [f'Holder_{i}' for i in range(1, n + 1)],
        'balance': np.random.uniform(1000, 100000, n),
        'last_transaction_date': pd.date_range(start='2025-01-01', periods=n, freq='h'),
        'account_type': np.random.choice(['Savings', 'Checking', 'Investment'], n),
        'interest_rate': np.random.uniform(0.5, 5.0, n),
        'transactions_count': np.random.randint(1, 500, n),
    }
    df = pd.DataFrame(data)
    df['last_transaction_date'] = pd.to_datetime(df['last_transaction_date'])
    return df

def generate_healthcare_data():
    """Generate clean healthcare data"""
    n = 1000
    data = {
        'patient_id': np.arange(1, n + 1),
        'patient_name': [f'Patient_{i}' for i in range(1, n + 1)],
        'age': np.random.randint(18, 85, n),
        'admission_date': pd.date_range(start='2024-01-01', periods=n, freq='h'),
        'department': np.random.choice(['Cardiology', 'Neurology', 'Orthopedics', 'General'], n),
        'blood_pressure_systolic': np.random.randint(90, 180, n),
        'blood_pressure_diastolic': np.random.randint(60, 120, n),
        'length_of_stay_days': np.random.randint(1, 30, n),
    }
    df = pd.DataFrame(data)
    df['admission_date'] = pd.to_datetime(df['admission_date'])
    return df

if __name__ == "__main__":
    print("🔄 Regenerating sample data files...")
    print("=" * 60)
    
    datasets = {
        'academic_data.csv': generate_academic_data(),
        'business_data.csv': generate_business_data(),
        'financial_data.csv': generate_financial_data(),
        'healthcare_data.csv': generate_healthcare_data(),
    }
    
    for filename, df in datasets.items():
        filepath = f'sample_data/{filename}'
        df.to_csv(filepath, index=False)
        print(f"✅ Generated: {filename} ({len(df)} rows)")
        print(f"   Columns: {', '.join(df.columns)}")
        print(f"   Types: {dict(df.dtypes)}")
        print()
    
    print("=" * 60)
    print("✅ All sample data files regenerated successfully!")
    print("💡 All datetime columns are now properly formatted")
