# Use Python as base image
FROM python:3.8

# Set working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install necessary python packages
RUN pip install -r requirements.txt

# Define environment variable
ENV NAME node

# Run node.py when the container launches
CMD python food_network.py
