FROM --platform=$BUILDPLATFORM python:3.10.8-slim as base
#FROM --platform=linux/amd64 python:3.10.8-slim as base

FROM base as builder

RUN apt-get -qq update \
    && apt-get install -y --no-install-recommends \
        wget g++ \
    && rm -rf /var/lib/apt/lists/*

ARG TARGETOS
ARG TARGETARCH
RUN echo ${TARGETOS}
RUN echo ${TARGETARCH}

# get packages
COPY requirements.txt .
RUN pip install -r requirements.txt

# Enable unbuffered logging
ENV PYTHONUNBUFFERED=1

WORKDIR /email_server

# Grab packages from builder
COPY --from=builder /usr/local/lib/python3.10/ /usr/local/lib/python3.10/

# Add the application
COPY . .

ENTRYPOINT [ "python", "replay.py" ]
