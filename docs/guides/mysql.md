# MySQL - SQL database

## Use case

The MySQL template can be used to deploy a MySQL database server. MySQL is a widely used open-source relational database management system that is suitable for various applications, including web applications, data warehousing, and logging.

## Template

This guide uses the [mysql-database](../api-reference/official-templates/databases/mysql.md) template.

## Setup

When [creating the service](./index.md#create-a-service), you can configure your MySQL database by setting the following [environment variables](./index.md#terminology):

 - `MYSQL_ROOT_PASSWORD`: The password for the MySQL root user.
 - `MYSQL_DATABASE`: The name of a database to be created when the MySQL server starts for.
 - `MYSQL_USER`: The name of a user to be created when the MySQL server starts.
 - `MYSQL_PASSWORD`: The password for the user specified in MYSQL_USER.

## Access your database

Refer to [Docker's DNS](./index.md#dns) section for information on how to connect to your database service from other services.


Once you have [started the service](./index.md#control). You can use the port that's been [assigned to your service](./index.md#detailed-view) along with the service name to connect to your MySQL database.

To connect, use either the root user or the user you created with the environment variables during setup.
