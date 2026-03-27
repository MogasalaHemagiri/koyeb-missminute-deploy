# Use a lightweight Python base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# 1. Install system dependencies (git, curl, bash)
RUN apt-get update && \
    apt-get install -y git curl bash && \
    rm -rf /var/lib/apt/lists/*

# 2. Install Node.js 22.x (Required by OpenClaw's package.json)
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs

# 3. Install pnpm (OpenClaw's specific package manager)
RUN npm install -g pnpm@10.32.1

# 4. Install uv for fast Python package management
RUN pip install uv

# 5. Clone your OpenClaw fork directly into the container
RUN git clone https://github.com/Rhodawk-AI/Missminute1.git /app/Missminute1

# 6. Install OpenClaw dependencies ONLY (Agent compiles assets automatically at runtime)
WORKDIR /app/Missminute1
RUN pnpm install


# 7. Move back to the main app directory and copy the Telegram bot wrapper files
WORKDIR /app
COPY . /app/wrapper

# 8. Install the Python dependencies for the bot
RUN uv pip install --system -r /app/wrapper/requirements.txt

# 9. Expose port 8000 for Koyeb's health checks
EXPOSE 8000

# 10. Make the start script executable
RUN chmod +x /app/wrapper/start.sh

# Run the background FastAPI server and foreground Telegram bot
CMD ["/app/wrapper/start.sh"]
