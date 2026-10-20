FROM python:3.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
COPY src ./src
RUN uv sync --frozen --no-dev
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8080
# Foundry/Event Hubs settings are passed at run time (see docs/DEPLOY.md); without them the app runs offline.
CMD ["uvicorn", "plc.api:app", "--host", "0.0.0.0", "--port", "8080"]
