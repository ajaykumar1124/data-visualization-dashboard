#!/bin/bash

# Data Analytics Dashboard Deployment Script
# Automated deployment for development and production environments

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="data-analytics-dashboard"
ENVIRONMENT=${1:-development}
DOCKER_COMPOSE_FILE="docker-compose.yml"

echo -e "${BLUE}🚀 Data Analytics Dashboard Deployment${NC}"
echo -e "${BLUE}Environment: ${ENVIRONMENT}${NC}"
echo "=================================================="

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    echo "🔍 Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check if Docker is running
    if ! docker info &> /dev/null; then
        print_error "Docker is not running"
        exit 1
    fi
    
    print_status "Prerequisites check passed"
}

# Setup environment
setup_environment() {
    echo "⚙️  Setting up environment..."
    
    # Create environment file if it doesn't exist
    if [ ! -f .env ]; then
        echo "Creating .env file..."
        cat > .env << EOF
# Environment Configuration
ENVIRONMENT=${ENVIRONMENT}

# Database
POSTGRES_DB=analytics_dashboard
POSTGRES_USER=analytics
POSTGRES_PASSWORD=analytics123
DATABASE_URL=postgresql://analytics:analytics123@postgres:5432/analytics_dashboard

# Security
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)

# API Configuration
MAX_FILE_SIZE_MB=200
RATE_LIMIT_PER_HOUR=100

# Frontend Configuration
BACKEND_URL=http://backend:8000
STREAMLIT_SERVER_PORT=8501

# Redis
REDIS_URL=redis://redis:6379/0
EOF
        print_status "Environment file created"
    else
        print_warning "Environment file already exists"
    fi
    
    # Create necessary directories
    mkdir -p uploads exports temp logs nginx/ssl sample_data
    print_status "Directories created"
}

# Build and start services
deploy_services() {
    echo "🏗️  Building and deploying services..."
    
    # Pull latest images
    echo "Pulling base images..."
    docker-compose pull postgres redis nginx
    
    # Build custom images
    echo "Building application images..."
    docker-compose build --no-cache
    
    # Start services
    echo "Starting services..."
    docker-compose up -d
    
    print_status "Services deployed"
}

# Wait for services to be ready
wait_for_services() {
    echo "⏳ Waiting for services to be ready..."
    
    # Wait for database
    echo "Waiting for PostgreSQL..."
    until docker-compose exec -T postgres pg_isready -U analytics -d analytics_dashboard; do
        sleep 2
    done
    
    # Wait for Redis
    echo "Waiting for Redis..."
    until docker-compose exec -T redis redis-cli ping; do
        sleep 2
    done
    
    # Wait for backend
    echo "Waiting for backend API..."
    until curl -f http://localhost:8000/health &> /dev/null; do
        sleep 5
    done
    
    # Wait for frontend
    echo "Waiting for frontend dashboard..."
    until curl -f http://localhost:8501 &> /dev/null; do
        sleep 5
    done
    
    print_status "All services are ready"
}

# Initialize database
initialize_database() {
    echo "🗄️  Initializing database..."
    
    # Run database migrations
    docker-compose exec backend python -c "from database import init_database; init_database()"
    
    print_status "Database initialized"
}

# Generate sample data
generate_sample_data() {
    echo "📊 Generating sample data..."
    
    # Generate sample datasets
    docker-compose exec backend python -c "
from sample_data_generator import SampleDataGenerator
generator = SampleDataGenerator()
generator.save_sample_datasets('sample_data')
print('Sample data generated successfully')
"
    
    print_status "Sample data generated"
}

# Run tests
run_tests() {
    echo "🧪 Running tests..."
    
    # Test backend API
    docker-compose exec backend python test_api.py --quick
    
    # Test frontend (basic health check)
    if curl -f http://localhost:8501/_stcore/health &> /dev/null; then
        print_status "Frontend health check passed"
    else
        print_warning "Frontend health check failed"
    fi
    
    print_status "Tests completed"
}

# Show deployment status
show_status() {
    echo ""
    echo "📋 Deployment Status"
    echo "=================================================="
    
    # Show running containers
    docker-compose ps
    
    echo ""
    echo "🔗 Access URLs:"
    echo "  📊 Dashboard:     http://localhost:8501"
    echo "  🔧 API Server:    http://localhost:8000"
    echo "  📚 API Docs:      http://localhost:8000/docs"
    echo "  📖 Alternative:   http://localhost:8000/redoc"
    echo "  ❤️  Health Check: http://localhost:8000/health"
    
    if [ "$ENVIRONMENT" = "production" ]; then
        echo "  🌐 Nginx Proxy:  http://localhost"
    fi
    
    echo ""
    echo "🗄️  Database:"
    echo "  Host: localhost:5432"
    echo "  Database: analytics_dashboard"
    echo "  User: analytics"
    
    echo ""
    echo "📊 Sample Data:"
    echo "  Location: ./sample_data/"
    echo "  Types: Academic, Business, Healthcare, Financial"
    
    print_status "Deployment completed successfully!"
}

# Cleanup function
cleanup() {
    echo "🧹 Cleaning up..."
    docker-compose down
    docker system prune -f
    print_status "Cleanup completed"
}

# Main deployment flow
main() {
    case "${1:-deploy}" in
        "deploy")
            check_prerequisites
            setup_environment
            deploy_services
            wait_for_services
            initialize_database
            generate_sample_data
            run_tests
            show_status
            ;;
        "start")
            docker-compose up -d
            wait_for_services
            show_status
            ;;
        "stop")
            docker-compose down
            print_status "Services stopped"
            ;;
        "restart")
            docker-compose restart
            wait_for_services
            show_status
            ;;
        "logs")
            docker-compose logs -f
            ;;
        "status")
            docker-compose ps
            ;;
        "cleanup")
            cleanup
            ;;
        "test")
            run_tests
            ;;
        *)
            echo "Usage: $0 {deploy|start|stop|restart|logs|status|cleanup|test}"
            echo ""
            echo "Commands:"
            echo "  deploy   - Full deployment (default)"
            echo "  start    - Start existing services"
            echo "  stop     - Stop all services"
            echo "  restart  - Restart all services"
            echo "  logs     - Show service logs"
            echo "  status   - Show service status"
            echo "  cleanup  - Stop and clean up"
            echo "  test     - Run tests"
            exit 1
            ;;
    esac
}

# Handle script interruption
trap cleanup INT TERM

# Run main function
main "$@"