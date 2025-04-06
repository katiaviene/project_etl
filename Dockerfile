# Use Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy the script into the container
COPY . /app/



# Install necessary libraries
RUN python3 -m venv /venv

# Activate the virtual environment and install the dependencies
RUN /venv/bin/pip install --upgrade pip
RUN /venv/bin/pip install -r requirements.txt
ENV PATH="/venv/bin:$PATH"
# Set command to run the Python script
CMD ["python", "main.py"]
