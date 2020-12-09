#! /bin/bash

set -euo pipefail

reponame="${1:-localhost}"
imagename="bip-nginx"
tag=$(git describe --tags --abbrev=0)

cnt=$(buildah from "docker.io/library/nginx:stable-alpine")

buildah copy -q ${cnt} "conf/bip.docker.conf" "/etc/nginx/nginx.conf"

buildah commit --rm ${cnt} ${reponame}/${imagename}:${tag}
