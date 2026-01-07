#!/bin/bash

set -e

# Source the main install script to reuse functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Prevent install.sh from running init() automatically
SOURCED_FOR_DEV=true

source "$SCRIPT_DIR/install.sh"

create_svs_user
permissions_setup
storage_setup
