FROM debian:bookworm

# Install base packages
RUN apt-get update && apt-get install -y \
    locales \
    python3 python3-pip python3-venv \
    git curl sudo less vim \
    postgresql-client \
    iptables uidmap \
    apt-transport-https ca-certificates gnupg lsb-release \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Setup locale
RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && locale-gen

# Install Docker CLI & daemon
RUN mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list \
    && apt-get update \
    && apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set locale environment
ENV LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8

# Create user
ARG USERNAME=dev
RUN useradd -m -s /bin/bash $USERNAME \
    && echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers \
    && groupadd -f docker && usermod -aG docker $USERNAME

# Install Python virtualenv
USER $USERNAME
WORKDIR /home/$USERNAME/app
RUN python3 -m venv /home/$USERNAME/.venv
ENV PATH="/home/$USERNAME/.venv/bin:$PATH"

# Copy project files
COPY --chown=dev:dev . .

COPY ./entrypoint.sh /etc/devcontainer/entrypoint.sh
