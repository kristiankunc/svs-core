FROM debian:bookworm

# Install base packages
RUN apt-get update && apt-get install -y \
    locales \
    python3 python3-pip python3-venv \
    git curl sudo less vim \
    postgresql-client \
    iptables uidmap \
    apt-transport-https ca-certificates gnupg lsb-release \
    golang-docker-credential-helpers \
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

# Switch to dev user
USER $USERNAME
WORKDIR /home/$USERNAME/app
ENV USER=dev

# Create Python virtualenv
RUN python3 -m venv /home/$USERNAME/.venv
ENV PATH="/home/$USERNAME/.venv/bin:$PATH"

# echo '{\n  "credsStore": "",\n  "auths": {\n    "https://index.docker.io/v1/": {}\n  }\n}' > $HOME/.docker/config.json

# Keep container alive for VS Code
CMD ["sleep", "infinity"]
