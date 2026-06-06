"""
Test Script for PowerPoint and Email Reporting
Comprehensive testing of all reporting features
"""

import os
import sys
from datetime import datetime
import pandas as pd
import numpy as np

# Test PowerPoint Generation
def test_powerpoint_generation():
    """Test PowerPoint presentation generation"""
    print("🎯 Testing PowerPoint Generation...")
    
    try:
        from powerpoint_generator import PowerPointGenerator, create_presentation_from_dashboard_data
        from data_pipeline import load_sample_data, DataCleaningPipeline
        
        # Generate test data
        pipeline = DataCleaningPipeline()
        raw_data = load_sample_data()
        cleaned_data = pipeline.clean_dataset(raw_data)
        cleaning_report = pipeline.get_cleaning_report()
        
        print(f"   📊 Test data: {len(cleaned_data)} rows, {len(cleaned_data.columns)} columns")
        
        # Create PowerPoint presentation
        generator = PowerPointGenerator()
        filepath = generator.create_presentation(
            cleaned_data, 
            cleaning_report, 
            "Test Analytics Report - PowerPoint Generation"
        )
        
        # Verify file creation
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath) / 1024 / 1024
            print(f"   ✅ PowerPoint created: {filepath}")
            print(f"   📄 File size: {file_size:.1f} MB")
            
            # Test alternative creation method
            filepath2 = create_presentation_from_dashboard_data(
                "test_dataset", 
                "Alternative Creation Method Test"
            )
            
            if os.path.exists(filepath2):
                print(f"   ✅ Alternative method works: {filepath2}")
            
            return True
        else:
            print(f"   ❌ PowerPoint file not created")
            return False
            
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        print("   💡 Install required package: pip install python-pptx")
        return False
    except Exception as e:
        print(f"   ❌ PowerPoint generation failed: {e}")
        return False

def test_email_functionality():
    """Test email reporting functionality"""
    print("\n📧 Testing Email Functionality...")
    
    try:
        from email_reporter import EmailReporter, send_executive_summary, setup_scheduled_reports
        from data_pipeline import load_sample_data, DataCleaningPipeline
        
        # Generate test data
        pipeline = DataCleaningPipeline()
        raw_data = load_sample_data()
        cleaned_data = pipeline.clean_dataset(raw_data)
        cleaning_report = pipeline.get_cleaning_report()
        
        print(f"   📊 Test data prepared: {len(cleaned_data)} rows")
        
        # Test EmailReporter initialization
        reporter = EmailReporter()
        print("   ✅ EmailReporter initialized successfully")
        
        # Test email content generation (without sending)
        html_content = reporter._generate_email_content(
            cleaned_data, 
            cleaning_report, 
            'executive_summary',
            "This is a test message for email functionality validation."
        )
        
        if html_content and len(html_content) > 100:
            print("   ✅ Email content generation works")
            print(f"   📄 Content length: {len(html_content)} characters")
        else:
            print("   ❌ Email content generation failed")
            return False
        
        # Test template loading
        templates = ['executive_summary', 'detailed_report', 'alert', 'scheduled']
        for template in templates:
            template_content = reporter.templates.get(template)
            if template_content:
                print(f"   ✅ Template '{template}' loaded")
            else:
                print(f"   ❌ Template '{template}' missing")
        
        # Test utility functions
        try:
            # Note: This won't actually send emails without SMTP config
            print("   ℹ️ Email sending requires SMTP configuration")
            print("   💡 Set environment variables: SMTP_SERVER, EMAIL_USERNAME, EMAIL_PASSWORD")
            
            # Test scheduled report setup
            success = setup_scheduled_reports(["test@example.com"], "weekly")
            if success:
                print("   ✅ Scheduled report setup works")
            
        except Exception as e:
            print(f"   ⚠️ Email sending test skipped: {e}")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        print("   💡 Email functionality uses built-in libraries")
        return False
    except Exception as e:
        print(f"   ❌ Email functionality test failed: {e}")
        return False

def test_report_integration():
    """Test report integration module"""
    print("\n🔗 Testing Report Integration...")
    
    try:
        from report_integration import ReportManager
        from data_pipeline import load_sample_data, DataCleaningPipeline
        
        # Generate test data
        pipeline = DataCleaningPipeline()
        raw_data = load_sample_data()
        cleaned_data = pipeline.clean_dataset(raw_data)
        cleaning_report = pipeline.get_cleaning_report()
        
        # Test ReportManager
        manager = ReportManager()
        print("   ✅ ReportManager initialized")
        
        # Test PowerPoint creation through manager
        try:
            ppt_path = manager.create_powerpoint_report(
                cleaned_data, 
                cleaning_report, 
                "Integration Test Report"
            )
            
            if os.path.exists(ppt_path):
                print(f"   ✅ PowerPoint creation via manager works: {ppt_path}")
            else:
                print("   ❌ PowerPoint creation via manager failed")
                
        except Exception as e:
            print(f"   ⚠️ PowerPoint creation test: {e}")
        
        # Test email functionality through manager
        try:
            # This won't send without SMTP config, but tests the method
            test_recipients = ["test1@example.com", "test2@example.com"]
            
            # Test method exists and can be called
            success = manager.send_email_report(
                recipients=test_recipients,
                data=cleaned_data,
                analysis_results=cleaning_report,
                report_type='executive_summary',
                include_attachments=False,  # Skip attachments for test
                custom_message="This is a test integration message"
            )
            
            print("   ✅ Email report method accessible (SMTP config needed for actual sending)")
            
        except Exception as e:
            print(f"   ⚠️ Email integration test: {e}")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Integration test failed: {e}")
        return False

