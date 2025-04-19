#!/bin/bash
# Enhanced Django project setup script

# Exit immediately if a command exits with a non-zero status
set -e

# Text colors for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Default configuration
DJANGO_PROJECT_NAME="core"
SUPERUSER_USERNAME="admin"
SUPERUSER_EMAIL="admin@example.com"
SUPERUSER_PASSWORD="admin123"
COLLECT_STATIC=true
RUN_TESTS=false
CREATE_SUPERUSER=true
LOAD_FIXTURES=false
FIXTURES_DIR="fixtures"
ENVIRONMENT="development"

# Display help information
function show_help {
    echo -e "${BLUE}Django Project Setup Script${NC}"
    echo -e "Usage: $0 [options]"
    echo
    echo "Options:"
    echo "  -h, --help                 Show this help message"
    echo "  -p, --project NAME         Set Django project name"
    echo "  -u, --username USERNAME    Set superuser username"
    echo "  -e, --email EMAIL          Set superuser email"
    echo "  --password PASSWORD        Set superuser password"
    echo "  --no-static                Skip collecting static files"
    echo "  --tests                    Run tests after setup"
    echo "  --no-superuser             Skip superuser creation"
    echo "  --fixtures                 Load fixtures from fixtures directory"
    echo "  --fixtures-dir DIR         Specify fixtures directory"
    echo "  --env ENVIRONMENT          Set environment (development, production, testing)"
    echo
}

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -p|--project)
            DJANGO_PROJECT_NAME="$2"
            shift 2
            ;;
        -u|--username)
            SUPERUSER_USERNAME="$2"
            shift 2
            ;;
        -e|--email)
            SUPERUSER_EMAIL="$2"
            shift 2
            ;;
        --password)
            SUPERUSER_PASSWORD="$2"
            shift 2
            ;;
        --no-static)
            COLLECT_STATIC=false
            shift
            ;;
        --tests)
            RUN_TESTS=true
            shift
            ;;
        --no-superuser)
            CREATE_SUPERUSER=false
            shift
            ;;
        --fixtures)
            LOAD_FIXTURES=true
            shift
            ;;
        --fixtures-dir)
            FIXTURES_DIR="$2"
            shift 2
            ;;
        --env)
            ENVIRONMENT="$2"
            shift 2
            ;;
        *)
            echo -e "${RED}Error: Unknown option $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Display configuration summary
echo -e "${BLUE}=== Django Setup Configuration ===${NC}"
echo -e "Project: ${YELLOW}$DJANGO_PROJECT_NAME${NC}"
echo -e "Environment: ${YELLOW}$ENVIRONMENT${NC}"
echo -e "Create superuser: ${YELLOW}$CREATE_SUPERUSER${NC}"
echo -e "Collect static: ${YELLOW}$COLLECT_STATIC${NC}"
echo -e "Run tests: ${YELLOW}$RUN_TESTS${NC}"
echo -e "Load fixtures: ${YELLOW}$LOAD_FIXTURES${NC}"
echo

# Check for Django installation
if ! command -v python -c "import django" &> /dev/null; then
    echo -e "${RED}⚠️ Django is not installed or not in PYTHONPATH.${NC}"
    read -p "Would you like to install Django now? (y/n): " install_django
    if [[ $install_django == "y" || $install_django == "Y" ]]; then
        echo -e "${YELLOW}📦 Installing Django...${NC}"
        pip install django
    else
        echo -e "${RED}Exiting script as Django is required.${NC}"
        exit 1
    fi
fi

# Check if manage.py exists
if [ ! -f "manage.py" ]; then
    echo -e "${RED}⚠️ manage.py not found in current directory.${NC}"
    echo -e "${YELLOW}Make sure you're in the Django project root directory.${NC}"
    exit 1
fi

# Set environment variables if needed
if [ "$ENVIRONMENT" == "production" ]; then
    export DJANGO_SETTINGS_MODULE="${DJANGO_PROJECT_NAME}.settings.production"
    echo -e "${YELLOW}📢 Using production settings${NC}"
elif [ "$ENVIRONMENT" == "testing" ]; then
    export DJANGO_SETTINGS_MODULE="${DJANGO_PROJECT_NAME}.settings.testing"
    echo -e "${YELLOW}📢 Using testing settings${NC}"
else
    export DJANGO_SETTINGS_MODULE="${DJANGO_PROJECT_NAME}.settings.development"
    echo -e "${YELLOW}📢 Using development settings${NC}"
fi

# With this simplified version:
export DJANGO_SETTINGS_MODULE="${DJANGO_PROJECT_NAME}.settings"
echo -e "${YELLOW}📢 Using default settings${NC}"

