FROM python:3.14.5-slim-bookworm

ARG NEXUS_PYPI_INDEX_URL

ENV SERVICE_NAME="tg_bot"
ENV SHARED_DIR="shared"
ENV HOME="/app"
ENV PYTHONPATH=$HOME

RUN groupadd -g 999 appuser && \
    useradd -u 999 -m -g appuser -s /bin/bash appuser && \
    mkdir -p ${HOME} && chown appuser:appuser $HOME

WORKDIR ${HOME}

RUN apt-get update && apt-get install -y curl build-essential netcat-openbsd \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install -i "${NEXUS_PYPI_INDEX_URL:-https://pypi.org/simple}" --disable-pip-version-check --no-cache-dir poetry==2.2.1 \
    && rm -rf /var/lib/apt/lists/* && poetry config virtualenvs.create false

COPY --chown=appuser:appuser services/${SERVICE_NAME}/src/pyproject.toml services/${SERVICE_NAME}/src/poetry.lock* ./

RUN poetry install --only main

COPY --chown=appuser:appuser services/${SERVICE_NAME} ./services/${SERVICE_NAME}
COPY --chown=appuser:appuser services/${SHARED_DIR} ./services/${SHARED_DIR}

RUN chown -R appuser:appuser $HOME

USER appuser

CMD ["python", "-m", "services.tg_bot.src.main"]
