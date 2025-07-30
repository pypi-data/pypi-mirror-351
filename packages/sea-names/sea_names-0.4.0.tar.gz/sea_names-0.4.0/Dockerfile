# syntax = docker/dockerfile:experimental
FROM debian:buster-20200511
LABEL maintainer="Luke Campbell <luke@axds.co>"
ENV DEBIAN_FRONTEND noninteractive
ENV LANG C.UTF-8

RUN apt-get update && apt-get install -y \
        binutils \
        build-essential \
        bzip2 \
        ca-certificates \
        curl \
        wget \
        git \
        libarchive13 \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ENV MINICONDA_VERSION py39_4.12.0
ENV MINICONDA_SHA256 78f39f9bae971ec1ae7969f0516017f2413f17796670f7040725dd83fcff5689
COPY docker/scripts/install-conda.sh /tmp/install-conda.sh
RUN /tmp/install-conda.sh && rm -f /tmp/install-conda.sh


ENV PROJECT_NAME=sea-names
ENV PROJECT_ROOT=/opt/sea-names
ENV CONDA_ENV=sea-names

COPY docker/main/entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
COPY docker/scripts/install-dependencies.sh /tmp/install-dependencies.sh
RUN mkdir /tmp/envs
COPY environment.yml /tmp/envs/

RUN --mount=type=cache,id=sea-names,target=/opt/conda/pkgs --mount=type=cache,id=sea-names,target=/root/.cache/pip /tmp/install-dependencies.sh && rm -rf /tmp/envs /tmp/install-dependencies.sh


COPY docker/scripts/install-project.sh /tmp/install-project.sh

COPY sea_names $PROJECT_ROOT/sea_names
COPY tests $PROJECT_ROOT/tests
COPY .flake8 conftest.py setup.py README.rst requirements.txt requirements-dev.txt LICENSE HISTORY.rst $PROJECT_ROOT/

RUN --mount=type=cache,id=sea-names,target=/opt/conda/pkgs --mount=type=cache,id=sea-names,target=/root/.cache/pip /tmp/install-project.sh && rm -rf /tmp/install-project.sh

WORKDIR $PROJECT_ROOT/
