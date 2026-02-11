# Generic PHP Template

A generic template for deploying PHP applications with Apache, perfect for PHP websites, APIs, and web applications.

## What is This Template?

This template provides a PHP 8.3 runtime environment with Apache web server. It's flexible and suitable for:

- PHP websites and web applications
- WordPress, Laravel, or other PHP frameworks
- REST APIs built with PHP
- Legacy PHP applications
- Custom PHP services

## Quick Start Guide

Follow the **[Common Deployment Steps](../../../guides/common-steps.md)** to deploy your PHP application:

1. **Prepare your application** - Ensure you have `index.php` and optionally `composer.json` (see below)
2. **[Find the template](../../../guides/common-steps.md#find-a-template)** - Look for `php-generic`
3. **[Create the service](../../../guides/common-steps.md#create-a-service)** - Configure environment variables as needed
4. **[Upload your code](../../../guides/common-steps.md#upload-files)** - Via GIT or SSH
5. **[Start the service](../../../guides/common-steps.md#start-a-service)** - Your PHP app will start
6. **Access your application** - Via your configured domain or port

## Prepare Your Application

### Required Files

- **`index.php`** - Main entry point (or other `.php` files)
- **`composer.json`** - PHP dependencies via Composer (optional but recommended)

### Example `index.php`

```php
<?php
echo "Hello from SVS!";
?>
```

### Example `composer.json` (Optional)

```json
{
    "require": {
        "monolog/monolog": "^3.0"
    }
}
```

## Configuration

### Default Settings

- **Runtime:** PHP 8.3 with Apache
- **Web Root:** `/var/www/html` (all your PHP files should be here)
- **Port:** Container port 80 (HTTP) is exposed
- **User:** Runs as non-root user `appuser`
- **Volume:** `/var/www/html` directory stores your application code
- **Dependencies:** Automatically installs from `composer.json` if present
- **Health Check:** Configured to check if Apache is responding on port 80

### Environment Variables

[Configure your application](../../../guides/common-steps.md#configure-environment-variables) using environment variables:

```bash
--env DB_HOST=my-mysql \
--env DB_NAME=mydatabase \
--env DB_USER=myuser \
--env DB_PASSWORD=mypassword \
--env APP_ENV=production
```

Access environment variables in PHP:
```php
<?php
$db_host = getenv('DB_HOST');
$db_name = getenv('DB_NAME');
?>
```

### Apache Configuration

The template uses Apache's default configuration. To customize:

1. Create custom Apache config files
2. Upload them to the service volume
3. [Restart the service](../../../guides/common-steps.md#restart-a-service) to apply changes

Common customizations include:
- URL rewriting (`.htaccess`)
- Custom error pages
- PHP settings via `.htaccess` or `php.ini`

## Common Use Cases

### Simple PHP Website

```php
<!-- index.php -->
<!DOCTYPE html>
<html>
<head>
    <title>My PHP Site</title>
</head>
<body>
    <h1><?php echo "Welcome!"; ?></h1>
    <p>Current time: <?php echo date('Y-m-d H:i:s'); ?></p>
</body>
</html>
```

### PHP API

```php
<?php
header('Content-Type: application/json');

$data = [
    'status' => 'success',
    'message' => 'API is working',
    'timestamp' => time()
];

echo json_encode($data);
?>
```

### WordPress Installation

1. Download WordPress files
2. Upload to service volume
3. Configure `wp-config.php` with database credentials
4. Access the WordPress installer via your domain

### Laravel Application

1. Ensure `composer.json` includes all dependencies
2. Set up `.env` file with environment variables
3. Configure Apache to point to `public/` directory
4. Run migrations (via service logs or exec)

## Connecting to Databases

### MySQL Example

```php
<?php
$host = getenv('DB_HOST') ?: 'my-mysql';
$dbname = getenv('DB_NAME') ?: 'mydatabase';
$user = getenv('DB_USER') ?: 'myuser';
$password = getenv('DB_PASSWORD') ?: 'mypassword';

try {
    $pdo = new PDO(
        "mysql:host=$host;dbname=$dbname",
        $user,
        $password
    );
    echo "Connected successfully!";
} catch (PDOException $e) {
    echo "Connection failed: " . $e->getMessage();
}
?>
```

Configure with:
```bash
--env DB_HOST=my-mysql \
--env DB_NAME=mydatabase \
--env DB_USER=myuser \
--env DB_PASSWORD=mypassword
```

For more details, see [Access Services via DNS](../../../guides/common-steps.md#access-services-via-dns).

## URL Rewriting with .htaccess

For clean URLs or framework routing (Laravel, WordPress, etc.), create a `.htaccess` file:

```apache
# .htaccess
RewriteEngine On

# Redirect all requests to index.php
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ index.php/$1 [L]
```

## Troubleshooting

### White Screen / No Output

1. **[Check PHP errors](../../../guides/common-steps.md#view-service-logs):** View service logs
2. **Enable error display:** Add to your PHP file:
   ```php
   <?php
   ini_set('display_errors', 1);
   error_reporting(E_ALL);
   ?>
   ```
3. **Check Apache logs:** Errors are logged to service logs

### Composer Dependencies Not Installing

1. **Verify composer.json:** Ensure valid JSON syntax
2. **[Check logs](../../../guides/common-steps.md#view-service-logs):** Installation happens during build
3. **Package availability:** Ensure packages exist on Packagist

### File Permission Errors

The application runs as `appuser`. Ensure:
- Uploaded files have appropriate permissions
- Write operations target writable directories
- Cache/storage directories have write permissions

### Database Connection Errors

1. **[Check database service](../../../guides/common-steps.md#view-service-details):** Verify it's running
2. **Use service name:** For DB_HOST, use service name (e.g., `my-mysql`) not `localhost`
3. **Use container port:** Use 3306 for MySQL, 5432 for PostgreSQL
4. **Verify credentials:** Ensure environment variables match database configuration

### 404 Errors with Clean URLs

1. **Enable mod_rewrite:** Should be enabled by default in this template
2. **Create .htaccess:** Add URL rewriting rules (see above)
3. **Check Apache config:** Ensure `AllowOverride All` is set

## Best Practices

- **Use Composer:** Manage dependencies with `composer.json`
- **Environment variables:** Don't hardcode sensitive data; use environment variables
- **Error logging:** Configure proper error logging for production
- **Security:** Keep PHP and dependencies updated
- **HTTPS:** Always use HTTPS in production (configured via domain)

## Definition

??? note "Source"
    ```json
    --8<-- "service_templates/php.json"
    ```

??? note "Dockerfile"
    ```dockerfile
    --8<-- "service_templates/php.Dockerfile"
    ```

## Additional Resources

- [PHP Official Documentation](https://www.php.net/docs.php)
- [Apache HTTP Server Documentation](https://httpd.apache.org/docs/)
- [Composer Documentation](https://getcomposer.org/doc/)
- [Common Deployment Steps](../../../guides/common-steps.md)
