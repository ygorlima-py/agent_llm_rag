# Essa imagem builder é a base para todas as outras
FROM ghcr.io/astral-sh/uv:0.9.18-trixie-slim AS builder

# Ambiente
ENV UV_COMPILE_BYTECODE=1 \
  UV_LINK_MODE=copy \
  UV_PYTHON_PREFERENCE=only-managed \
  UV_NO_DEV=1 \
  UV_PYTHON_INSTALL_DIR=/python

# Atualiza e instala as dependencias essenciais do container, depois lima o cache
RUN apt-get update \
  && apt-get install -y --no-install-recommends build-essential \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* ;

# Instala o python no docker
RUN uv python install 3.12.12;

# Aqui criamos a pasta app no container e entramos nela igual
# fazemos com cd
WORKDIR /app

# cria o ambiente virtual e instala as dependências do projeto e 
# guarda elas no cache
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

# copia o projeto para a pasta app
COPY . /app

# Usa o cache salvo para fazer a sincronização do projeto
# Novamente
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen


################################################################################
# STAGE 2 - Estágio final

# Cria uma outra imagem 

FROM debian:trixie-slim AS development

ENV PYTHONUNBUFFERED=1

RUN apt-get update \
  && apt-get install -y --no-install-recommends build-essential \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* ;

# Define um usuário chamado python que será salvo o python
RUN groupadd --gid 1000 python \
  && useradd --uid 1000 --gid python --shell /bin/bash --create-home python ;

# Copia a pasta python do estágio anterior e da permissão ao usuário python
COPY --from=builder --chown=python:python /python /python

# Copia a pasta app do estágio anterior e da permissão ao usuário python
COPY --from=builder --chown=python:python /app /app

# coloca as pastas onde o sistema busca programas como o python em primeiro
ENV PATH="/app/.venv/bin:$PATH"

# Define o usuário da pasta app sendo python
USER python

# Aqui colocamos um comando para ser execultado
ENTRYPOINT []

# Aqui criamos a pasta app novamente no container e entramos nela igual
# fazemos com cd
WORKDIR /app

# Esse comando é execultado no ENTRYPOINT
CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8003", "--reload", "chatapp.main:app"]



