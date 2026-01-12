# NGINX - Static website

## Use case

The NGINX template can be used to deploy static websites consisting of HTML, CSS, and JavaScript files. NGINX is a high-performance web server that efficiently serves static content.

## Template

This guide uses the [nginx-webserver](../api-reference/official-templates/webservers/nginx.md) template.

## Setup

After [creating the service](./index.md#create-a-service) (_preferably with a custom domain_), you can upload your static website files to the service's storage.

Note the [host path](./index.md#volumes) of the service's storage volume using the [detailed service view](./index.md#manage-your-service).

Upload your static website files (HTML, CSS, JS, images, etc.) to the `www` directory inside the storage volume. For example, if the host path of the storage volume is `/var/svs/volumes/1/foo`, upload your files to `/var/svs/volumes/1/foo/www`. This is where the NGINX server looks for the website files to serve.

## Access your website

Once you have uploaded your static files and [started the service](./index.md#control). You can use the port that's been [assigned to your service](./index.md#detailed-view) or the custom domain you specified during service creation to access your static website.
