FROM debian:bookworm

RUN apt-get update && apt-get install -y \
    locales \
    python3 python3-pip python3-venv \
    git curl sudo less vim \
    postgresql-client \
    iptables uidmap \
    apt-transport-https ca-certificates gnupg lsb-release \
    golang-docker-credential-helpers \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && locale-gen
ENV LANG=en_US.UTF-8 LANGUAGE=en_US:en LC_ALL=en_US.UTF-8

ARG USERNAME=dev
RUN useradd -m -s /bin/bash $USERNAME \
    && echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

USER $USERNAME
WORKDIR /home/$USERNAME/app

RUN python3 -m venv /home/$USERNAME/.venv
ENV PATH="/home/$USERNAME/.venv/bin:$PATH"

RUN mkdir -p /home/$USERNAME/.cache/pip /home/$USERNAME/.cache/pre-commit \
    && chown -R $USERNAME:$USERNAME /home/$USERNAME/.cache

ENV PIP_CACHE_DIR=/home/$USERNAME/.cache/pip

COPY --chown=$USERNAME:$USERNAME pyproject.toml ./
RUN --mount=type=cache,target=/home/$USERNAME/.cache/pip \
    pip install --upgrade pip setuptools wheel && \
    pip install .
COPY --chown=$USERNAME:$USERNAME . .

CMD ["sleep", "infinity"]
