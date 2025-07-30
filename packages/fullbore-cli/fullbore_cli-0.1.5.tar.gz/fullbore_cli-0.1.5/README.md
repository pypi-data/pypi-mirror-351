# fullbore-cli

**Full Bore CLI** — a command-line tool to simplify internal infrastructure operations like server access, config management, and deployments.

---

## Features

* 🔎 List available servers from a shared config file
* 🔐 One-command SSH access to internal machines
* 🚀 Redeploy services via Git and Docker with one command
* ⚙️ Easily customizable and extensible with new commands

---

## Installation

```bash
pip install fullbore-cli
```

---

## Usage

List all configured servers:

```bash
fbcli list-servers
```

SSH into a server:

```bash
fbcli ssh fb-web-1
```

You can also use the shortcut:

```bash
fb ssh fb-web-2
```

Redeploy a service (runs `git pull && docker compose down && up -d`):

```bash
fbcli redeploy fb-web-1 /home/fbadmin/myapp
```

---

## Configuration

On first run, you'll be prompted for the location of your `config.fb` file.

You can:

* Press Enter to auto-create a default one at:

  * `~/.fbcli/config.fb` (Linux/macOS)
  * `C:\Users\yourname\.fbcli\config.fb` (Windows)

* Or paste a full path like:

  * Windows: `C:\Users\you\Documents\config.fb`
  * macOS/Linux: `/Users/you/config.fb`

The file should look like:

```python
servers = {
    "fb-web-1": {"host": "192.168.1.112", "user": "fbadmin"},
    "fb-rp": {"host": "192.168.1.186", "user": "fbadmin"},
}
```

Your chosen path will be saved automatically for future runs.

---

## Development Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

---

## 🛠 Feature Sketchpad (Not Yet Implemented)

Ideas for future enhancements to `fbcli`. These are still in exploration but show where the tool is headed:

### 🔧 `fb run "<command>" -s <server>`

* Run shell commands on any registered server
* Example: `fb run "docker ps" -s fb-web-1`
* Optional working directory or user override

### 🚀 `fb deploy <project> --server <alias>`

* Deploy preconfigured projects to known paths
* Example: `fb deploy myapp --server staging`
* Could support Docker, Git pulls, symlink swaps, etc.

### 🧰 `fb tool <task> [--args]`

* Trigger remote scripts or system automation
* Example: `fb tool ssl-renew -s fb-rp`
* Example: `fb tool add-domain myapp.local --server fb-rp`
* Powered by server-side `fbtools` scripts or dockerized tool containers

### 🧪 Other possible commands

* `fb logs <project>` — tail logs via SSH
* `fb open <project>` — open the app in browser
* `fb scale <project>` — scale services/containers
* `fb db shell <project>` — open a DB shell inside container
* `fb config reset` — force re-selecting a config file

---

