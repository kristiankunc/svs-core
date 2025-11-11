#!/bin/bash

set -e

# Global variables
automated_yes=false
admin_user=""
admin_password=""
python_path="/opt/pipx/venvs/svs-core/bin/python"
setup_scope="all"

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

    # Check if Docker service is running
    if command -v systemctl &> /dev/null; then
        if systemctl is-active --quiet docker; then
            echo "✅ Docker service is running."
        else
            echo "❌ Docker service is not running."
            confirm
        fi
    else
        if ps aux | grep -q '[d]ockerd'; then
            echo "✅ Docker service is running."
        else
            echo "❌ Docker service is not running."
            confirm
        fi
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

    # Allow the svs script to switch to svs user internally without password
    echo "%svs-admins ALL=(svs) NOPASSWD: /usr/local/bin/svs" | sudo tee -a /etc/sudoers
    echo "✅ svs script can run as svs user without password prompt"
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

    sudo mkdir -p /etc/svs/docker
    sudo chown -R root:svs-admins /etc/svs/docker

    compose_path="/etc/svs/docker/docker-compose.yml"
    stack_env_path="/etc/svs/docker/stack.env"

    # Create docker-compose.yml first
    if [ ! -f "$compose_path" ]; then
        sudo bash -c 'cat > '"$compose_path"' <<'"'"'EOF'"'"'
name: "svs-core"

services:
  db:
    image: postgres:latest
    restart: unless-stopped
    container_name: svs-db
    ports:
      - "5432:5432"
    env_file:
      - stack.env
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
'
        echo "✅ $compose_path created."
    else
        echo "✅ $compose_path already exists."
    fi

    POSTGRES_USER=svs
    POSTGRES_DB=svsdb
    POSTGRES_HOST=localhost

    # Check if stack.env exists and read existing credentials
    if [ -f "$stack_env_path" ]; then
        echo "✅ $stack_env_path already exists."
        POSTGRES_PASSWORD=$(sudo grep "POSTGRES_PASSWORD=" "$stack_env_path" | cut -d'=' -f2)
    else
        # Generate a URL-safe password using only hexadecimal characters
        POSTGRES_PASSWORD=$(openssl rand -hex 16)
        sudo bash -c "cat > $stack_env_path <<EOL
POSTGRES_USER=$POSTGRES_USER
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
POSTGRES_DB=$POSTGRES_DB
POSTGRES_HOST=$POSTGRES_HOST
EOL"
        echo "✅ $stack_env_path created."
    fi

    # start the compose stack as daemon and wait for db to be ready
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
    echo "Setting up storage directories..."

    # Setup /etc/svs directory
    sudo mkdir -p /etc/svs
    sudo chown root:svs-admins /etc/svs
    sudo chmod 2775 /etc/svs

    # Setup /var/svs directory
    sudo mkdir -p /var/svs
    sudo mkdir -p /var/svs/volumes
    sudo chown -R root:svs-admins /var/svs
    sudo chmod 2775 /var/svs
    sudo chmod 2775 /var/svs/volumes

    # Create log file with proper permissions
    sudo touch /etc/svs/svs.log
    sudo chown svs:svs-admins /etc/svs/svs.log
    sudo chmod 660 /etc/svs/svs.log

    echo "✅ Storage directories and permissions set."
}

django_migrations() {
    echo "Running Django migrations..."

    DATABASE_URL=$(sudo cat /etc/svs/.env | grep DATABASE_URL | cut -d '=' -f2-)

    if  DATABASE_URL="$DATABASE_URL" $python_path -m django migrate svs_core; then
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

    # System setup: user creation and directory setup
    verify_prerequisites
    permissions_setup
    create_svs_user
    storage_setup

    # Docker and Django setup (only if scope is "all")
    if [ "$setup_scope" = "all" ]; then
        docker_setup
        django_migrations
        create_admin_user
    fi

    echo "✅ SVS environment initialization complete."
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
        --scope)
            setup_scope="$2"
            if [ "$setup_scope" != "all" ] && [ "$setup_scope" != "system" ]; then
                echo "❌ Invalid scope: $setup_scope. Must be 'all' or 'system'."
                exit 1
            fi
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
            echo "  --scope SCOPE             Scope of setup: 'all' (default) or 'system'."
            echo "                            'system' - User creation and directory setup only"
            echo "                            'all'    - Full setup including Docker, migrations, and admin user"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

init
