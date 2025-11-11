#!/bin/bash

set -e

# Global variables
automated_yes=false
admin_user=""
admin_password=""
python_path="/opt/pipx/venvs/svs-core/bin/python"

confirm() {
    if [ "$automated_yes" = true ]; then
        return
    fi

    read -p "Are you sure you want to proceed? (y/n) " answer
    if [ "$answer" != "y" ]; then
        echo "Aborted."
        exit 1
    fi
}

verify_prerequisites() {
    echo "Verifying system prerequisites..."

    # Check if system is Debian-based
    if [ -f /etc/debian_version ]; then
        echo "✅ System is Debian-based."
    else
        echo "❌ This setup script is designed for Debian-based systems."
        confirm
    fi

    # Check if Docker is installed
    if command -v docker &> /dev/null; then
        echo "✅ Docker is installed."
    else
        echo "❌ Docker is not installed or not in PATH."
        confirm
    fi

    # Check if required Docker containers are running
    if docker ps --filter 'name=svs-db' --filter 'name=caddy' --format '{{.Names}}' | grep -qE "svs-db|caddy"; then
        echo "✅ Required Docker containers are running."
    else
        echo "❌ Required Docker containers 'svs-db' and 'caddy' are not running."
        confirm
    fi
}

permissions_setup() {
    echo "Setting up necessary permissions..."

    # Create svs-admins group
    if getent group svs-admins > /dev/null; then
        echo "✅ Group 'svs-admins' exists."
    else
        sudo groupadd svs-admins
        echo "✅ Group 'svs-admins' created."
    fi

    # Add current user to svs-admins group
    sudo usermod -a -G svs-admins "$(id -u -n)"
    echo "✅ User '$(id -u -n) added to 'svs-admins' group."

    echo "ALL ALL=NOPASSWD: /usr/local/bin/svs" | sudo tee -a /etc/sudoers
    echo "✅ /usr/local/bin/svs is runnable with sudo for all"
}

create_svs_user() {
    echo "Creating svs system user..."

    if id -u svs &> /dev/null; then
        echo "✅ System user 'svs' already exists."
    else
        sudo useradd --system --no-create-home --shell /usr/sbin/nologin svs
        echo "✅ System user 'svs' created."
    fi
}

docker_setup() {
    echo "Setting up Docker environment..."

    sudo mkdir -p /etc/svs
    sudo chown -R root:svs-admins /etc/svs
    sudo chmod 2775 /etc/svs

    sudo mkdir -p /etc/svs/docker
    sudo chown -R root:svs-admins /etc/svs/docker

    POSTGRES_USER=svs
    POSTGRES_PASSWORD=$(openssl rand -base64 12)
    POSTGRES_DB=svsdb
    POSTGRES_HOST=localhost

    # Create stack.env only if it doesn't exist
    stack_env_path="/etc/svs/docker/stack.env"
    if [ -f "$stack_env_path" ]; then
        echo "✅ $stack_env_path already exists."
    else
        sudo bash -c "cat > $stack_env_path <<EOL
POSTGRES_USER=$POSTGRES_USER
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
POSTGRES_DB=$POSTGRES_DB
POSTGRES_HOST=$POSTGRES_HOST
EOL"
        echo "✅ $stack_env_path created."
    fi

    # Create docker-compose.yml only if it doesn't exist
    compose_path="/etc/svs/docker/docker-compose.yml"
    if [ -f "$compose_path" ]; then
        echo "✅ $compose_path already exists."
    else
        sudo bash -c "cat > $compose_path <<EOL$(cat << 'EOF'
name: "svs-core"

services:
  db:
    image: postgres:latest
    restart: unless-stopped
    container_name: svs-db
    ports:
      - "5432:5432"
    env_file:
      - .env
    volumes:
      - pgdata:/var/lib/postgresql

  caddy:
    image: lucaslorentz/caddy-docker-proxy:latest
    container_name: caddy
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - caddy_data:/data
      - caddy_config:/config
    environment:
      - CADDY_INGRESS_NETWORK=caddy
    networks:
      - caddy

volumes:
  pgdata:
  caddy_data:
  caddy_config:

networks:
  caddy:
    driver: bridge
EOF
)"
        echo "✅ $compose_path created."
    fi

    # start the compose stack as deamon and wait for db to be ready
    sudo docker-compose -f $compose_path --env-file $stack_env_path up -d
    echo "Waiting for PostgreSQL to be ready..."
    until sudo docker exec svs-db pg_isready -U $POSTGRES_USER; do
        sleep 2
    done

    env_path="/etc/svs/.env"
    if [ -f "$env_path" ]; then
        echo "✅ $env_path already exists."
    else
        sudo touch "$env_path"
        sudo chmod 640 "$env_path"
        sudo chown svs:svs-admins "$env_path"
        sudo bash -c "echo DATABASE_URL=postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@$POSTGRES_HOST:5432/$POSTGRES_DB > $env_path"
        echo "✅ $env_path created with DATABASE_URL."
    fi
}

storage_setup() {
    echo "Setting up /var/svs storage..."

    sudo mkdir -p /var/svs
    sudo mkdir -p /var/svs/volumes
    sudo chown -R root:svs-admins /var/svs
    sudo chmod 2775 /var/svs
    sudo chmod 2775 /var/svs/volumes
    echo "✅ /var/svs created and permissions set."
}

django_migrations() {
    echo "Running Django migrations..."

    if $python_path -m django migrate svs_core; then
        echo "✅ Django migrations completed."
    else
        echo "❌ Failed to run Django migrations."
        exit 1
    fi
}

create_admin_user() {
    echo "Creating initial admin user..."

    if [ -n "$admin_user" ] && [ -n "$admin_password" ]; then
        # User and password provided via command line
        if $python_path -c "from svs_core.__main__ import cli_first_user_setup; cli_first_user_setup(username='$admin_user', password='$admin_password')"; then
            echo "✅ Admin user '$admin_user' created."
        else
            echo "❌ Failed to create admin user."
            exit 1
        fi
    else
        # Interactive mode (original behavior)
        if $python_path -c "from svs_core.__main__ import cli_first_user_setup; cli_first_user_setup()"; then
            echo "✅ Admin user created (or already exists)."
        else
            echo "❌ Failed to create admin user."
            exit 1
        fi
    fi
}

init() {
    echo "Initializing the SVS environment..."

    export DJANGO_SETTINGS_MODULE=svs_core.db.settings

    verify_prerequisites
    permissions_setup
    create_svs_user
    docker_setup
    storage_setup
    django_migrations
    create_admin_user

    echo "✅ SVS environment initialization complete."
    echo "Please configure the /etc/svs/.env file before starting SVS services."
}

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -y|--yes)
            automated_yes=true
            shift
            ;;
        --user)
            admin_user="$2"
            shift 2
            ;;
        --password)
            admin_password="$2"
            shift 2
            ;;
        --python-path)
            python_path="$2"
            shift 2
            ;;
        --help)
            echo "Usage: install.sh [options]"
            echo ""
            echo "Options:"
            echo "  -y, --yes                 Run in automated mode, skipping confirmations."
            echo "  --user USERNAME           Specify admin username."
            echo "  --password PASSWORD       Specify admin password."
            echo "  --python-path PATH        Specify the Python interpreter path."
            exit 0
            ;;
        *)


            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

init
