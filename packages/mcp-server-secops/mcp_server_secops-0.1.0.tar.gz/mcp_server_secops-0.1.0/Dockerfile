# Etapa 1: instalar dependencias del proyecto con uv
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS uv

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev --no-editable

ADD . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable

# Etapa 2: imagen final con todas las tools instaladas
FROM python:3.12-slim-bookworm

WORKDIR /app

# Instala herramientas del sistema necesarias para pentesting
RUN apt-get update && apt-get install -y \
    nmap \
    hashcat \
    git \
    curl \
    wget \
    unzip \
    build-essential \
    default-jdk \
    libpcap-dev \
    && apt-get clean

# FFUF
RUN wget https://github.com/ffuf/ffuf/releases/download/v2.0.0/ffuf_2.0.0_linux_amd64.tar.gz && \
    tar -xvzf ffuf_2.0.0_linux_amd64.tar.gz && mv ffuf /usr/local/bin/

# sqlmap
RUN git clone https://github.com/sqlmapproject/sqlmap.git /opt/sqlmap

# nuclei, httpx, subfinder, tlsx, amass
RUN wget -qO - https://github.com/projectdiscovery/nuclei/releases/latest/download/nuclei_3.0.0_linux_amd64.zip | bsdtar -xvf- && \
    mv nuclei /usr/local/bin/
RUN wget -qO - https://github.com/projectdiscovery/httpx/releases/latest/download/httpx_1.6.3_linux_amd64.zip | bsdtar -xvf- && \
    mv httpx /usr/local/bin/
RUN wget -qO - https://github.com/projectdiscovery/subfinder/releases/latest/download/subfinder_2.7.6_linux_amd64.zip | bsdtar -xvf- && \
    mv subfinder /usr/local/bin/
RUN wget -qO - https://github.com/projectdiscovery/tlsx/releases/latest/download/tlsx_1.1.2_linux_amd64.zip | bsdtar -xvf- && \
    mv tlsx /usr/local/bin/

RUN wget https://github.com/OWASP/Amass/releases/latest/download/amass_linux_amd64.zip && \
    unzip amass_linux_amd64.zip && mv amass_linux_amd64/amass /usr/local/bin/

# ipinfo
RUN wget -qO - https://github.com/projectdiscovery/ipinfo/releases/latest/download/ipinfo_1.1.5_linux_amd64.zip | bsdtar -xvf- && \
    mv ipinfo /usr/local/bin/

# dirsearch
RUN git clone https://github.com/maurosoria/dirsearch.git /opt/dirsearch

# xsstrike
RUN git clone https://github.com/s0md3v/XSStrike.git /opt/xsstrike

# Copia el entorno y los paquetes instalados
COPY --from=uv /root/.local /root/.local
COPY --from=uv --chown=app:app /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH"

COPY . /app

# Ejecuta el servidor MCP (ajústalo si cambias el nombre del entrypoint)
ENTRYPOINT ["mcp-server-secops"]