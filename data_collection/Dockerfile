# Start with a lightweight Python base image
FROM python:3.9-slim

# Set working directory in the container
WORKDIR /app

# Install necessary utilities for downloading and installing Miniforge
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    xz-utils \
    && rm -rf /var/lib/apt/lists/*

# Download and install Miniforge (works for multiple architectures)
ENV CONDA_DIR=/opt/conda
RUN wget --quiet https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-$(uname -m).sh -O /tmp/miniforge.sh && \
    bash /tmp/miniforge.sh -b -p $CONDA_DIR && \
    rm /tmp/miniforge.sh

# Update PATH to include Conda
ENV PATH=$CONDA_DIR/bin:$PATH

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

# (Optional) Update Conda to ensure latest version
RUN conda update -n base -c defaults conda && conda clean -afy

# Copy the environment.yml and Python script into the container
COPY environment.yml .
COPY collection.py .

# Create the Conda environment using the environment.yml file
RUN conda env create -f environment.yml

# Activate the conda environment by setting PATH
ENV PATH /opt/conda/envs/document_processing/bin:$CONDA_DIR/bin:$PATH

# Ensure the working directory is set (in case the environment.yml changes it)
WORKDIR /app

# Run the script with arguments passed from docker run
ENTRYPOINT ["python", "-u", "collection.py"]
