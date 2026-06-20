#!/bin/bash

set -e

PIPX_HOME="${PIPX_HOME:-/opt/pipx}"
PIPX_BIN_DIR="${PIPX_BIN_DIR:-/usr/local/bin}"

automated_yes=false
admin_user=""
admin_password=""
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

BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

info()  { echo -e "${BOLD}${YELLOW}INFO${NC}   $1"; }
ok()    { echo -e "${BOLD}${GREEN}OK${NC}      $1"; }
fail()  { echo -e "${BOLD}${RED}FAIL${NC}    $1"; }
erro()  { echo -e "${BOLD}${RED}ERROR${NC}   $1"; }



verify_prerequisites() {
    echo ""
    info "Verifying system prerequisites..."

    if [ -f /etc/debian_version ]; then
        ok "System is Debian-based."
    else
        fail "This setup script is designed for Debian-based systems."
        confirm
    fi

    if command -v systemctl &>/dev/null && systemctl is-active --quiet docker; then
        ok "Docker service is running."
    elif docker info &>/dev/null; then
        ok "Docker service is running."
    else
        fail "Docker service is not running."
        confirm
    fi
}

permissions_setup() {
    echo ""
    info "Setting up permissions..."

    if getent group svs-admins > /dev/null; then
        ok "Group 'svs-admins' exists."
    else
        sudo groupadd svs-admins
        ok "Group 'svs-admins' created."
    fi

    sudo usermod -a -G svs-admins "$(id -u -n)"
    ok "User '$(id -u -n)' added to 'svs-admins' group."

    if grep -q "ALL ALL=NOPASSWD: /usr/local/bin/svs" /etc/sudoers 2>/dev/null; then
        ok "sudoers entry for 'svs' already exists."
    else
        echo "ALL ALL=NOPASSWD: /usr/local/bin/svs" | sudo tee -a /etc/sudoers >/dev/null
        ok "Added sudoers entry: ALL NOPASSWD: svs"
    fi

    if grep -q "%svs-admins ALL=(svs) NOPASSWD: /usr/local/bin/svs" /etc/sudoers 2>/dev/null; then
        ok "sudoers entry for 'svs-admins' already exists."
    else
        echo "%svs-admins ALL=(svs) NOPASSWD: /usr/local/bin/svs" | sudo tee -a /etc/sudoers >/dev/null
        ok "Added sudoers entry: %svs-admins NOPASSWD: svs"
    fi
}

create_svs_user() {
    echo ""
    info "Creating svs system user..."

    if id -u svs &>/dev/null; then
        ok "System user 'svs' already exists."
    else
        sudo useradd --system --no-create-home --shell /usr/sbin/nologin svs
        ok "System user 'svs' created."
    fi

    sudo usermod -a -G svs-admins svs
    sudo usermod -a -G docker svs
    ok "System user 'svs' added to 'svs-admins' and 'docker' groups."
}

storage_setup() {
    echo ""
    info "Setting up storage directories..."

    sudo mkdir -p /etc/svs
    sudo chown svs:svs-admins /etc/svs
    sudo chmod 2775 /etc/svs
    ok "/etc/svs/ created."

    sudo mkdir -p /var/svs/volumes
    sudo chown -R svs:svs-admins /var/svs
    sudo chmod 2775 /var/svs
    sudo chmod 2775 /var/svs/volumes
    ok "/var/svs/volumes/ created."

    sudo touch /etc/svs/svs.log
    sudo chown svs:svs-admins /etc/svs/svs.log
    sudo chmod 660 /etc/svs/svs.log
    ok "/etc/svs/svs.log created."
}

setup_environment() {
    echo ""
    info "Setting environment variables..."

    local env_file="/etc/environment"

    if ! grep -q "PIPX_HOME=" "$env_file" 2>/dev/null; then
        echo "PIPX_HOME=\"$PIPX_HOME\"" | sudo tee -a "$env_file" >/dev/null
        ok "PIPX_HOME added to $env_file"
    else
        ok "PIPX_HOME already set in $env_file"
    fi

    if ! grep -q "PIPX_BIN_DIR=" "$env_file" 2>/dev/null; then
        echo "PIPX_BIN_DIR=\"$PIPX_BIN_DIR\"" | sudo tee -a "$env_file" >/dev/null
        ok "PIPX_BIN_DIR added to $env_file"
    else
        ok "PIPX_BIN_DIR already set in $env_file"
    fi
}

install_svs() {
    echo ""
    info "Installing/upgrading svs-core via pipx..."

    if ! command -v pipx &>/dev/null; then
        info "pipx not found. Installing..."
        sudo apt-get update -qq && sudo apt-get install -y -qq pipx
        pipx ensurepath
        ok "pipx installed."
    fi

    PIPX_HOME="$PIPX_HOME" PIPX_BIN_DIR="$PIPX_BIN_DIR" pipx install svs-core --force
    ok "svs-core installed via pipx."
}

run_svs_init() {
    echo ""
    info "Handing off to 'svs init' for application setup..."

    local init_args=""
    [ "$automated_yes" = true ] && init_args="$init_args --yes"
    [ -n "$admin_user" ] && init_args="$init_args --user $admin_user"
    [ -n "$admin_password" ] && init_args="$init_args --password $admin_password"

    PIPX_HOME="$PIPX_HOME" PIPX_BIN_DIR="$PIPX_BIN_DIR" \
        svs init $init_args

    echo ""
    ok "SVS bootstrap complete!"
}


init() {
    echo ""
    echo "============================================"
    echo "  SVS Bootstrap Installer"
    echo "============================================"
    echo "Scope: $setup_scope"
    [ "$automated_yes" = true ] && echo "Mode: automated"

    verify_prerequisites
    permissions_setup
    create_svs_user
    storage_setup
    setup_environment

    if [ "$setup_scope" = "all" ]; then
        install_svs
        run_svs_init
    else
        echo ""
        ok "System setup complete. Run 'sudo svs init' to finish configuration."
    fi
}


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
        --scope)
            setup_scope="$2"
            if [ "$setup_scope" != "all" ] && [ "$setup_scope" != "system" ]; then
                erro "Invalid scope: $setup_scope. Must be 'all' or 'system'."
                exit 1
            fi
            shift 2
            ;;
        --help)
            echo "Usage: install.sh [options]"
            echo ""
            echo "Options:"
            echo "  -y, --yes                 Non-interactive (automated) mode."
            echo "  --user USERNAME           Admin username for svs init."
            echo "  --password PASSWORD       Admin password for svs init."
            echo "  --scope SCOPE             'all' (default) or 'system'."
            echo "                            'system' = user+dirs+sudoers only."
            exit 0
            ;;
        *)
            erro "Unknown option: $1"
            exit 1
            ;;
    esac
done

if [ -z "$SOURCED_FOR_DEV" ]; then
    init
fi
