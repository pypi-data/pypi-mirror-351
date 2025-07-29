# syntax=docker/dockerfile:1

ARG UBUNTU_MAJOR=22
ARG UBUNTU_VERSION=${UBUNTU_MAJOR}.04

# ======================================BART=======================================
FROM ubuntu:${UBUNTU_VERSION} AS bart_build
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
            vim \
            make \
            gcc \
            git \
            libfftw3-dev \
            liblapacke-dev \
            libpng-dev \
            libopenblas-dev
# This is better than apt-get installing git, but it doesn't work for older Docker
# ADD https://github.com/mrirecon/bart.git#v0.8.00 /bart
RUN git clone --depth 1 --branch v0.8.00 https://github.com/mrirecon/bart.git /bart
WORKDIR /bart
RUN make && PREFIX="" make install

# ======================================AFNI=======================================
# FROM ubuntu:${UBUNTU_VERSION} AS afni_build
FROM bart_build AS bart_afni_build
# ARG UBUNTU_MAJOR
# ARG UBUNTU_VERSION
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
            vim \
            tcsh \
            curl

# ENV UBUNTU_MAJOR=$UBUNTU_MAJOR
# Manually run setup scripts
# Part A (copied from afni setup)
# Getting add-apt-repository
# Fix time zone issue
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    rm -rf /var/lib/apt/lists/*
RUN add-apt-repository -y universe && \
    apt-get update && \
    apt-get install -y \
            tcsh xfonts-base libssl-dev       \
            python-is-python3                 \
            python3-matplotlib python3-numpy  \
            python3-flask python3-flask-cors  \
            python3-pil                       \
            gsl-bin libgsl-dev                \
            netpbm gnome-tweaks               \
            libjpeg62 xvfb xterm vim curl     \
            gedit evince eog                  \
            libglu1-mesa-dev libglw1-mesa     \
            libxm4 build-essential            \
            libcurl4-openssl-dev libxml2-dev  \
            libgfortran-11-dev libgomp1       \
            gnome-terminal nautilus           \
            firefox xfonts-100dpi             \
            r-base-dev cmake bc git           \
            libgdal-dev libopenblas-dev       \
            libnode-dev libudunits2-dev
RUN ln -s /usr/lib/x86_64-linux-gnu/libgsl.so.27 /usr/lib/x86_64-linux-gnu/libgsl.so.19

# Part B (copied from afni setup)
# Skip bootcamp install
# AFNI binaries
RUN curl -O https://afni.nimh.nih.gov/pub/dist/bin/misc/@update.afni.binaries && \
    tcsh @update.afni.binaries -package linux_ubuntu_16_64 -do_extras
ENV PATH=$PATH:/root/abin
# Skip other env install
# Skip R install



# ===================================FreeSurfer====================================
# FROM ubuntu:${UBUNTU_VERSION} AS freesurfer_build
FROM bart_afni_build AS bart_afni_freesurfer_build
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
            vim git wget tcsh xxd curl \
            build-essential gfortran \
            libblas-dev liblapack-dev \
            libxmu-dev libxmu-headers \
            libxi-dev libxt-dev \
            libx11-dev libglu1-mesa-dev
RUN wget https://surfer.nmr.mgh.harvard.edu/pub/dist/freesurfer/7.4.1/freesurfer_ubuntu22-7.4.1_amd64.deb
RUN apt update && apt install -y ./freesurfer_ubuntu22-7.4.1_amd64.deb
# COPY /usr/local/freesurfer/license.txt /usr/local/freesurfer/license.txt

# =====================================Python (uv)======================================
FROM bart_afni_freesurfer_build AS bart_afni_freesurfer_uv_build
# install uv
COPY --from=ghcr.io/astral-sh/uv:0.7.8 /uv /uvx /bin/

# =====================================Setup=======================================
# Install the project into `/app`
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT ["python", "entrypoint.py"]
