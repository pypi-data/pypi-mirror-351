FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

ENV UV_COMPILE_BYTECODE=1
ENV UV_NO_CACHE=1

RUN apt update && \
    apt install -y --no-install-recommends \
    build-essential \
    cmake \
    curl \
    gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY README.md /app/
COPY pyproject.toml /app/
RUN uv sync --no-install-project --no-dev
COPY src/opensymbiose /app/opensymbiose

EXPOSE 8000

CMD ["uv", "run", "opensymbiose/main.py"]
