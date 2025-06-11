#!/bin/bash
set -e

# UCC Event Manager Production Deployment Script
# This script assists with deploying the application in a production environment

# Print usage information
function show_usage {
    echo "UCC Event Manager Deployment Script"
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  setup           - Initial setup (generate certificates, etc.)"
    echo "  deploy          - Deploy the application"
    echo "  update          - Update an existing deployment"
    echo "  backup          - Backup database and configuration"
    echo "  generate-keys   - Generate new JWT RS256 key pair"
    echo "  migrate         - Run database migrations"
    echo "  logs [service]  - View logs (optional: specify service name)"
    echo "  help            - Show this help message"
    echo ""
}

# Setup initial configuration
function setup {
    echo "Setting up UCC Event Manager production environment..."
    
    # Create necessary directories
    mkdir -p nginx/certs nginx/conf.d nginx/www
    
    # Check if prod.env exists, if not, create from example
    if [ ! -f ".env" ]; then
        if [ -f "prod.env.example" ]; then
            echo "Creating .env file from example..."
            cp prod.env.example .env
            echo "WARNING: Please edit .env and replace all placeholder values!"
        else
            echo "ERROR: prod.env.example not found!"
            exit 1
        fi
    fi
    
    # Generate self-signed certificates for development/testing
    # In production, you should use Let's Encrypt or other trusted certificates
    if [ ! -f "nginx/certs/fullchain.pem" ]; then
        echo "Generating self-signed SSL certificates..."
        mkdir -p nginx/certs
        openssl req -x509 -nodes -days 365 -newkey rsa:4096 \
            -keyout nginx/certs/privkey.pem \
            -out nginx/certs/fullchain.pem \
            -subj "/C=US/ST=State/L=City/O=UCC/CN=ucc-event-manager.com"
        echo "NOTE: For production, replace these with trusted certificates!"
    fi
    
    # Generate JWT keys
    generate_keys
    
    echo "Setup complete. Next steps:"
    echo "1. Edit .env file with proper production values"
    echo "2. Run './deploy.sh deploy' to start the application"
}

# Generate JWT keys
function generate_keys {
    echo "Generating new JWT RS256 key pair..."
    
    # Create keys directory if it doesn't exist
    mkdir -p keys
    
    # Generate private key
    openssl genrsa -out keys/jwt-private.pem 4096
    
    # Generate public key
    openssl rsa -in keys/jwt-private.pem -pubout -out keys/jwt-public.pem
    
    echo "Keys generated in 'keys' directory."
    echo "Private key: keys/jwt-private.pem"
    echo "Public key: keys/jwt-public.pem"
    echo ""
    echo "IMPORTANT: In production, store these securely and load them from a secure storage service."
    echo "           Do not commit these keys to version control."
}

# Deploy the application
function deploy {
    echo "Deploying UCC Event Manager..."
    
    # Verify that .env file exists
    if [ ! -f ".env" ]; then
        echo "ERROR: .env file not found. Run './deploy.sh setup' first."
        exit 1
    fi
    
    # Verify that SSL certificates exist
    if [ ! -f "nginx/certs/fullchain.pem" ] || [ ! -f "nginx/certs/privkey.pem" ]; then
        echo "ERROR: SSL certificates not found. Run './deploy.sh setup' first."
        exit 1
    fi
    
    # Pull latest images or build them
    docker-compose -f docker-compose.prod.yml build
    
    # Start the services in detached mode
    docker-compose -f docker-compose.prod.yml up -d
    
    # Run database migrations
    migrate
    
    echo "Deployment complete! Application is now running."
}

# Update an existing deployment
function update {
    echo "Updating UCC Event Manager..."
    
    # Pull latest code if in a git repository
    if [ -d ".git" ]; then
        git pull
        echo "Pulled latest code."
    fi
    
    # Update the containers
    docker-compose -f docker-compose.prod.yml down
    docker-compose -f docker-compose.prod.yml build
    docker-compose -f docker-compose.prod.yml up -d
    
    # Run database migrations
    migrate
    
    echo "Update complete!"
}

# Backup database and configuration
function backup {
    echo "Backing up UCC Event Manager..."
    
    # Create backup directory
    BACKUP_DIR="backups/$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Backup environment variables
    cp .env "$BACKUP_DIR/env.backup"
    
    # Backup PostgreSQL database
    echo "Backing up database..."
    docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > "$BACKUP_DIR/database.sql"
    
    # Backup JWT keys if they exist
    if [ -d "keys" ]; then
        cp -r keys "$BACKUP_DIR/keys"
    fi
    
    echo "Backup completed successfully in $BACKUP_DIR"
}

# Run database migrations
function migrate {
    echo "Running database migrations..."
    
    # Wait for the database to be ready
    sleep 5
    
    # Run migrations using the backend service
    docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
    
    echo "Database migrations completed successfully."
}

# View logs
function logs {
    SERVICE="$1"
    
    if [ -z "$SERVICE" ]; then
        # View all logs if no service specified
        docker-compose -f docker-compose.prod.yml logs --tail=100 -f
    else
        # View logs for the specified service
        docker-compose -f docker-compose.prod.yml logs --tail=100 -f "$SERVICE"
    fi
}

# Main script logic
COMMAND="$1"
PARAM="$2"

case "$COMMAND" in
    setup)
        setup
        ;;
    deploy)
        deploy
        ;;
    update)
        update
        ;;
    backup)
        backup
        ;;
    generate-keys)
        generate_keys
        ;;
    migrate)
        migrate
        ;;
    logs)
        logs "$PARAM"
        ;;
    help|*)
        show_usage
        ;;
esac

exit 0 