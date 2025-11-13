# SVS

- *🇬🇧 self-hosted virtual stack*
- *🇨🇿 studentský vývojový server*

---

- [Quickstart guide](setup/quickstart.md)
- [CLI documentation](cli.md)
- [API documentation](api/index.md)


## Introduction

SVS is a python library designed to provide users with an easy way to deploy containerized services on a host machine. It abstracts away the complexities of container orchestration, allowing users to focus on deploying and managing their applications with minimal effort.

### How does it work?

To Understand how SVS works, it's important to grasp a few key concepts:

#### Template

A template is a predefined configuration that outlines the specifications for a service. It includes details such as the container image to be used, resource limits, environment variables, and networking configurations. Templates serve as blueprints for creating services, ensuring consistency and standardization across deployments.

The templates can be defined as JSON files and have 2 main types:

1) **Image** - These templates are based on existing container images from registries like Docker Hub. They specify the image name, version, and any additional configurations needed to run the container. Those are pre-built and re-used by multiple services and only require mounting static files. For example, an NGINX web server template.

2) **Build** - These templates include instructions to build a container image from source code. They specify the build context, Dockerfile location, and any build arguments required. Build templates are useful for deploying custom applications that need to be built on-the-fly. For example, a Django web application that needs to be built from source code.
