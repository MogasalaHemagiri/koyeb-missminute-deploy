# Use a lightweight Python base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install git, curl, and system dependencies
RUN apt-get update && \
    apt-get install -y git curl bash && \
    rm -rf /var/lib/apt/lists/*

# Install uv for fast package management
RUN pip install uv

# Clone your OpenClaw fork directly into the container
RUN git clone https://github.com/Rhodawk-AI/Missminute1.git /app/Missminute1

# Copy your wrapper scripts into the container
COPY . /app/wrapper

# Install your wrapper dependencies using uv system-wide
RUN uv pip install --system -r /app/wrapper/requirements.txt

# (Optional) If Missminute1 has its own requirements, install them with uv too:
# RUN uv pip install --system -r /app/Missminute1/requirements.txt

# Expose port 8000 for Koyeb's health checks
EXPOSE 8000

# Make the start script executable
RUN chmod +x /app/wrapper/start.sh

# Run the startup script
CMD ["/app/wrapper/start.sh"]
