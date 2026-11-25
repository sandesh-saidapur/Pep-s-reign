# Reproducible environment: installs locked dependencies and runs the test suite.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

RUN pip install --no-cache-dir uv==0.4.18

WORKDIR /app
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
COPY tests ./tests
RUN uv sync --all-extras --frozen

COPY . .
CMD ["uv", "run", "pytest"]
