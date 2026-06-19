## Prerequisites

Before you begin, ensure you meet the following prerequisites:

- **Linux distribution:** A Debian-based distribution (e.g., Debian, Ubuntu) is required.
- **Docker:** Installed and running. Follow the [official Docker guide](https://docs.docker.com/engine/install/) if needed.

## One-command setup

Download and run the bootstrap installer. It will handle everything - system users, directories, pipx, and hands off to the `svs init` command for application setup.

```bash
curl -sS https://raw.githubusercontent.com/kristiankunc/svs-core/refs/heads/main/scripts/install.sh | sudo bash
```

??? question "What does the script do?"
    1. **System setup** - Creates the `svs` system user, `svs-admins` group, storage directories, and sudoers entries.
    2. **Installation** - Installs `svs-core` via pipx and sets up environment variables.
    3. **`svs init`** - Creates the Docker Compose stack (PostgreSQL + Caddy), runs database migrations, imports official service templates, installs bash completions, and prompts you to create an admin user.

    The script is **idempotent** - running it multiple times is safe.

### Automated mode

For fully non-interactive installation:

```bash
curl -sS https://raw.githubusercontent.com/kristiankunc/svs-core/refs/heads/main/scripts/install.sh | sudo bash -s -- -y --user admin --password your-password
```

### System-only setup

If you only want the system user, groups, and directories without installing svs-core itself (useful for development):

```bash
curl -sS https://raw.githubusercontent.com/kristiankunc/svs-core/refs/heads/main/scripts/install.sh | sudo bash -s -- --scope system
```

## Manual alternative

If you prefer to install step-by-step, or the bootstrap script doesn't cover your case:

```bash
# 1. Install pipx and svs-core
sudo apt install pipx
pipx ensurepath
sudo PIPX_HOME=/opt/pipx PIPX_BIN_DIR=/usr/local/bin pipx install svs-core

# 2. Set environment variables
printf '%s\n' 'PIPX_HOME="/opt/pipx"' 'PIPX_BIN_DIR="/usr/local/bin"' | sudo tee -a /etc/environment

# 3. Bootstrap system setup (user, groups, directories, sudoers)
#    Downloads and runs only the system portion of the installer
curl -sS https://raw.githubusercontent.com/kristiankunc/svs-core/refs/heads/main/scripts/install.sh \
  | sudo bash -s -- --scope system

# 4. Initialize the SVS environment (Docker stack, migrations, templates)
sudo svs init
```

## Verify

Check that everything is working:

```bash
sudo svs user list
```

This should display the admin user you created during setup.

## Next steps

- Follow the [hello-world guide](hello-world.md) to start your first service.
- Browse the [CLI documentation](../cli-documentation/) for all available commands.
- Set up the [web interface](web.md) for a graphical management UI.

## Updating

```bash
curl -sS https://raw.githubusercontent.com/kristiankunc/svs-core/refs/heads/main/scripts/update.sh | sudo bash
```

This script upgrades svs-core via pipx, runs Django migrations, and applies any system migration steps.

## Uninstalling

To completely remove SVS from your server:

```bash
sudo svs destroy
```

This stops all services, removes Docker containers and volumes, deletes configuration files, cleans up sudoers entries, and removes the `svs` system user.

Add `--yes` for automated removal:

```bash
sudo svs destroy --yes
```

!!! warning "Destructive operation"
    `svs destroy` is irreversible. Use `--keep-volumes` or `--keep-config` if you want to preserve data or configuration.
