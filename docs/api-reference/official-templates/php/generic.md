# Generic PHP Template

A template for deploying PHP applications with Apache - websites, WordPress, Laravel, or APIs.

## Usage

1. Prepare your application (see below)
2. [Create a service](../../../guides/index.md#create-a-service)
3. [Upload your code](../../../guides/index.md#uploading-files) via GIT or SSH
4. [Start the service](../../../guides/index.md#control)

## Preparation

Your project should have:
- `index.php` - Entry point
- `composer.json` - PHP dependencies (optional)

**Example `index.php`:**
```php
<?php
echo "Hello from SVS!";
?>
```

## Configuration

- **Runtime:** PHP 8.3 with Apache
- **Web Root:** `/var/www/html`
- **Port:** Container port 80 (HTTP)
- **Volume:** `/var/www/html` - Application code
- **User:** Non-root user `appuser`
- **Health Check:** Checks Apache response on port 80

## Environment Variables

Access in PHP:
```php
<?php
$db_host = getenv('DB_HOST');
?>
```

Example:
```bash
--env DB_HOST=my-mysql \
--env DB_NAME=mydb \
--env DB_USER=myuser \
--env DB_PASSWORD=mypass
```

## URL Rewriting

For clean URLs (Laravel, WordPress), create `.htaccess`:
```apache
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ index.php/$1 [L]
```

## Definition

??? note "Source"
    ```json
    --8<-- "service_templates/php.json"
    ```

??? note "Dockerfile"
    ```dockerfile
    --8<-- "service_templates/php.Dockerfile"
    ```
