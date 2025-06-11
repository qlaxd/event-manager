FROM rasa/rasa-sdk:latest

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file
COPY requirements.txt ./

# Install the python dependencies with sudo to handle permission issues
USER root
RUN pip install --no-cache-dir -r requirements.txt

# Switch back to non-root user if needed
USER 1000

# Copy the actions code over to the 'actions' subdirectory inside the container
COPY . /app/actions 