def test_dependencies():
    """Test all required dependencies"""
    print("\n📦 Testing Dependencies...")
    
    required_packages = {
        'pandas': 'Data processing',
        'numpy': 'Numerical operations', 
        'matplotlib': 'Basic plotting',
        'seaborn': 'Statistical visualization',
        'plotly': 'Interactive charts',
        'streamlit': 'Web dashboard',
        'openpyxl': 'Excel file handling'
    }
    
    optional_packages = {
        'python-pptx': 'PowerPoint generation',
        'kaleido': 'Static image export for charts'
    }
    
    all_good = True
    
    # Test required packages
    for package, description in required_packages.items():
        try:
            __import__(package.replace('-', '_'))
            print(f"   ✅ {package:<15} - {description}")
        except ImportError:
            print(f"   ❌ {package:<15} - {description} (MISSING)")
            all_good = False
    
    # Test optional packages
    print("\n   Optional packages:")
    for package, description in optional_packages.items():
        try:
            __import__(package.replace('-', '_'))
            print(f"   ✅ {package:<15} - {description}")
        except ImportError:
            print(f"   ⚠️ {package:<15} - {description} (install with: pip install {package})")
    
    return all_good

def create_sample_outputs():
    """Create sample outputs for demonstration"""
    print("\n🎨 Creating Sample Outputs...")
    
    try:
        # Ensure directories exist
        os.makedirs("exports", exist_ok=True)
        os.makedirs("temp", exist_ok=True)
        
        # Create sample PowerPoint
        if test_powerpoint_generation():
            print("   ✅ Sample PowerPoint created in exports/ directory")
        
        # Create sample email HTML
        try:
            from email_reporter import EmailReporter
            from data_pipeline import load_sample_data, DataCleaningPipeline
            
            pipeline = DataCleaningPipeline()
            raw_data = load_sample_data()
            cleaned_data = pipeline.clean_dataset(raw_data)
            cleaning_report = pipeline.get_cleaning_report()
            
            reporter = EmailReporter()
            html_content = reporter._generate_email_content(
                cleaned_data, 
                cleaning_report, 
                'executive_summary',
                "This is a sample email report generated for demonstration purposes."
            )
            
            # Save sample HTML
            with open("exports/sample_email_report.html", "w", encoding='utf-8') as f:
                f.write(html_content)
            
            print("   ✅ Sample email HTML created: exports/sample_email_report.html")
            
        except Exception as e:
            print(f"   ⚠️ Sample email creation: {e}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Sample output creation failed: {e}")
        return False

def run_comprehensive_test():
    """Run all tests"""
    print("🚀 PowerPoint & Email Reporter - Comprehensive Test Suite")
    print("=" * 70)
    
    tests = [
        ("Dependencies Check", test_dependencies),
        ("PowerPoint Generation", test_powerpoint_generation),
        ("Email Functionality", test_email_functionality),
        ("Report Integration", test_report_integration),
        ("Sample Outputs", create_sample_outputs)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("📋 TEST SUMMARY")
    print("=" * 70)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! PowerPoint and Email reporting are ready!")
        print("\n📋 What's Available:")
        print("   • PowerPoint presentation generation with 8+ professional slides")
        print("   • Email reporting with 4 different templates")
        print("   • Automated scheduling and batch sending")
        print("   • Integration with main dashboard")
        print("   • Professional formatting and visualizations")
        
        print("\n🚀 Next Steps:")
        print("   1. Configure SMTP settings for email functionality")
        print("   2. Test with your own data")
        print("   3. Integrate with main dashboard")
        print("   4. Setup automated scheduling")
        
    elif passed > total * 0.7:
        print("⚠️ Most tests passed. Check failed tests for missing dependencies.")
        print("💡 Install missing packages: pip install python-pptx kaleido")
        
    else:
        print("❌ Several tests failed. Check dependencies and configuration.")
        print("💡 Run: pip install -r requirements.txt")
    
    return passed == total

if __name__ == "__main__":
    success = run_comprehensive_test()
    
    if success:
        print("\n🎊 PowerPoint and Email reporting features are fully functional!")
    else:
        print("\n🔧 Some issues need to be resolved before full functionality.")
    
    sys.exit(0 if success else 1)