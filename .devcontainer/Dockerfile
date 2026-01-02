FROM mcr.microsoft.com/devcontainers/python:3.13-bookworm

RUN echo "vscode ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/vscode
RUN chmod 440 /etc/sudoers.d/vscode

USER vscode
RUN git config --global --add safe.directory /home/vscode/app

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

WORKDIR /home/vscode
RUN /home/vscode/.cargo/bin/cargo init
RUN /home/vscode/.cargo/bin/cargo install typst-cli typst-live
