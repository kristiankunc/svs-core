#!/bin/bash

docker run --rm \
    -v "./fancy-docs:/workspace/fancy-docs:ro" \
    -v "./docs:/workspace/docs" \
    ghcr.io/typst/typst:latest \
    compile /workspace/fancy-docs/main.typ /workspace/docs/main.pdf
