# PostgreSQL Template

A template for the [PostgreSQL](https://www.postgresql.org/) database server.

## Usage

This template allows you to quickly deploy a PostgreSQL database server. You only need to configure the credentials for the default user and database using the environment variables provided.

When [creating the service](./index.md#create-a-service), you can configure your PostgreSQL database by setting the following [environment variables](./index.md#terminology):

 - `POSTGRES_USER`: The username for the PostgreSQL user to be created when the server starts.
 - `POSTGRES_PASSWORD`: The password for the user specified in POSTGRES_USER.
 - `POSTGRES_DB`: The name of a database to be created when the PostgreSQL server starts.


## Access your database

Refer to [Docker's DNS](./index.md#dns) section for information on how to connect to your database service from other services.

Once you have [started the service](./index.md#control), you can use the port that's been [assigned to your service](./index.md#detailed-view) along with the service name to connect to your PostgreSQL database.

To connect, use the user and database credentials you configured with the environment variables during setup.

## Definition

??? note "Source"
    ```json
    --8<-- "service_templates/postgres.json"
    ```
