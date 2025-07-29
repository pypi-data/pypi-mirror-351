# dnscheck

🔎 A Python module and CLI tool to check DNS health, resolve domains, inspect and configure system DNS settings — made for sysadmins, developers, and network engineers.

---

## 📦 Installation

Install from [PyPI](https://pypi.org/project/dnscheck):

```bash
pip install py-dnscheck
```

## 🚀 Features
🌐 Resolve domains to IP addresses
📡 Check DNS and network health with ping
🧠 Get system-configured DNS nameservers
🧭 Query authoritative DNS servers (NS records)
⚙️ Change system DNS configuration (Linux only)
🧪 CLI and Python module support

## 🧑‍💻 Usage
### 📘 As a Python Module
``` python
from dnscheck import resolve, check_dns_health, get_nameservers, get_authoritative_dns, set_dns

# Resolve a domain
ips = resolve("example.com")

# DNS health check
healthy = check_dns_health("google.com")

# Get current nameservers
dns_servers = get_nameservers()

# Get authoritative DNS
authoritative = get_authoritative_dns("example.com")

# Change system DNS (Linux only)
set_dns(["8.8.8.8", "1.1.1.1"])

```

### 💻 As a CLI Tool
```Bash
# Resolve a domain
dnscheck resolve example.com

# Check DNS health
dnscheck health

# Get current DNS servers
dnscheck nameservers

# Get authoritative DNS
dnscheck authoritative example.com

# Set DNS (Linux only)
dnscheck setdns 8.8.8.8 1.1.1.1
```

## 📜 License
MIT License.

## 🧑‍💼 Author
[Santhosh Murugesan](https://geeks.santhoz.in/)
A full-stack network engineer building tools and writing blogs to make life easier for fellow engineers.
