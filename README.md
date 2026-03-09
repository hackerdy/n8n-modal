# n8n-modal

Deploy [n8n](https://n8n.io) — the workflow automation platform — on [Modal.com](https://modal.com).

## Prerequisites

| Tool | Install |
|------|---------|
| Python 3.11+ | <https://python.org> |
| Modal CLI | `pip install modal` |
| Modal account | <https://modal.com/signup> |

## Quick start

```bash
# 1. Clone the repo
git clone https://github.com/hackerdy/n8n-modal.git
cd n8n-modal

# 2. Install dependencies
pip install -r requirements.txt

# 3. Authenticate with Modal (one-time)
modal setup

# 4. Test locally (ephemeral – stops when you Ctrl-C)
modal serve modal_app.py

# 5. Deploy to Modal (persistent HTTPS endpoint)
modal deploy modal_app.py
```

After deploying, Modal prints a URL like
`https://<your-workspace>--n8n-run-n8n.modal.run`.
Open it in your browser to access the n8n UI.

## Persistent storage

Workflows, credentials, and execution logs are stored in a
[Modal Volume](https://modal.com/docs/guide/volumes) named **`n8n-data`**.
It is created automatically on first deploy and survives redeployments.

## Configuration

Environment variables can be set directly in `modal_app.py` (in the `.env()`
block) or via a [Modal Secret](https://modal.com/docs/guide/secrets):

| Variable | Purpose | Default |
|----------|---------|---------|
| `N8N_PORT` | Port n8n listens on | `5678` |
| `N8N_HOST` | Bind address | `0.0.0.0` |
| `N8N_PROTOCOL` | Protocol reported to n8n | `https` |
| `N8N_BASIC_AUTH_ACTIVE` | Enable basic auth | _(off)_ |
| `N8N_BASIC_AUTH_USER` | Basic-auth username | – |
| `N8N_BASIC_AUTH_PASSWORD` | Basic-auth password | – |
| `WEBHOOK_URL` | Public URL for incoming webhooks | _(auto)_ |
| `DB_TYPE` | Database backend (`sqlite` / `postgresdb`) | `sqlite` |

### Adding secrets

```bash
modal secret create n8n-secrets \
  N8N_BASIC_AUTH_ACTIVE=true \
  N8N_BASIC_AUTH_USER=admin \
  N8N_BASIC_AUTH_PASSWORD=changeme
```

Then add `secrets=[modal.Secret.from_name("n8n-secrets")]` to the
`@app.function` decorator in `modal_app.py`.

## Architecture

```
Browser ──HTTPS──► Modal proxy ──HTTP──► n8n (port 5678)
                                              │
                                        Modal Volume
                                        (n8n-data)
```
