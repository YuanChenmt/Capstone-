# Use an official lightweight Python image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the necessary files to the container
COPY requirements.txt ./
COPY app.py ./
COPY .env ./
COPY pandas_operations.py ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the Gradio port (default is 7860)
EXPOSE 7860

# Run the Gradio app
CMD ["python", "app.py"]
