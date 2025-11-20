FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Image environment configuration
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_TOOL_BIN_DIR=/usr/local/bin \
    XDG_CACHE_HOME=/tmp/.cache \
    UV_CACHE_DIR=/tmp/.cache/uv \
    DOCKER_CONTAINER=true

WORKDIR /app

# Install dependencies using lockfile via BuildKit mounts (no project install)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=/app/uv.lock \
    --mount=type=bind,source=pyproject.toml,target=/app/pyproject.toml \
    uv sync --locked --no-install-project --no-dev

RUN mkdir -p /tmp/.cache/uv && chown -R 1000:1000 /tmp/.cache

COPY src ./src

# Ensure the user owns the source code so it can write pycache or instance folders if needed
RUN chown -R 1000:1000 /app/src

USER 1000:1000

EXPOSE 5000

CMD ["uv", "run", "src/app.py"]
