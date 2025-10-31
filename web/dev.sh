#!/bin/bash

# npx @tailwindcss/cli -i input.css -o static/css/output.css --watch

uvicorn web.asgi:application --reload --reload-include "*.html"

##
