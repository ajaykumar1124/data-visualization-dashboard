"""
Setup Verification Script - Checks if all components are properly configured
"""

import os
import sys
import subprocess
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} NOT FOUND")
        return False

def check_directory_exists(dirpath, description):
    """Check if a directory exists"""
    if os.path.isdir(dirpath):
        print(f"✅ {description}: {dirpath}")
        return True
    else:
        print(f"❌ {description}: {dirpath} NOT FOUND")
        return False

def check_package_installed(package_name):
    """Check if a Python package is installed"""
    try:
        __import__(package_name)
        print(f"✅ Package installed: {package_name}")
        return True
    except ImportError:
        print(f"❌ Package NOT installed: {package_name}")
        return False

def main():
    print("=" * 60)
    print("🔍 Data Analytics Dashboard - Setup Verification")
    print("=" * 60)
    print()

    all_checks_passed = True

    # 1. Check core files
    print("📁 Checking core files...")
    print("-" * 60)
    core_files = {
        "dashboard.py": "Main Streamlit app",
        "data_pipeline.py": "Data cleaning pipeline",
        "visualization_engine.py": "Visualization engine",
        "powerpoint_generator.py": "PowerPoint reporter",
        "email_reporter.py": "Email reporter",
        "requirements.txt": "Python dependencies",
        "Procfile": "Deployment process file",
        "Dockerfile": "Docker configuration",
        "runtime.txt": "Python runtime version",
    }

    for filename, description in core_files.items():
        if not check_file_exists(filename, description):
            all_checks_passed = False

    print()

    # 2. Check directories
    print("📂 Checking directories...")
    print("-" * 60)
    directories = {
        "sample_data": "Sample data directory",
        ".streamlit": "Streamlit config directory",
        "backend": "Backend API directory (optional)",
    }

    for dirname, description in directories.items():
        if os.path.isdir(dirname):
            print(f"✅ {description}: {dirname}")
        else:
            print(f"⚠️  {description}: {dirname} (optional)")

    print()

    # 3. Check configuration files
    print("⚙️  Checking configuration files...")
    print("-" * 60)
    check_file_exists(".streamlit/config.toml", "Streamlit config")
    check_file_exists(".gitignore", "Git ignore")
    check_file_exists(".dockerignore", "Docker ignore")

    print()

    # 4. Check sample data
    print("📊 Checking sample data...")
    print("-" * 60)
    sample_files = [
        "sample_data/academic_data.csv",
        "sample_data/business_data.csv",
        "sample_data/financial_data.csv",
        "sample_data/healthcare_data.csv",
    ]

    for sample_file in sample_files:
        check_file_exists(sample_file, f"Sample data: {os.path.basename(sample_file)}")

    print()

    # 5. Check Python packages
    print("📦 Checking Python packages...")
    print("-" * 60)
    packages = [
        "streamlit",
        "pandas",
        "numpy",
        "plotly",
        "matplotlib",
        "seaborn",
        "openpyxl",
        "pptx",
        "slack_sdk",
    ]

    missing_packages = []
    for package in packages:
        if not check_package_installed(package):
            missing_packages.append(package)
            all_checks_passed = False

    print()

    # 6. Check Python version
    print("🐍 Checking Python version...")
    print("-" * 60)
    python_version = sys.version_info
    version_string = f"{python_version.major}.{python_version.minor}.{python_version.micro}"
    
    if python_version.major >= 3 and python_version.minor >= 11:
        print(f"✅ Python version: {version_string} (recommended)")
    else:
        print(f"⚠️  Python version: {version_string} (3.11+ recommended)")

    print()

    # 7. Summary
    print("=" * 60)
    print("📋 Verification Summary")
    print("=" * 60)

    if all_checks_passed and not missing_packages:
        print("✅ All checks passed! Your setup is ready.")
        print()
        print("🚀 To run the dashboard:")
        print("   streamlit run dashboard.py")
        print()
        print("📊 Open in browser: http://localhost:8501")
        return 0
    else:
        if missing_packages:
            print(f"❌ Missing packages: {', '.join(missing_packages)}")
            print()
            print("🔧 Install missing packages:")
            print(f"   pip install {' '.join(missing_packages)}")
            print()
        
        if not all_checks_passed:
            print("⚠️  Some files are missing or not configured properly.")
            print("    Please check the error messages above.")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
