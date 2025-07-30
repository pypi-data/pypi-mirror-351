FROM ghcr.io/astral-sh/uv:python3.12-alpine

LABEL \
  org.opencontainers.image.source="https://github.com/vs4vijay/espresso-mcp" \
  org.opencontainers.image.authors="vs4vijay@gmail.com" \
  org.opencontainers.image.title="Espresso MCP" \
  org.opencontainers.image.description="MCP Server for Android Espresso Test Framework" \
  org.opencontainers.image.licenses="MIT"

# Settings for faster container start
ENV UV_COMPILE_BYTECODE=0 UV_PYTHON_DOWNLOADS=0 UV_LINK_MODE=copy

COPY pyproject.toml uv.lock /app/

COPY LICENSE README.md server.py /app/

WORKDIR /app

RUN uv sync --frozen --no-dev

CMD ["uv", "run", "--frozen", "--no-dev", "espresso-mcp"]
# CMD ["uv", "tool", "run", "espresso-mcp"]