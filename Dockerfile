FROM astral/uv:python3.14-trixie-slim

WORKDIR /code

# Optimize uv behavior for containers
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_DEV=1

# Install dependencies first using cache mounts
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

# Copy the rest of the application code and perform the final sync
COPY . /code/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

# Place the virtual environment's binaries at the front of PATH
ENV PATH="/code/.venv/bin:$PATH"

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]