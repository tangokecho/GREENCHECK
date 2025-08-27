FROM python:3.11-slim

# System deps (build + WeasyPrint runtime)
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    # WeasyPrint deps
    libffi8 \
    libcairo2 \
    pango1.0-tools \
    libpango-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libpangocairo-1.0-0 \
    fonts-dejavu-core \
    # optional: wkhtmltopdf alternative fonts & utils
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Copy only dependency files first (better caching)
COPY apps/api/requirements.txt /workspace/apps/api/requirements.txt
RUN pip install --no-cache-dir -r apps/api/requirements.txt

# Copy the whole repo (so Alembic, templates, etc are available)
COPY . /workspace

ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

EXPOSE 8000

# Default command gets overridden by docker-compose
CMD ["bash", "-lc", "uvicorn apps.api.main:app --host 0.0.0.0 --port 8000"]
