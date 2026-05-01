#!/bin/bash
set -euo pipefail

# Expand root partition and filesystem to fill the EBS volume
# AL2023 cloud-init may already handle this; || true prevents set -e from aborting if NOCHANGE
growpart /dev/nvme0n1 1 || true
xfs_growfs / || true

# Install Docker
dnf install -y docker
systemctl enable docker
systemctl start docker

# Install, enable, and start SSM agent (not pre-installed on AL2023)
dnf install -y amazon-ssm-agent
systemctl enable amazon-ssm-agent
systemctl start amazon-ssm-agent

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
