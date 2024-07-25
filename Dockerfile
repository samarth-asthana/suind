# Use a pre-built GDAL image
FROM osgeo/gdal:alpine-small-3.1.0

# Set the working directory
WORKDIR /app

# Copy the application files
COPY . .

# Install any required dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip

# Install Python dependencies if applicable
RUN pip3 install -r requirements.txt

# Define the command to run your application
CMD ["python3", "your_script.py"]
