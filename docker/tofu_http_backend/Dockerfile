FROM python:3.13-alpine AS base
ENV PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1

FROM base AS builder

WORKDIR /wheels

COPY ./conf/requirements /wheels/requirements/
RUN pip install -U pip && pip wheel --no-cache-dir -r ./requirements/development.txt


FROM base AS production

COPY --from=builder /wheels /wheels
RUN pip install -U pip \
        && pip install --no-cache-dir -r /wheels/requirements/development.txt -f /wheels \
        && rm -rf /wheels

COPY ./src /app

RUN adduser -D appuser
RUN chown -R appuser /app

USER appuser

WORKDIR /app
