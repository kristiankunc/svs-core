# Template API reference

Templates are defined using `JSON` files and can be imported via the [cli](../../cli-documentation/template.md#svs-template-import) or the web interface.


The JSON schema is specified at https://github.com/kristiankunc/svs-core/blob/main/service_templates/schema.json.

You can also refer to the [official templates](./index.md) for examples of 1st party templates.

Generally, the schema should explain itself, but here are some notes on the fields:

## `dockerfile`

This field contains inline dockerfile instructions. To create such format from a regular dockerfile, you can use the [svs utils format-dockerfile](../../cli-documentation/utils.md#svs-utils-format-dockerfile) command.

```bash
sudo svs utils format-dockerfile service_templates/python.Dockerfile
```

## Docker user

The default user used in containsers is `root`. This is unsafe to use on SVS as it can lead to [privilige escalation](https://docs.docker.com/engine/security/#docker-daemon-attack-surface). To mitigate this, when writing a custom dockerfile you should **always create a non-root user who will be executing the entrypoint**.
