"""
Deploy n8n on Modal.com

Usage:
    modal deploy modal_app.py       # deploy to Modal (persistent)
    modal serve modal_app.py        # run ephemerally for testing
"""
import subprocess

import modal

app = modal.App("n8n")

# ---------------------------------------------------------------------------
# Persistent volume – stores n8n workflows, credentials and execution logs
# ---------------------------------------------------------------------------
n8n_volume = modal.Volume.from_name("n8n-data", create_if_missing=True)

# ---------------------------------------------------------------------------
# Container image – official n8n image, Python added for Modal compatibility
# ---------------------------------------------------------------------------
n8n_image = modal.Image.from_registry(
    "n8nio/n8n:latest",
    add_python="3.11",
).env(
    {
        # n8n listens on this port inside the container
        "N8N_PORT": "5678",
        # Bind to all interfaces so Modal's proxy can reach it
        "N8N_HOST": "0.0.0.0",
        # Tell n8n it is served over HTTPS (Modal terminates TLS)
        "N8N_PROTOCOL": "https",
        # Disable diagnostics data collection (optional, remove to enable)
        "N8N_DIAGNOSTICS_ENABLED": "false",
    }
)


# ---------------------------------------------------------------------------
# Web endpoint
# ---------------------------------------------------------------------------
@app.function(
    image=n8n_image,
    # Mount persistent volume at n8n's default data directory
    volumes={"/home/node/.n8n": n8n_volume},
    # Allow many concurrent requests (n8n handles them internally)
    allow_concurrent_inputs=100,
    # Keep the container alive for up to 1 hour of inactivity
    timeout=3600,
    # Increase memory for larger workflow executions
    memory=1024,
)
@modal.web_server(5678)
def run_n8n():
    """Start the n8n server inside the Modal container."""
    proc = subprocess.Popen(["n8n", "start"])
    proc.wait()
