import inspect


def generate_caddyfile(domain: str, backend_port: int) -> str:
    """
    Generate a Caddyfile configuration for the given domain.

    Args:
        domain: The domain name to configure (e.g., "infuseth.ink")
        backend_port: The port on which the backend is running

    Returns:
        A string containing the Caddyfile configuration.
    """
    return f"""
        {domain} {{
            reverse_proxy localhost:{backend_port}
        }}
    """.rstrip()


def generate_user_data(domain: str, backend_port: int = 8000) -> str:
    """
    Generate a user data script to run Caddy in Docker and set up a hello world server.

    Args:
        domain: The domain name to configure (e.g., "backstage.infuseth.ink")
        backend_port: The port on which the backend is running (default: 8000)

    Returns:
        A string containing the user data script.
    """
    caddyfile_content = generate_caddyfile(domain, backend_port)

    return inspect.cleandoc(f"""\
        #!/bin/bash
        # Install Docker
        dnf install -y docker
        systemctl enable docker
        systemctl start docker

        # Create hello world server
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
            <h1>Hello HTTPS World! 🎉 Whatta pain debugging this 😬</h1>
            <p>Caddy + Let's Encrypt working on {domain}</p>
        </body>
        </html>
        HTMLEOF

        # Start simple HTTP server
        cd /var/www
        nohup python3 -m http.server {backend_port} &

        # Create Caddyfile
        mkdir -p /etc/caddy
        cat > /etc/caddy/Caddyfile << 'CADDYEOF'
        {caddyfile_content}
        CADDYEOF

        # Run Caddy in Docker
        docker run -d \\
          --name caddy \\
          --restart unless-stopped \\
          --network host \\
          -v /etc/caddy:/etc/caddy \\
          -v caddy_data:/data \\
          caddy:latest
    """)
