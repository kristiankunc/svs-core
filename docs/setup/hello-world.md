## Starting a hello-world service

After successfully installing and configuring SVS, you can start your first service.

We're gonna run a simple nginx webserver

### Importing the config

Grab the example template configuration from [https://github.com/kristiankunc/svs-core/blob/main/service_templates/nginx.json](https://github.com/kristiankunc/svs-core/blob/main/service_templates/nginx.json)

```bash
curl https://raw.githubusercontent.com/kristiankunc/svs-core/refs/heads/main/service_templates/nginx.json -o nginx.json
```

and apply it using the [`svs template import`](../cli.md#svs-template-import) command

```bash
sudo svs template import nginx.json
```

Verify all data via [`svs template list`](../cli.md#svs-template-list)

```bash
sudo svs template list
```

### Creating the service

We use [`svs service create`](../cli.md#svs-service-create)

```bash
sudo svs service create <name> <template_id>
```

The IDs are indexed from 1 so you can likely put that in, if in doubt use the list commands (`svs template//user//service list`)

### Configuring

When reading info about the service using [`svs service get <id>`](../cli.md#svs-service-get), you will see a section about Volumes

??? example "Example output"
`volumes=['Volume(/config=/var/svs/volumes/1/hbhuclgfnfnqwrru)']`

```
This means that on host, you can modify the contents of `/var/svs/volumes/1/hbhuclgfnfnqwrru` which will be mirrored inside the container at `/config`.

What exactly this affects is specific to each service, but in this case, anything in the container `/config/www` will be served by nginx.

You can read more info about volumes [here](../index.md#data-storage)
```

To add a custom `index.html` page, create a file `/var/svs/volumes/<user_id>/<volume_id>/www/index.html` with your content. A Default one is already preconfigured to verify the service is working.

### Starting and checking the service

Simply start the service

```bash
sudo svs service start <service_id>
```

After that, you can list your services and see which port has been assigned. If you curl `localhost:<assigned_port>`, you should receive the nginx hello world message.
