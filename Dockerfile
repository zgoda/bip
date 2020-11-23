FROM python:3.8-buster as builder

COPY scripts/docker_install_packages.sh .

RUN \
    ./docker_install_packages.sh && \
    rm docker_install_packages.sh

RUN useradd --create-home bip

WORKDIR /home/bip

USER bip

COPY --chown=bip src/ ./src/

COPY --chown=bip LICENSE MANIFEST.in README.rst setup.cfg setup.py scripts/docker_install_app.sh ./

RUN \
    ./docker_install_app.sh && \
    rm docker_install_app.sh


FROM python:3.8-slim-buster as runtime

RUN useradd --create-home bip

WORKDIR /home/bip

USER bip

COPY --chown=bip --from=builder /home/bip/.local /home/bip/.local

COPY --chown=bip scripts/docker_setup_env.sh .

RUN \
    ls -la && \
    ./docker_setup_env.sh && \
    rm docker_setup_env.sh

COPY --chown=bip conf/site.json.example data/config/site.json

VOLUME [ "/home/bip/data" ]

ENV \
    FLASK_ENV=production \
    INSTANCE_PATH=/home/bip/data \
    SITE_JSON=/home/bip/data/config/site.json \
    DB_DRIVER=sqlite \
    DB_NAME=/home/bip/data/db.sqlite

COPY --chown=bip scripts/docker_entrypoint.sh .

CMD [ "./docker_entrypoint.sh" ]
