"""
Sample Data Generator
Creates realistic datasets for testing the analytics dashboard
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from typing import Dict, List, Optional

class SampleDataGenerator:
    """
    Generates various types of sample datasets for testing the dashboard
    """
    
    def __init__(self, seed: int = 42):
        np.random.seed(seed)
        random.seed(seed)
        
    def generate_academic_dataset(self, n_rows: int = 15000) -> pd.DataFrame:
        """
        Generate academic/university dataset with realistic data quality issues
        """
        # Student performance data
        departments = ['Computer Science', 'Mathematics', 'Physics', 'Chemistry', 'Biology', 'Engineering']
        programs = ['Bachelor', 'Master', 'PhD']
        semesters = ['Fall 2023', 'Spring 2024', 'Fall 2024']
        
        data = {
            'student_id': [f"STU{str(i).zfill(6)}" for i in range(1, n_rows + 1)],
            'name': [self._generate_name() if i % 100 != 0 else None for i in range(n_rows)],
            'department': np.random.choice(departments + [None], n_rows, p=[0.15, 0.15, 0.15, 0.15, 0.15, 0.2, 0.05]),
            'program': np.random.choice(programs, n_rows, p=[0.6, 0.3, 0.1]),
            'semester': np.random.choice(semesters, n_rows),
            'gpa': [round(np.random.normal(3.2, 0.8), 2) if i % 50 != 0 else None for i in range(n_rows)],
            'credits_completed': [np.random.randint(0, 180) if i % 75 != 0 else None for i in range(n_rows)],
            'age': [np.random.randint(18, 35) if i % 60 != 0 else None for i in range(n_rows)],
            'enrollment_date': pd.date_range('2020-01-01', periods=n_rows, freq='D'),
            'tuition_paid': [np.random.normal(25000, 5000) if i % 40 != 0 else None for i in range(n_rows)],
            'scholarship_amount': [np.random.exponential(2000) if np.random.random() > 0.7 else 0 for _ in range(n_rows)],
            'graduation_status': np.random.choice(['Enrolled', 'Graduated', 'Dropped', 'Transferred'], n_rows, p=[0.7, 0.15, 0.1, 0.05])
        }
        
        df = pd.DataFrame(data)
        
        # Add data quality issues
        df = self._add_data_quality_issues(df)
        
        return df
    
    def generate_business_dataset(self, n_rows: int = 15000) -> pd.DataFrame:
        """
        Generate business/sales dataset with realistic patterns
        """
        regions = ['North', 'South', 'East', 'West', 'Central']
        products = ['Product A', 'Product B', 'Product C', 'Product D', 'Product E']
        sales_reps = [f"Rep_{i}" for i in range(1, 51)]
        
        data = {
            'transaction_id': [f"TXN{str(i).zfill(8)}" for i in range(1, n_rows + 1)],
            'sales_rep': np.random.choice(sales_reps + [None], n_rows, p=[0.02] * 50 + [0.0]),
            'region': np.random.choice(regions, n_rows),
            'product': np.random.choice(products, n_rows),
            'sale_date': pd.date_range('2023-01-01', periods=n_rows, freq='h'),
            'quantity': [np.random.poisson(5) + 1 if i % 100 != 0 else None for i in range(n_rows)],
            'unit_price': [round(np.random.uniform(10, 500), 2) if i % 80 != 0 else None for i in range(n_rows)],
            'discount_percent': [round(np.random.uniform(0, 25), 1) if np.random.random() > 0.6 else 0 for _ in range(n_rows)],
            'customer_satisfaction': [np.random.randint(1, 6) if i % 120 != 0 else None for i in range(n_rows)],
            'shipping_cost': [round(np.random.uniform(5, 50), 2) if i % 90 != 0 else None for i in range(n_rows)],
            'customer_type': np.random.choice(['New', 'Returning', 'VIP'], n_rows, p=[0.3, 0.6, 0.1])
        }
        
        df = pd.DataFrame(data)
        
        # Calculate derived fields
        df['total_revenue'] = df['quantity'] * df['unit_price'] * (1 - df['discount_percent'] / 100)
        df['profit_margin'] = np.random.uniform(0.1, 0.4, n_rows)
        df['profit'] = df['total_revenue'] * df['profit_margin']
        
        # Add data quality issues
        df = self._add_data_quality_issues(df)
        
        return df
    
    def generate_healthcare_dataset(self, n_rows: int = 15000) -> pd.DataFrame:
        """
        Generate healthcare/medical dataset
        """
        conditions = ['Diabetes', 'Hypertension', 'Heart Disease', 'Asthma', 'Arthritis', 'None']
        treatments = ['Medication', 'Surgery', 'Therapy', 'Lifestyle', 'Monitoring']
        
        data = {
            'patient_id': [f"PAT{str(i).zfill(7)}" for i in range(1, n_rows + 1)],
            'age': [np.random.randint(18, 90) if i % 50 != 0 else None for i in range(n_rows)],
            'gender': np.random.choice(['Male', 'Female', 'Other'], n_rows, p=[0.48, 0.48, 0.04]),
            'condition': np.random.choice(conditions, n_rows, p=[0.15, 0.2, 0.1, 0.15, 0.1, 0.3]),
            'treatment': np.random.choice(treatments, n_rows),
            'admission_date': pd.date_range('2023-01-01', periods=n_rows, freq='6h'),
            'length_of_stay': [np.random.poisson(3) + 1 if i % 70 != 0 else None for i in range(n_rows)],
            'treatment_cost': [np.random.lognormal(8, 1) if i % 60 != 0 else None for i in range(n_rows)],
            'insurance_coverage': [np.random.uniform(0.5, 1.0) if i % 80 != 0 else None for i in range(n_rows)],
            'satisfaction_score': [np.random.randint(1, 11) if i % 100 != 0 else None for i in range(n_rows)],
            'readmission': np.random.choice([True, False], n_rows, p=[0.15, 0.85]),
            'outcome': np.random.choice(['Improved', 'Stable', 'Declined'], n_rows, p=[0.7, 0.25, 0.05])
        }
        
        df = pd.DataFrame(data)
        
        # Add data quality issues
        df = self._add_data_quality_issues(df)
        
        return df
    
    def generate_financial_dataset(self, n_rows: int = 15000) -> pd.DataFrame:
        """
        Generate financial/investment dataset
        """
        asset_types = ['Stock', 'Bond', 'ETF', 'Mutual Fund', 'Commodity']
        sectors = ['Technology', 'Healthcare', 'Finance', 'Energy', 'Consumer', 'Industrial']
        
        data = {
            'asset_id': [f"AST{str(i).zfill(6)}" for i in range(1, n_rows + 1)],
            'asset_name': [f"Asset_{i}" if i % 150 != 0 else None for i in range(n_rows)],
            'asset_type': np.random.choice(asset_types, n_rows),
            'sector': np.random.choice(sectors, n_rows),
            'purchase_date': pd.date_range('2020-01-01', periods=n_rows, freq='D'),
            'purchase_price': [round(np.random.lognormal(4, 1), 2) if i % 80 != 0 else None for i in range(n_rows)],
            'current_price': [round(np.random.lognormal(4, 1), 2) if i % 90 != 0 else None for i in range(n_rows)],
            'quantity': [np.random.randint(1, 1000) if i % 70 != 0 else None for i in range(n_rows)],
            'dividend_yield': [round(np.random.uniform(0, 8), 2) if np.random.random() > 0.4 else 0 for _ in range(n_rows)],
            'risk_rating': np.random.choice(['Low', 'Medium', 'High'], n_rows, p=[0.3, 0.5, 0.2]),
            'market_cap': [np.random.lognormal(20, 2) if i % 100 != 0 else None for i in range(n_rows)],
            'volume': [np.random.poisson(10000) if i % 110 != 0 else None for i in range(n_rows)]
        }
        
        df = pd.DataFrame(data)
        
        # Calculate derived fields
        df['total_value'] = df['current_price'] * df['quantity']
        df['gain_loss'] = (df['current_price'] - df['purchase_price']) * df['quantity']
        df['return_percentage'] = ((df['current_price'] - df['purchase_price']) / df['purchase_price']) * 100
        
        # Add data quality issues
        df = self._add_data_quality_issues(df)
        
        return df
    
    def _generate_name(self) -> str:
        """Generate realistic names"""
        first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'Robert', 'Lisa', 
                      'James', 'Maria', 'William', 'Jennifer', 'Richard', 'Patricia', 'Charles']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 
                     'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez']
        
        return f"{random.choice(first_names)} {random.choice(last_names)}"
    
    def _add_data_quality_issues(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add realistic data quality issues to simulate real-world data
        """
        # Add duplicates (5% of data)
        n_duplicates = int(len(df) * 0.05)
        duplicate_indices = np.random.choice(df.index, n_duplicates, replace=False)
        duplicates = df.loc[duplicate_indices].copy()
        df = pd.concat([df, duplicates], ignore_index=True)
        
        # Add format inconsistencies
        string_columns = df.select_dtypes(include=['object']).columns
        
        for col in string_columns:
            if col not in ['student_id', 'transaction_id', 'patient_id', 'asset_id']:
                # Random case changes
                mask = np.random.random(len(df)) < 0.1
                df.loc[mask, col] = df.loc[mask, col].astype(str).str.upper()
                
                # Add extra whitespace
                mask = np.random.random(len(df)) < 0.05
                df.loc[mask, col] = '  ' + df.loc[mask, col].astype(str) + '  '
        
        # Add some currency formatting issues
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if any(keyword in col.lower() for keyword in ['price', 'cost', 'revenue', 'salary', 'tuition']):
                mask = np.random.random(len(df)) < 0.1
                # Convert to object type first to avoid pandas type conflicts
                df[col] = df[col].astype('object')
                df.loc[mask, col] = '$' + df.loc[mask, col].astype(str)
        
        return df
    
    def save_sample_datasets(self, output_dir: str = "sample_data"):
        """
        Generate and save all sample datasets
        """
        import os
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        datasets = {
            'academic_data.csv': self.generate_academic_dataset(),
            'business_data.csv': self.generate_business_dataset(),
            'healthcare_data.csv': self.generate_healthcare_dataset(),
            'financial_data.csv': self.generate_financial_dataset()
        }
        
        for filename, dataset in datasets.items():
            filepath = os.path.join(output_dir, filename)
            dataset.to_csv(filepath, index=False)
            print(f"Generated {filename}: {len(dataset)} rows, {len(dataset.columns)} columns")
        
        print(f"\nAll sample datasets saved to '{output_dir}' directory")


def main():
    """Generate sample datasets for testing"""
    generator = SampleDataGenerator()
    
    print("Generating sample datasets...")
    generator.save_sample_datasets()
    
    print("\nSample datasets generated successfully!")
    print("You can now use these files to test the dashboard functionality.")


if __name__ == "__main__":
    main()