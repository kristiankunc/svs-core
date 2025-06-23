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

# Set locale environment
ENV LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8

# Create user
ARG USERNAME=dev
RUN useradd -m -s /bin/bash $USERNAME \
    && echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Install Python virtualenv
USER $USERNAME
WORKDIR /home/$USERNAME/app
RUN python3 -m venv /home/$USERNAME/.venv
ENV PATH="/home/$USERNAME/.venv/bin:$PATH"

COPY --chown=dev:dev . .
