FROM mcr.microsoft.com/devcontainers/python:3.12-bookworm

RUN echo "vscode ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/vscode
RUN chmod 440 /etc/sudoers.d/vscode

COPY .devcontainer/configure-user-remap.sh /tmp/configure-user-remap.sh
RUN bash /tmp/configure-user-remap.sh && rm /tmp/configure-user-remap.sh

USER vscode
RUN git config --global --add safe.directory /home/vscode/app
