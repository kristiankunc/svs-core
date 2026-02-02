FROM mcr.microsoft.com/devcontainers/python:3.13-bookworm

RUN echo "vscode ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/vscode \
    && chmod 440 /etc/sudoers.d/vscode


RUN rm -f /etc/apt/sources.list.d/yarn.list \
    && rm -f /etc/apt/sources.list.d/*yarn*

USER vscode
ENV NVM_DIR=/home/vscode/.nvm


RUN curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.4/install.sh | bash \
    && . "$NVM_DIR/nvm.sh" \
    && nvm install 22 \
    && nvm alias default 22 \
    && nvm use 22 \
    && npm install -g npm@latest

ENV NODE_PATH=$NVM_DIR/versions/node/v22.*/lib/node_modules
ENV PATH=$NVM_DIR/versions/node/v22.*/bin:$PATH

RUN git config --global --add safe.directory /home/vscode/app

WORKDIR /home/vscode
