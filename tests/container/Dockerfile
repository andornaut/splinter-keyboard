ARG NODE_VERSION=24.21.0
ARG PYTHON_VERSION=3.12
FROM node:${NODE_VERSION} AS node
FROM koalaman/shellcheck:v0.11.0 AS shellcheck
FROM python:${PYTHON_VERSION}
COPY --from=shellcheck /bin/shellcheck /usr/local/bin/shellcheck
COPY --from=node /usr/local /opt/node
ENV PATH="/opt/node-deps/node_modules/.bin:/opt/node/bin:/opt/venv/bin:${PATH}" \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
COPY package.json package-lock.json /opt/node-deps/
RUN cd /opt/node-deps && HUSKY=0 npm ci --no-audit --no-fund && chmod -R a+rX /opt/node-deps
COPY requirements-dev.txt /opt/check/requirements-dev.txt
RUN python -m venv /opt/venv && /opt/venv/bin/python -m pip install -r /opt/check/requirements-dev.txt
COPY tests/container/check /opt/check/run
WORKDIR /work
USER 19001:19001
