#!/bin/bash
set -euo pipefail

# Install Docker
dnf install -y docker
systemctl enable docker
systemctl start docker

# Minimal placeholder — proves Docker → Caddy → HTTPS chain before real image exists
docker run -d \
  --name backend \
  --restart unless-stopped \
  -p 127.0.0.1:${backend_port}:80 \
  traefik/whoami

# Write Caddyfile
mkdir -p /etc/caddy
cat > /etc/caddy/Caddyfile << 'CADDYEOF'
${domain} {
  reverse_proxy localhost:${backend_port}
}
CADDYEOF

# Run Caddy in Docker (host network so it can reach the backend container)
docker run -d \
  --name caddy \
  --restart unless-stopped \
  --network host \
  -v /etc/caddy:/etc/caddy \
  -v caddy_data:/data \
  caddy:2.11.2
