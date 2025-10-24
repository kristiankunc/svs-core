## Starting a hello-world service

After successfully installing and configuring SVS, you can start your first service.

We're gonna run a simple nginx webserver

### Importing the config

Grab the example template configuration from [https://github.com/kristiankunc/svs-core/blob/main/service_templates/nginx.json](https://github.com/kristiankunc/svs-core/blob/main/service_templates/nginx.json)

```bash
$ curl -o nginx.json https://raw.githubusercontent.com/kristiankunc/svs-core/refs/heads/main/service_templates/nginx.json
```

and apply it using the [`svs template import`](../cli.md#svs-template-import) command

```bash
$ sudo svs template import nginx.json
```

Verify all data via [`svs template list`](../cli.md#svs-template-list)

```bash
$ sudo svs template list
```

### Creating the service

We use [`svs service create`](../cli.md#svs-service-create)

```bash
$ sudo svs service create <user_id> <template_id>
```

The IDs are indexed from 1 so you can likely put that in, if in doubt use the list commands (`svs template//user//service list`)

### Starting and checking the service

Simply start the service

```bash
$ sudo svs service start <service_id>
```

After that, you can list your services and see which port has been assigned. If you curl `localhost:<assigned_port>`, you should receive the nginx hello world message.