# Create database directory if using SQLite
if [ -f "${DJANGO_PROJECT_NAME}/settings.py" ]; then
    DB_ENGINE=$(python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', '${DJANGO_PROJECT_NAME}.settings'); import django; django.setup(); from django.conf import settings; print(settings.DATABASES['default']['ENGINE'])")
    
    if [[ $DB_ENGINE == *"sqlite3"* ]]; then
        DB_DIR=$(dirname $(python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', '${DJANGO_PROJECT_NAME}.settings'); import django; django.setup(); from django.conf import settings; print(settings.DATABASES['default']['NAME'])"))
        
        if [ ! -d "$DB_DIR" ]; then
            echo -e "${YELLOW}📁 Creating database directory...${NC}"
            mkdir -p "$DB_DIR"
        fi
    fi
fi

# Backup database if one exists
if [ -f "db.sqlite3" ]; then
    BACKUP_NAME="db_backup_$(date +%Y%m%d_%H%M%S).sqlite3"
    echo -e "${YELLOW}💾 Creating database backup: $BACKUP_NAME${NC}"
    cp db.sqlite3 "$BACKUP_NAME"
fi

# Check for pending migrations before applying
echo -e "${BLUE}🔍 Checking for pending migrations...${NC}"
PENDING_MIGRATIONS=$(python manage.py showmigrations --list | grep -c "\[ \]" || true)
if [ "$PENDING_MIGRATIONS" -gt 0 ]; then
    echo -e "${YELLOW}Found $PENDING_MIGRATIONS pending migrations to apply.${NC}"
else
    echo -e "${GREEN}No pending migrations.${NC}"
fi

# Make and apply migrations
echo -e "${BLUE}🔄 Running makemigrations...${NC}"
python manage.py makemigrations --no-input

echo -e "${BLUE}✅ Applying migrations...${NC}"
python manage.py migrate --no-input

# Create superuser if requested
if [ "$CREATE_SUPERUSER" = true ]; then
    echo -e "${BLUE}👤 Creating superuser...${NC}"
    # Use Django shell to create superuser non-interactively
    python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$SUPERUSER_USERNAME').exists():
    User.objects.create_superuser(
        username='$SUPERUSER_USERNAME',
        email='$SUPERUSER_EMAIL',
        password='$SUPERUSER_PASSWORD'
    )
    print("${GREEN}✅ Superuser created successfully.${NC}")
else:
    print("${YELLOW}⚠️  Superuser already exists.${NC}")
EOF
fi

# Collect static files if requested
if [ "$COLLECT_STATIC" = true ]; then
    echo -e "${BLUE}📦 Collecting static files...${NC}"
    python manage.py collectstatic --no-input --clear
fi

# Load fixtures if requested
if [ "$LOAD_FIXTURES" = true ]; then
    if [ -d "$FIXTURES_DIR" ]; then
        echo -e "${BLUE}📚 Loading fixtures from $FIXTURES_DIR...${NC}"
        for fixture in "$FIXTURES_DIR"/*.json; do
            if [ -f "$fixture" ]; then
                echo -e "${YELLOW}Loading fixture: $(basename "$fixture")${NC}"
                python manage.py loaddata "$fixture"
            fi
        done
    else
        echo -e "${YELLOW}⚠️ Fixtures directory $FIXTURES_DIR not found.${NC}"
    fi
fi

# Run tests if requested
if [ "$RUN_TESTS" = true ]; then
    echo -e "${BLUE}🧪 Running tests...${NC}"
    python manage.py test
fi

# Check and report on installed apps
echo -e "${BLUE}📊 Project Summary${NC}"
INSTALLED_APPS=$(python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', '${DJANGO_PROJECT_NAME}.settings'); import django; django.setup(); from django.conf import settings; print('\n'.join(settings.INSTALLED_APPS))")
echo -e "${YELLOW}Installed apps:${NC}"
echo "$INSTALLED_APPS" | while read app; do
    echo -e "  - $app"
done

echo -e "\n${GREEN}✅ Django setup completed successfully!${NC}"
echo -e "${BLUE}You can now run the development server with:${NC}"
echo -e "  python manage.py runserver"

# If superuser was created, show login info
if [ "$CREATE_SUPERUSER" = true ]; then
    echo -e "\n${BLUE}Admin login details:${NC}"
    echo -e "  URL: http://127.0.0.1:8000/admin/"
    echo -e "  Username: ${YELLOW}$SUPERUSER_USERNAME${NC}"
    echo -e "  Password: ${YELLOW}$SUPERUSER_PASSWORD${NC}"
fi