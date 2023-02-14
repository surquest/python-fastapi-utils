FROM python:3.11-slim AS base

# Copy local code to the container image.
ENV DIR_PROJECT /opt/project
ENV DIR_SRC /opt/project/src
ENV DIR_TEST /opt/project/test
RUN mkdir -p PROJECT_DIR
ENV HOME $PROJECT_DIR
WORKDIR $PROJECT_DIR

# Update pip
RUN pip install --upgrade pip

COPY /pyproject.toml /$PROJECT_DIR/pyproject.toml
COPY /README.md /$PROJECT_DIR/README.md

# Allow statements and log messages to immediately appear in the Cloud Run logs
ENV PYTHONUNBUFFERED True
ENV PYTHONPATH="${PYTHONPATH}:${DIR_SRC}:${DIR_TEST}"

# Install python packages
RUN pip install . --no-cache-dir

FROM base AS test

# Install python packages for testing
RUN pip install .[test] --no-cache-dir