FROM node:22-bookworm-slim

USER root

RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages pymupdf pdfplumber
RUN npm install -g n8n

RUN useradd -m -u 1000 node || true
RUN mkdir -p /home/node/.n8n && chown -R node:node /home/node

USER node

ENV N8N_USER_FOLDER=/home/node/.n8n

CMD ["n8n"]

