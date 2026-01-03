FROM mcr.microsoft.com/devcontainers/python:3.13-bookworm

RUN echo "vscode ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/vscode
RUN chmod 440 /etc/sudoers.d/vscode

USER vscode
RUN git config --global --add safe.directory /home/vscode/app

WORKDIR /home/vscode
