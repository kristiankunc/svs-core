# NGINX Template

A template for the [NGINX](https://nginx.org) web server for hosting static websites, single-page applications, or as a reverse proxy.

## Usage

1. [Create a service](../../../guides/index.md#create-a-service) using the NGINX template. _Add a [domain](../../../guides/index.md#domains) if you wish_
2. [Upload your website files](../../../guides/index.md#uploading-files) to the service's `/config/www` directory
3. [Start the service](../../../guides/index.md#control)
4. Access via your configured domain or assigned port

## Configuration

- **Port:** Container port 80 (HTTP)
- **Volume:** `/config` - Stores NGINX configuration and website files
- **Health Check:** Checks if NGINX responds on port 80

## Customization

NGINX configuration files are in `/config/` in your service's volume. Customize for SSL, rewrites, caching, etc.

## Definition

??? note "Source"
    ```json
    --8<-- "service_templates/nginx.json"
    ```
