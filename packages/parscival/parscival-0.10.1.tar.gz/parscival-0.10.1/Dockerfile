# Created by Philippe Breucker

# Stable base image to ensure consistency across builds
FROM python:3.10-bookworm


# Update the package list and install required system packages in a single RUN
RUN apt-get update && apt-get install -y \
    libhdf5-dev \
    git && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip and setuptools to the latest version
RUN pip install -U pip setuptools

# Install tox
RUN pip install -U tox

# Create the application directory
RUN mkdir /app

# Set the working directory
WORKDIR /app

# Clone the Parscival repository
RUN git clone https://gitlab.com/cortext/cortext-methods/parscival.git

# Set the working directory to Parscival
WORKDIR /app/parscival

# Install the package in editable mode
RUN pip install -e .

# Build the package using tox
RUN tox -e build

# Set the default command to start a bash shell
CMD ["/bin/bash"]
