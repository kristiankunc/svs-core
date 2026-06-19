FROM php:8.3-apache

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /var/www/html

RUN chown -R appuser:appuser /var/www/html

USER appuser

RUN if [ -f composer.json ]; then curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer && composer install --no-interaction --prefer-dist; fi

CMD ["apache2-foreground"]
