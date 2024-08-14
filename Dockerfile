# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Define environment variables for DB credentials
ENV DB_USERNAME=your_username
ENV DB_PASSWORD=your_password
ENV DB_HOST=your_azure_mysql_host
ENV DB_NAME=your_database_name

# The rest of the Dockerfile remains the same


# Run the application
CMD ["flask", "run"]
