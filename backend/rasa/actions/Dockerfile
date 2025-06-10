FROM rasa/rasa-sdk:latest

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file
COPY requirements.txt ./

# Install the python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the actions code over to the 'actions' subdirectory inside the container
COPY . /app/actions 