#!/bin/bash

uvicorn web.asgi:application --reload --reload-include "*.html"
