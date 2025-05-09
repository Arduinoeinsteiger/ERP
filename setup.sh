#!/bin/bash
# SwissAirDry - Setup Script
# This script helps with initial setup of the SwissAirDry platform

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}       SwissAirDry Platform Setup          ${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Check for required commands
check_command() {
    command -v $1 >/dev/null 2>&1 || { 
        echo -e "${RED}Error: $1 is required but not installed.${NC}" 
        echo "Please install $1 and try again."
        exit 1
    }
}

echo -e "${YELLOW}Checking for required commands...${NC}"
check_command docker
check_command docker-compose
check_command git
echo -e "${GREEN}All required commands are available.${NC}"
echo ""

# Setup environment file
setup_env() {
    if [ -f .env ]; then
        echo -e "${YELLOW}An .env file already exists.${NC}"
        read -p "Do you want to overwrite it? (y/N): " overwrite
        if [[ $overwrite =~ ^[Yy]$ ]]; then
            cp .env.example .env
            echo -e "${GREEN}.env file has been reset from example.${NC}"
        else
            echo -e "${BLUE}Keeping existing .env file.${NC}"
        fi
    else
        cp .env.example .env
        echo -e "${GREEN}.env file created from example.${NC}"
    fi
    
    echo -e "${YELLOW}Generating secure secret key...${NC}"
    # Generate a random secret key and update .env
    SECRET_KEY=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)
    sed -i "s/FLASK_SECRET_KEY=.*/FLASK_SECRET_KEY=$SECRET_KEY/" .env
    
    # Generate a random ExApp secret and update .env
    EXAPP_SECRET=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)
    sed -i "s/EXAPP_SECRET=.*/EXAPP_SECRET=$EXAPP_SECRET/" .env
    
    echo -e "${GREEN}Secret keys updated.${NC}"
    echo ""
}

# Check if requirements.txt exists in backup/attached_assets
check_requirements() {
    if [ ! -f backup/attached_assets/requirements.txt ]; then
        echo -e "${YELLOW}requirements.txt not found in backup/attached_assets directory.${NC}"
        echo -e "${BLUE}Creating directory structure...${NC}"
        mkdir -p backup/attached_assets
        
        if [ -f requirements.txt ]; then
            cp requirements.txt backup/attached_assets/
            echo -e "${GREEN}requirements.txt copied to backup/attached_assets/.${NC}"
        else
            echo -e "${YELLOW}Creating requirements.txt from example...${NC}"
            cat > backup/attached_assets/requirements.txt << EOL
Flask>=2.3.3
flask-cors>=4.0.0
requests>=2.31.0
paho-mqtt>=2.2.1
python-dotenv>=1.0.0
gunicorn>=22.0.0
psycopg2-binary>=2.9.9
jinja2>=3.1.3
email-validator>=2.0.0
flask-sqlalchemy>=3.0.5
bleak>=0.21.1
EOL
            echo -e "${GREEN}requirements.txt created in backup/attached_assets/.${NC}"
        fi
    else
        echo -e "${GREEN}requirements.txt already exists in backup/attached_assets/.${NC}"
    fi
    echo ""
}

# Build and start the containers
start_containers() {
    echo -e "${BLUE}Building and starting Docker containers...${NC}"
    docker-compose build
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Docker build completed successfully.${NC}"
        echo -e "${BLUE}Starting containers...${NC}"
        docker-compose up -d
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}Docker containers started successfully.${NC}"
        else
            echo -e "${RED}Error starting Docker containers.${NC}"
            exit 1
        fi
    else
        echo -e "${RED}Docker build failed.${NC}"
        exit 1
    fi
    echo ""
}

# Check container status
check_status() {
    echo -e "${BLUE}Checking container status...${NC}"
    docker-compose ps
    echo ""
    
    echo -e "${BLUE}SwissAirDry Platform should now be available at:${NC}"
    echo -e "${GREEN}http://localhost:5000${NC}"
    echo ""
}

# Main execution
setup_env
check_requirements

echo -e "${YELLOW}Do you want to build and start the containers now? (y/N)${NC}"
read -p "> " start_now
if [[ $start_now =~ ^[Yy]$ ]]; then
    start_containers
    check_status
    
    echo -e "${BLUE}============================================${NC}"
    echo -e "${GREEN}SwissAirDry Platform setup is complete!${NC}"
    echo -e "${BLUE}============================================${NC}"
    echo ""
    echo -e "Use the following commands to manage the system:"
    echo -e "  ${YELLOW}docker-compose up -d${NC}    - Start all services"
    echo -e "  ${YELLOW}docker-compose down${NC}     - Stop all services"
    echo -e "  ${YELLOW}docker-compose logs -f${NC}  - View service logs"
    echo ""
    echo -e "For more information, refer to the documentation:"
    echo -e "  ${BLUE}docs/docker_installation.md${NC}"
    echo ""
else
    echo -e "${BLUE}============================================${NC}"
    echo -e "${GREEN}SwissAirDry Platform environment is prepared!${NC}"
    echo -e "${BLUE}============================================${NC}"
    echo ""
    echo -e "To build and start the containers later, run:"
    echo -e "  ${YELLOW}docker-compose up -d${NC}"
    echo ""
    echo -e "For more information, refer to the documentation:"
    echo -e "  ${BLUE}docs/docker_installation.md${NC}"
    echo ""
fi