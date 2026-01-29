## Generic Python Template

A generic template for deploying Python applications.

## Usage

This template is designed for any simple Python applications. It supports installing dependencies from a `requirements.txt` file located in the root of your project.

By default, the file `main.py` is ran, if you want to specify a different entrypoint, override the start command.

## Definition


??? note "Source"
    ```json
    --8<-- "service_templates/python.json"
    ```

??? note "Dockerfile"
    ```dockerfile
    --8<-- "service_templates/python.Dockerfile"
    ```
