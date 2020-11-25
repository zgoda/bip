# Dockerfiles for BIP application

Collection of Dockerfiles for containerisation of BIP application. In general application is exposed on port 5000 and requires external reverse proxy to not disclose Gunicorn. The application runs in production mode with all optimisations turned on (such as Cythonised Peewee). These dockerfiles use local application code so they all require local source checkout to build.

Images built from these dockerfiles may be run with either Docker or [Podman](https://podman.io/).

## Simple

File name: `Dockerfile.simple`

This is the simplest Dockerfile that allows to containerise single-instance application. It uses SQLite as database and stores all data in internal volume. Because of that it should be run as **single instance only**.

To build image change to root directory and run either:

```shell
docker build -t bip:0.7.1 -f dockerfiles/Dockerfile.simple .
```

or

```shell
podman build -t bip:0.7.1 -f dockerfiles/Dockerfile.simple .
```

The resulting image can be then run in container with Docker or Podman, eg

```shell
podman run -ti --rm -p 5000:5000 bip:0.7.1
```

## PostgreSQL

File name: `Dockerfile.postgres`

PostgreSQL server should not be run containerised in production because of possible data corruption. Connection params have to be provided in command line as exported environment variable when running image. The only difference from *simple* image is that PostgreSQL DBAPI-2.0 library is installed along with application.

```shell
podman run -ti --rm \
    -e DB_HOST=ip_or_host_name \
    -e DB_PORT=5432 \
    -e DB_USER=bip \
    -e DB_PASSWORD=bip \
    -p 5000:5000 \
    bip:0.7.1
```

This requires that both database and user/role are created upfront.

While use of MySQL/MariaDB should be possible, it has not been tested.
