"""
Test Script for Data Analytics Dashboard
Validates all components work correctly
"""

import sys
import traceback
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import pandas as pd
        import numpy as np
        import matplotlib.pyplot as plt
        import seaborn as sns
        import plotly.express as px
        import plotly.graph_objects as go
        print("✅ Core libraries imported successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    try:
        from data_pipeline import DataCleaningPipeline, load_sample_data
        from visualization_engine import VisualizationEngine
        from sample_data_generator import SampleDataGenerator
        print("✅ Custom modules imported successfully")
    except ImportError as e:
        print(f"❌ Custom module import error: {e}")
        return False
    
    return True

def test_data_pipeline():
    """Test the data cleaning pipeline"""
    print("\n🧹 Testing data cleaning pipeline...")
    
    try:
        from data_pipeline import DataCleaningPipeline, load_sample_data
        
        # Initialize pipeline
        pipeline = DataCleaningPipeline()
        
        # Load sample data
        raw_data = load_sample_data()
        print(f"   📊 Generated sample data: {len(raw_data)} rows, {len(raw_data.columns)} columns")
        
        # Clean the data
        cleaned_data = pipeline.clean_dataset(raw_data)
        print(f"   🔧 Cleaned data: {len(cleaned_data)} rows, {len(cleaned_data.columns)} columns")
        
        # Get cleaning report
        report = pipeline.get_cleaning_report()
        print(f"   📈 Cleaning accuracy: {report['accuracy_score']:.1%}")
        
        print("✅ Data pipeline test passed")
        return True
        
    except Exception as e:
        print(f"❌ Data pipeline test failed: {e}")
        traceback.print_exc()
        return False

def test_visualization_engine():
    """Test the visualization engine"""
    print("\n📊 Testing visualization engine...")
    
    try:
        from visualization_engine import VisualizationEngine, create_sample_visualizations
        
        # Create sample visualizations
        charts, engine = create_sample_visualizations()
        
        print(f"   📈 Created {len(charts)} visualization types:")
        for chart_type in charts.keys():
            print(f"      - {chart_type.title()} Chart")
        
        print("✅ Visualization engine test passed")
        return True
        
    except Exception as e:
        print(f"❌ Visualization engine test failed: {e}")
        traceback.print_exc()
        return False

def test_sample_data_generator():
    """Test the sample data generator"""
    print("\n🎲 Testing sample data generator...")
    
    try:
        from sample_data_generator import SampleDataGenerator
        
        generator = SampleDataGenerator()
        
        # Test different dataset types
        datasets = {
            'academic': generator.generate_academic_dataset(1000),
            'business': generator.generate_business_dataset(1000),
            'healthcare': generator.generate_healthcare_dataset(1000),
            'financial': generator.generate_financial_dataset(1000)
        }
        
        for name, dataset in datasets.items():
            print(f"   📋 {name.title()} dataset: {len(dataset)} rows, {len(dataset.columns)} columns")
        
        print("✅ Sample data generator test passed")
        return True
        
    except Exception as e:
        print(f"❌ Sample data generator test failed: {e}")
        traceback.print_exc()
        return False

def test_config():
    """Test configuration system"""
    print("\n⚙️ Testing configuration system...")
    
    try:
        from config import config, apply_preset, get_available_presets
        
        # Test default config
        print(f"   🔧 Default missing threshold: {config.data_processing.missing_value_threshold}")
        print(f"   🎨 Default color palette: {len(config.visualization.color_palette)} colors")
        
        # Test presets
        presets = get_available_presets()
        print(f"   📋 Available presets: {', '.join(presets)}")
        
        # Test applying a preset
        apply_preset('academic')
        print(f"   ✅ Applied academic preset")
        
        print("✅ Configuration system test passed")
        return True
        
    except Exception as e:
        print(f"❌ Configuration system test failed: {e}")
        traceback.print_exc()
        return False

def test_file_structure():
    """Test if all required files exist"""
    print("\n📁 Testing file structure...")
    
    required_files = [
        'dashboard.py',
        'data_pipeline.py',
        'visualization_engine.py',
        'sample_data_generator.py',
        'config.py',
        'requirements.txt',
        'README.md'
    ]
    
    missing_files = []
    
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
        else:
            print(f"   ✅ {file}")
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files present")
    return True

def run_comprehensive_test():
    """Run all tests"""
    print("🚀 Data Analytics Dashboard - Comprehensive Test Suite")
    print("=" * 60)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Imports", test_imports),
        ("Data Pipeline", test_data_pipeline),
        ("Visualization Engine", test_visualization_engine),
        ("Sample Data Generator", test_sample_data_generator),
        ("Configuration System", test_config)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Dashboard is ready to use.")
        print("\n🚀 To start the dashboard, run:")
        print("   python run_dashboard.py")
        print("   or")
        print("   streamlit run dashboard.py")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        print("💡 Make sure all dependencies are installed:")
        print("   pip install -r requirements.txt")
    
    return passed == total

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)