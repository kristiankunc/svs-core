# NGINX Template

A template for the [NGINX](https://nginx.org) web server, perfect for hosting static websites, single-page applications, or as a reverse proxy.

## What is NGINX?

NGINX is a high-performance web server that can serve static files, act as a reverse proxy, and handle HTTP/HTTPS traffic efficiently. This template provides a minimal NGINX configuration ready to serve your website.

## Quick Start Guide

Follow the **[Common Deployment Steps](../../../guides/common-steps.md)** to deploy your NGINX website:

1. **[Find the template](../../../guides/common-steps.md#find-a-template)** - Look for `nginx-webserver`
2. **[Create the service](../../../guides/common-steps.md#create-a-service)** - Optionally add a domain: `--domain my-site.example.com`
3. **[Upload your website files](../../../guides/common-steps.md#upload-files)** - Via GIT or SSH
4. **[Start the service](../../../guides/common-steps.md#start-a-service)** - Make your website live
5. **Access your website** - Via your configured domain or the assigned port

## Configuration

### Default Settings

- **Port:** Container port 80 (HTTP) is exposed
- **Volume:** `/config` directory stores NGINX configuration and website files
- **Health Check:** Configured to check if NGINX is responding on port 80

### Customizing NGINX Configuration

The NGINX configuration files are stored in the service's volume. You can modify them to:
- Add custom server blocks
- Configure SSL/TLS certificates
- Set up redirects or rewrites
- Configure caching

Access the configuration at `/config/nginx/` in your service's volume.

## Troubleshooting

### Website Not Loading

1. **[Check service status](../../../guides/common-steps.md#view-service-details):** Verify the service is running
2. **[Check logs](../../../guides/common-steps.md#view-service-logs):** See NGINX error messages
3. **Verify files:** Ensure your website files are in the correct directory

### Permission Issues

NGINX runs as a non-root user. Ensure your uploaded files have appropriate permissions.

## Common Use Cases

- **Static Website Hosting:** Upload HTML/CSS/JavaScript files and serve them
- **Single Page Applications:** Host React, Vue, or Angular applications
- **Reverse Proxy:** Configure NGINX to proxy requests to other services

## Additional Resources

- [NGINX Official Documentation](https://nginx.org/en/docs/)
- [NGINX Docker Image](https://hub.docker.com/r/linuxserver/nginx)
- [Common Deployment Steps](../../../guides/common-steps.md)


## Definition

??? note "Source"
    ```json
    --8<-- "service_templates/nginx.json"
    ```
