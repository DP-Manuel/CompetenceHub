# Local disposable validation only; never install or run this image on the VPS.
FROM ubuntu:24.04@sha256:68ee22004a9109b44973313b02ff7b1de250f1de0f5ecb628d73f579aaff33ac
ENV DEBIAN_FRONTEND=noninteractive PIP_CONFIG_FILE=/dev/null
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-venv nginx systemd openssl ca-certificates postgresql-16 \
    && rm -rf /var/lib/apt/lists/*
RUN useradd --system --home /nonexistent --shell /usr/sbin/nologin competencehub
WORKDIR /work
CMD ["sleep", "infinity"]
