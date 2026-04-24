#!/bin/bash
set -euo pipefail

# Install Docker
dnf install -y docker
systemctl enable docker
systemctl start docker

# Create hello world placeholder (served by python3 until FastAPI is deployed)
mkdir -p /var/www
cat > /var/www/index.html << 'HTMLEOF'
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Infusethink Backend</title>
</head>
<body>
  <h1>Hello HTTPS World! 🎉</h1>
  <p>Caddy + Let's Encrypt working on ${domain}</p>
</body>
</html>
HTMLEOF

# Start simple HTTP server on backend port (placeholder until FastAPI)
cd /var/www
nohup python3 -m http.server ${backend_port} &

# Write Caddyfile
mkdir -p /etc/caddy
cat > /etc/caddy/Caddyfile << 'CADDYEOF'
${domain} {
  reverse_proxy localhost:${backend_port}
}
CADDYEOF

# Run Caddy in Docker (host network so it can reach the local python server)
docker run -d \
  --name caddy \
  --restart unless-stopped \
  --network host \
  -v /etc/caddy:/etc/caddy \
  -v caddy_data:/data \
  caddy:latest
