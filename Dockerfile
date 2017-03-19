FROM debian:jessie

# Install OS dependencies
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get -yq dist-upgrade \
 && apt-get install -yq --no-install-recommends \
    wget \
    curl \
    bzip2 \
    ca-certificates \
    sudo \
    locales \
    git \
    vim \
    make \
    gcc \
    pkg-config \
    libffi-dev \
    build-essential \
    autoconf \
    autogen \
    automake \
    libtool \
    libltdl-dev \
 && apt-get clean

RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && locale-gen

# Configure the environment
ENV WORK_DIR /work
ENV CONDA_DIR /opt/conda
ENV PATH $CONDA_DIR/bin:$PATH
ENV SHELL /bin/bash
ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

RUN mkdir -p WORK_DIR

# Install conda
RUN cd /tmp && \
    mkdir -p $CONDA_DIR && \
    wget --quiet https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    /bin/bash Miniconda3-latest-Linux-x86_64.sh -f -b -p $CONDA_DIR && \
    rm Miniconda3-latest-Linux-x86_64.sh && \
    $CONDA_DIR/bin/conda config --system --add channels conda-forge && \
    $CONDA_DIR/bin/conda config --system --set auto_update_conda false && \
    conda clean -tipsy

# Install Jupyter Notebook
RUN conda install --quiet --yes \
    'notebook=4.4.*' \
    && conda clean -tipsy

EXPOSE 8888
WORKDIR /work

# Build micropython
RUN git clone http://github.com/micropython/micropython.git /work/micropython && \
    cd /work/micropython && \
    git submodule update --init && \
    make -C unix deplibs && \
    make -C unix

COPY . /work/mpkernel

