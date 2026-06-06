"""
API Testing Script
Comprehensive tests for the Data Analytics Dashboard API
"""

import requests
import json
import time
import os
from pathlib import Path
import pandas as pd
import io

class APITester:
    """Test suite for the Analytics Dashboard API"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.access_token = None
        self.test_user_id = None
        self.test_dataset_id = None
        
    def test_health_check(self):
        """Test health check endpoint"""
        print("🔍 Testing health check...")
        
        try:
            response = self.session.get(f"{self.base_url}/health")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Health check passed: {data['status']}")
                return True
            else:
                print(f"   ❌ Health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Health check error: {e}")
            return False
    
    def test_api_info(self):
        """Test API info endpoint"""
        print("📋 Testing API info...")
        
        try:
            response = self.session.get(f"{self.base_url}/info")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ API info retrieved: {data['api']['name']}")
                print(f"   📊 Features: {len(data['features'])} categories")
                return True
            else:
                print(f"   ❌ API info failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ API info error: {e}")
            return False
    
    def test_user_registration(self):
        """Test user registration"""
        print("👤 Testing user registration...")
        
        try:
            user_data = {
                "username": f"testuser_{int(time.time())}",
                "email": f"test_{int(time.time())}@example.com",
                "password": "testpassword123",
                "full_name": "Test User",
                "organization": "Test Organization"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/register",
                params=user_data
            )
            
            if response.status_code == 200:
                data = response.json()
                self.test_user_id = data['user']['id']
                print(f"   ✅ User registered: {data['user']['username']}")
                return True, user_data
            else:
                print(f"   ❌ Registration failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False, None
                
        except Exception as e:
            print(f"   ❌ Registration error: {e}")
            return False, None
    
    def test_user_login(self, user_data):
        """Test user login"""
        print("🔐 Testing user login...")
        
        try:
            login_data = {
                "username": user_data["username"],
                "password": user_data["password"]
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                params=login_data
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data['access_token']
                
                # Set authorization header for future requests
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}'
                })
                
                print(f"   ✅ Login successful: {data['user']['username']}")
                return True
            else:
                print(f"   ❌ Login failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Login error: {e}")
            return False
    
    def test_user_info(self):
        """Test getting current user info"""
        print("👤 Testing user info retrieval...")
        
        try:
            response = self.session.get(f"{self.base_url}/api/v1/auth/me")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ User info retrieved: {data['username']}")
                return True
            else:
                print(f"   ❌ User info failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ User info error: {e}")
            return False
    
    def create_test_csv(self):
        """Create a test CSV file for upload"""
        # Generate sample data
        data = {
            'id': range(1, 101),
            'name': [f'Item_{i}' for i in range(1, 101)],
            'value': [i * 10 + (i % 7) for i in range(1, 101)],
            'category': ['A', 'B', 'C'] * 33 + ['A'],
            'date': pd.date_range('2024-01-01', periods=100, freq='D')
        }
        
        df = pd.DataFrame(data)
        
        # Save to CSV
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_content = csv_buffer.getvalue()
        
        return csv_content.encode('utf-8')
    
    def test_data_upload(self):
        """Test data file upload"""
        print("📁 Testing data upload...")
        
        try:
            # Create test CSV
            csv_content = self.create_test_csv()
            
            files = {
                'file': ('test_data.csv', csv_content, 'text/csv')
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/data/upload",
                files=files
            )
            
            if response.status_code == 200:
                data = response.json()
                self.test_dataset_id = data['id']
                print(f"   ✅ Data uploaded: {data['rows_count']} rows, {data['columns_count']} columns")
                return True
            else:
                print(f"   ❌ Upload failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Upload error: {e}")
            return False
    
    def test_data_processing(self):
        """Test data processing"""
        print("🔄 Testing data processing...")
        
        if not self.test_dataset_id:
            print("   ⚠️ No dataset to process")
            return False
        
        try:
            processing_config = {
                "remove_outliers": False,
                "missing_threshold": 0.5
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/data/process/{self.test_dataset_id}",
                json=processing_config
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Data processed: {data['cleaning_report']['accuracy_score']:.1%} accuracy")
                return True
            else:
                print(f"   ❌ Processing failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Processing error: {e}")
            return False
    
    def test_dataset_list(self):
        """Test listing datasets"""
        print("📋 Testing dataset listing...")
        
        try:
            response = self.session.get(f"{self.base_url}/api/v1/data/datasets")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Datasets listed: {len(data)} datasets")
                return True
            else:
                print(f"   ❌ Dataset listing failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Dataset listing error: {e}")
            return False
    
    def test_dataset_preview(self):
        """Test dataset preview"""
        print("👀 Testing dataset preview...")
        
        if not self.test_dataset_id:
            print("   ⚠️ No dataset to preview")
            return False
        
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/data/datasets/{self.test_dataset_id}/preview"
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Preview retrieved: {len(data['preview'])} rows shown")
                return True
            else:
                print(f"   ❌ Preview failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Preview error: {e}")
            return False
    
    def test_visualization_creation(self):
        """Test visualization creation"""
        print("📊 Testing visualization creation...")
        
        if not self.test_dataset_id:
            print("   ⚠️ No dataset for visualization")
            return False
        
        try:
            viz_config = {
                "viz_type": "distribution",
                "title": "Test Distribution Chart",
                "description": "Test visualization",
                "config": {
                    "column": "value"
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/visualizations/create/{self.test_dataset_id}",
                json=viz_config
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Visualization created: {data['title']}")
                return True
            else:
                print(f"   ❌ Visualization failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Visualization error: {e}")
            return False
    
    def test_export_creation(self):
        """Test export job creation"""
        print("📤 Testing export creation...")
        
        if not self.test_dataset_id:
            print("   ⚠️ No dataset to export")
            return False
        
        try:
            export_config = {
                "export_format": "csv",
                "export_config": {
                    "include_report": True
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/export/create/{self.test_dataset_id}",
                json=export_config
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Export job created: {data['export_format']} format")
                return True
            else:
                print(f"   ❌ Export failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Export error: {e}")
            return False
    
    def run_comprehensive_test(self):
        """Run all tests"""
        print("🚀 Data Analytics Dashboard API - Comprehensive Test Suite")
        print("=" * 70)
        
        tests = [
            ("Health Check", self.test_health_check),
            ("API Info", self.test_api_info),
            ("User Registration", lambda: self.test_user_registration()[0]),
            ("User Login", lambda: self.test_user_login(self.user_data) if hasattr(self, 'user_data') else False),
            ("User Info", self.test_user_info),
            ("Data Upload", self.test_data_upload),
            ("Data Processing", self.test_data_processing),
            ("Dataset List", self.test_dataset_list),
            ("Dataset Preview", self.test_dataset_preview),
            ("Visualization Creation", self.test_visualization_creation),
            ("Export Creation", self.test_export_creation)
        ]
        
        results = []
        
        # Special handling for registration and login
        reg_success, self.user_data = self.test_user_registration()
        results.append(("User Registration", reg_success))
        
        if reg_success and self.user_data:
            login_success = self.test_user_login(self.user_data)
            results.append(("User Login", login_success))
            
            if login_success:
                # Run remaining tests
                for test_name, test_func in tests[2:]:
                    try:
                        result = test_func()
                        results.append((test_name, result))
                    except Exception as e:
                        print(f"❌ {test_name} crashed: {e}")
                        results.append((test_name, False))
            else:
                # Skip tests that require authentication
                for test_name, _ in tests[2:]:
                    results.append((test_name, False))
        else:
            # Skip all tests if registration failed
            for test_name, _ in tests[1:]:
                results.append((test_name, False))
        
        # Summary
        print("\n" + "=" * 70)
        print("📋 TEST SUMMARY")
        print("=" * 70)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name:<30} {status}")
            if result:
                passed += 1
        
        print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! API is working correctly.")
        elif passed > total * 0.7:
            print("⚠️ Most tests passed. Check failed tests for issues.")
        else:
            print("❌ Many tests failed. Check server status and configuration.")
        
        return passed == total

def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="API Test Suite")
    parser.add_argument("--url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--quick", action="store_true", help="Run quick tests only")
    
    args = parser.parse_args()
    
    # Check if server is running
    try:
        response = requests.get(f"{args.url}/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ Server not responding correctly at {args.url}")
            print("💡 Make sure the API server is running:")
            print("   python run_server.py")
            return
    except requests.exceptions.RequestException:
        print(f"❌ Cannot connect to server at {args.url}")
        print("💡 Make sure the API server is running:")
        print("   python run_server.py")
        return
    
    # Run tests
    tester = APITester(args.url)
    
    if args.quick:
        # Quick tests only
        success = (
            tester.test_health_check() and
            tester.test_api_info()
        )
        print(f"\n🎯 Quick test result: {'✅ PASSED' if success else '❌ FAILED'}")
    else:
        # Full test suite
        success = tester.run_comprehensive_test()
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)