FROM node:22-bookworm-slim

USER root

# Install Python
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt /tmp/requirements.txt

# Install Python dependencies
RUN pip3 install --break-system-packages -r /tmp/requirements.txt

# Install n8n
RUN npm install -g n8n

# Create node user if missing and prepare n8n directory
RUN useradd -m -u 1000 node || true
RUN mkdir -p /home/node/.n8n && chown -R node:node /home/node

USER node

ENV N8N_USER_FOLDER=/home/node/.n8n

CMD ["n8n"]
