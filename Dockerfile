FROM python:3.13-slim-bookworm AS base

# install poppler-utils
RUN apt update && apt upgrade -y && \
    apt install -y poppler-utils && \
    apt clean && rm -rf /var/lib/apt/lists/*

# Set the POPPLER_PATH environment variable dynamically
RUN POPPLER_PATH=$(dirname $(which pdftotext)) && echo "POPPLER_PATH=$POPPLER_PATH" >> /etc/environment
ENV POPPLER_PATH=$POPPLER_PATH
ENV PATH=$POPPLER_PATH:$PATH

# install uv 
COPY --from=ghcr.io/astral-sh/uv:0.4.24 /uv /bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# app directory is the current working directory
WORKDIR /app
COPY uv.lock pyproject.toml /app/

# install the dependencies
ENV DOCKER_BUILDKIT=1
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-install-project --no-dev

# copy the application to app directory 
COPY src /app/src
COPY run_app.py /app/run_app.py
COPY .env /app/.env
COPY .config /app/.config

# create a temp directory
RUN mkdir -p /app/temp

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 5001

# run the app
ENTRYPOINT [ "hypercorn", "run_app:app", "--bind", "0.0.0.0:5001" ]


