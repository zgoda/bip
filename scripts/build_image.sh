#! /bin/bash

set -euo pipefail

reponame="${1:-localhost}"
imagename="bip"
tag=$(git describe --tags --abbrev=0)
username="bip"
userhome="/home/${username}"

rm -rf build dist
python3 setup.py bdist_wheel
python3 -m pip install -U pip-tools
pip-compile

export DEBIAN_FRONTEND=noninteractive

# builder container
builder_cnt=$(buildah from "docker.io/library/python:3.8-buster")

buildah run ${builder_cnt} apt-get update
buildah run ${builder_cnt} \
	apt-get -y install --no-install-recommends \
	build-essential libffi-dev libicu-dev libmagic-dev

buildah run ${builder_cnt} useradd --create-home ${username}
buildah config \
	--user ${username} \
	--workingdir ${userhome} \
	${builder_cnt}

buildah run ${builder_cnt} /usr/local/bin/python3 -m venv venv
py=${userhome}/venv/bin/python3
buildah run ${builder_cnt} ${py} -m pip install --no-cache-dir -U pip wheel setuptools Cython

builder_mnt=$(buildah mount ${builder_cnt})

cp requirements.txt ${builder_mnt}/${userhome}/
buildah run ${builder_cnt} ${py} -m pip install --no-cache-dir -U -r requirements.txt
rm ${builder_mnt}/${userhome}/requirements.txt
buildah run ${builder_cnt} ${py} -m pip install --no-cache-dir -U gunicorn
cp dist/*.whl ${builder_mnt}/${userhome}/
buildah run ${builder_cnt} ${py} -m pip install --no-cache-dir -U --no-index --find-links=. biuletyn-bip
rm -rf ${builder_mnt}/${userhome}/*.whl
buildah run ${builder_cnt} ${py} -m pip uninstall --no-cache-dir -y Cython

# runtime container
runtime_cnt=$(buildah from "docker.io/library/python:3.8-slim-buster")

buildah run ${runtime_cnt} apt-get update
buildah run ${runtime_cnt} apt-get -y install --no-install-recommends libicu63 libmagic1 libffi6
buildah run ${runtime_cnt} apt-get clean
buildah run ${runtime_cnt} rm -rf /var/lib/apt/lists/*

buildah run ${runtime_cnt} useradd --create-home ${username}
buildah config \
	--workingdir ${userhome} \
	--user ${username} \
	${runtime_cnt}

runtime_mnt=$(buildah mount ${runtime_cnt})

cp -r ${builder_mnt}/${userhome}/venv ${runtime_mnt}/${userhome}/

# static content directories
mkdir -p ${runtime_mnt}/${userhome}/data/config ${runtime_mnt}/${userhome}/data/attachments

# gunicorn runtime and artifacts
mkdir -p ${runtime_mnt}/${userhome}/run/logs

buildah copy --chown=${username} ${runtime_cnt} conf/site.json.example data/config/site.json
buildah copy --chown=${username} ${runtime_cnt} scripts/docker_entrypoint.sh ./

buildah config \
	--env PYTHONDONTWRITEBYTECODE=1 \
	--env PYTHONUNBUFFERED=1 \
	--env FLASK_ENV=production \
	--env ENV=production \
	--env INSTANCE_PATH=${userhome}/data \
	--env SITE_JSON=${userhome}/data/config/site.json \
	--env DB_DRIVER=sqlite \
	--env DB_NAME=${userhome}/data/bip.sqlite \
	--cmd '[ "./docker_entrypoint.sh" ]' \
	--volume ${userhome}/data \
	--volume ${userhome}/run \
	${runtime_cnt}

buildah umount ${builder_cnt}
buildah umount ${runtime_cnt}
buildah commit --rm ${runtime_cnt} ${reponame}/${imagename}:${tag}
buildah rm ${builder_cnt}

rm -rf requirements.txt build dist
python3 -m pip uninstall -y pip-tools
