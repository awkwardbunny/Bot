FROM ghcr.io/astral-sh/uv:debian

WORKDIR /app

COPY pyproject.toml uv.lock main.py ./
RUN uv sync --no-dev

CMD ["uv", "run", "main.py"]
