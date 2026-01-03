# NGINX Template

A template for the [NGINX](https://nginx.org) web server.

## Usage

This template is fairly straightforward. After creating a service using this template, you can access the `www` directory inside the bind mount. All files here will be served by the NGINX web server.


## Definition

??? note "Source"
    ```json
    --8<-- "service_templates/nginx.json"
    ```
