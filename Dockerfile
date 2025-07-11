# Use a slim Python base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Streamlit application code
COPY . .

# Expose the default Streamlit port
EXPOSE 8501

# Command to run the Streamlit app with environment variables
# The actual environment variables will be passed during `docker run` on EC2
CMD ["streamlit", "run", "appfourthjuly.py", "--server.port=8501", "--server.address=0.0.0.0"]
