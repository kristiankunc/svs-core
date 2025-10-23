#!/bin/bash

set -e

# Global variables
automated_yes=false

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

env_setup() {
    echo "Setting up /etc/svs/.env file..."

    env_path="/etc/svs/.env"

    if [ -f "$env_path" ]; then
        echo "✅ /etc/svs/.env already exists."
    else
        sudo mkdir -p /etc/svs
        sudo chown -R root:svs-admins /etc/svs
        sudo chmod 2775 /etc/svs
        sudo touch "$env_path"
        sudo chmod 640 "$env_path"
        sudo chown svs:svs-admins "$env_path"
        echo "✅ /etc/svs/.env created and permissions set."
    fi
}

storage_setup() {
    echo "Setting up /var/svs storage..."

    sudo mkdir -p /var/svs
    sudo chown -R root:svs-admins /var/svs
    sudo chmod 2775 /var/svs
    echo "✅ /var/svs created and permissions set."
}

django_migrations() {
    echo "Running Django migrations..."

    if /opt/pipx/venvs/svs-core/bin/python -m django migrate svs_core; then
        echo "✅ Django migrations completed."
    else
        echo "❌ Failed to run Django migrations."
        exit 1
    fi
}

create_admin_user() {
    echo "Creating initial admin user..."
    if /opt/pipx/venvs/svs-core/bin/python -c "from svs_core.__main__ import cli_first_user_setup; cli_first_user_setup()"; then
        echo "✅ Admin user created (or already exists)."
    else
        echo "❌ Failed to create admin user."
        exit 1
    fi
}

init() {
    echo "Initializing the SVS environment..."

    verify_prerequisites
    permissions_setup
    create_svs_user
    env_setup
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
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

init
