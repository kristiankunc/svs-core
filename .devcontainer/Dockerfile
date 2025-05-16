FROM debian:bookworm

# Install locales and set up en_US.UTF-8
RUN apt-get update && apt-get install -y \
    locales python3 python3-pip python3-venv git curl sudo less vim \
    && echo "en_US.UTF-8 UTF-8" > /etc/locale.gen \
    && locale-gen \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

ENV LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8

ARG USERNAME=dev
RUN useradd -m -s /bin/bash $USERNAME && echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

USER $USERNAME
WORKDIR /home/$USERNAME/app

RUN python3 -m venv /home/$USERNAME/.venv
ENV PATH="/home/$USERNAME/.venv/bin:$PATH"

# Copy only requirements.txt first for caching
COPY --chown=dev:dev requirements.txt ./requirements.txt

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt
    
# Copy the rest of the library source code
COPY --chown=dev:dev . .
