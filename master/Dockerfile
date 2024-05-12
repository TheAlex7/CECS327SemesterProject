# Use an official Python runtime as a base image
FROM python:3.8

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app 

# Install necessary python packages
RUN pip install -r requirements.txt

# Define environment variable
ENV NAME master

# Run master.py when the container launches
CMD python master.py
