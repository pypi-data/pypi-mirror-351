# syntax = docker/dockerfile:experimental
FROM mambaorg/micromamba:0.19.1
ARG PYTHON_VERSION 3.9
ENV DEBIAN_FRONTEND noninteractive
ENV LANG C.UTF-8

USER root

RUN apt-get update && apt-get install -y git && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

USER $MAMBA_USER

RUN micromamba install -y -n base -c conda-forge python=${PYTHON_VERSION} pre-commit

CMD ["pre-commit", "run", "--show-diff-on-failure", "--color=always", "--all-files"]
