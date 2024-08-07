FROM python:3.10.7

# Set the working directory for the container
WORKDIR /app

# Copy the requirements file into the container
COPY src/requirements.txt .

# Install Python dependencies
RUN apt-get update && apt-get install -y \
    libx11-6 libxext-dev libxrender-dev libxinerama-dev libxi-dev libxrandr-dev libxcursor-dev libxtst-dev tk-dev && \
    rm -rf /var/lib/apt/lists/*

# Install the dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the rest of the application code
COPY src/ /app/

# Ensure that the /app directory is writable
RUN chmod -R 777 /app

# Set the display environment variable
ENV DISPLAY=:0

EXPOSE 5002  # Certifique-se de expor a porta correta

# Run the application
CMD ["python3", "main.py"]
