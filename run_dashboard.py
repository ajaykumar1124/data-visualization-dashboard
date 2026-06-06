"""
Dashboard Runner Script
Simplified script to launch the Streamlit dashboard
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'streamlit', 'pandas', 'matplotlib', 'seaborn', 
        'plotly', 'numpy', 'openpyxl'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Install missing packages with:")
        print("   pip install -r requirements.txt")
        return False
    
    print("✅ All required packages are installed!")
    return True

def generate_sample_data():
    """Generate sample data if it doesn't exist"""
    sample_dir = Path("sample_data")
    
    if not sample_dir.exists() or not any(sample_dir.glob("*.csv")):
        print("📊 Generating sample datasets...")
        try:
            from sample_data_generator import SampleDataGenerator
            generator = SampleDataGenerator()
            generator.save_sample_datasets()
            print("✅ Sample data generated successfully!")
        except Exception as e:
            print(f"⚠️ Could not generate sample data: {e}")
            print("   You can still upload your own data files.")

def launch_dashboard():
    """Launch the Streamlit dashboard"""
    print("🚀 Launching Data Analytics Dashboard...")
    print("📱 Dashboard will open in your default web browser")
    print("🔗 URL: http://localhost:8501")
    print("\n" + "="*50)
    print("Press Ctrl+C to stop the dashboard")
    print("="*50 + "\n")
    
    try:
        # Launch Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "dashboard.py",
            "--server.headless", "false",
            "--server.port", "8501",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped. Thank you for using the Analytics Dashboard!")
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")
        print("💡 Try running manually: streamlit run dashboard.py")

def main():
    """Main runner function"""
    print("🎯 Data Analytics & Visualization Dashboard")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("dashboard.py").exists():
        print("❌ dashboard.py not found in current directory")
        print("💡 Make sure you're in the project root directory")
        return
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Generate sample data
    generate_sample_data()
    
    # Launch dashboard
    launch_dashboard()

if __name__ == "__main__":
    main()