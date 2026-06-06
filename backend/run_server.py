"""
Server Runner Script
Easy way to start the FastAPI backend server
"""

import uvicorn
import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'fastapi', 'uvicorn', 'pandas', 'sqlalchemy', 
        'python-jose', 'passlib', 'python-multipart'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
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

def setup_environment():
    """Setup environment variables and directories"""
    
    # Set default environment variables if not set
    env_vars = {
        'DATABASE_URL': 'sqlite:///./analytics_dashboard.db',
        'SECRET_KEY': 'your-secret-key-change-in-production',
        'ENVIRONMENT': 'development'
    }
    
    for key, default_value in env_vars.items():
        if key not in os.environ:
            os.environ[key] = default_value
    
    # Create necessary directories
    directories = ['uploads', 'exports', 'temp', 'logs']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("✅ Environment setup completed!")

def initialize_database():
    """Initialize database with tables and default data"""
    try:
        from database import init_database
        init_database()
        print("✅ Database initialized successfully!")
    except Exception as e:
        print(f"⚠️ Database initialization warning: {e}")
        print("   The server will still start, but some features may not work.")

def start_server(host="0.0.0.0", port=8000, reload=True, log_level="info"):
    """Start the FastAPI server"""
    
    print("🚀 Starting Data Analytics Dashboard API Server...")
    print(f"📱 Server will be available at: http://{host}:{port}")
    print(f"📚 API Documentation: http://{host}:{port}/docs")
    print(f"📖 Alternative Docs: http://{host}:{port}/redoc")
    print("\n" + "="*60)
    print("Press Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    try:
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=reload,
            log_level=log_level,
            access_log=True,
            reload_dirs=[".", "../"] if reload else None
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Thank you for using the Analytics Dashboard API!")
    except Exception as e:
        print(f"❌ Server error: {e}")
        print("💡 Try checking the logs or running with --debug flag")

def main():
    """Main runner function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Data Analytics Dashboard API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--no-reload", action="store_true", help="Disable auto-reload")
    parser.add_argument("--log-level", default="info", help="Log level")
    parser.add_argument("--production", action="store_true", help="Run in production mode")
    parser.add_argument("--skip-checks", action="store_true", help="Skip dependency checks")
    
    args = parser.parse_args()
    
    print("🎯 Data Analytics Dashboard API Server")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("❌ main.py not found in current directory")
        print("💡 Make sure you're in the backend directory")
        return
    
    # Check dependencies
    if not args.skip_checks and not check_dependencies():
        return
    
    # Setup environment
    setup_environment()
    
    # Initialize database
    if not args.skip_checks:
        initialize_database()
    
    # Production mode adjustments
    if args.production:
        args.no_reload = True
        args.log_level = "warning"
        os.environ['ENVIRONMENT'] = 'production'
        print("🏭 Running in production mode")
    
    # Start server
    start_server(
        host=args.host,
        port=args.port,
        reload=not args.no_reload,
        log_level=args.log_level
    )

if __name__ == "__main__":
    main()