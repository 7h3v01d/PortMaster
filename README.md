# Portmaster (Python) — CLI + PyQt6 GUI for Port / Connection Management

**Portmaster** is a small Python toolkit for inspecting active network connections and performing common “port hygiene” actions from either:
- a **CLI** (argparse), or
- a **PyQt6 GUI** with dedicated tabs for day-to-day workflows.

Under the hood it uses `psutil` for connection/process inspection and Windows `netsh advfirewall` rules for port block/unblock + “reserve port for an executable” style allow-rules. :contentReference[oaicite:0]{index=0} :contentReference[oaicite:1]{index=1} :contentReference[oaicite:2]{index=2}

> ⚠️ **Safety note**: This project can terminate processes and modify firewall rules. Use it on machines you control and understand the impact of blocking ports or killing PIDs.

---

## Features

### Connection inspection
- List active TCP/UDP connections with protocol, local/remote endpoints, status, PID, and process name. :contentReference[oaicite:3]{index=3}
- Save a formatted snapshot of connections to a file. :contentReference[oaicite:4]{index=4}

### Port actions
- Check whether a port is currently in use. :contentReference[oaicite:5]{index=5}
- Kill a process by PID (with explicit confirmation). :contentReference[oaicite:6]{index=6}
- Block / unblock a port via Windows Firewall rules (`netsh advfirewall`). :contentReference[oaicite:7]{index=7}

### Server utilities
- Start a simple TCP/UDP server bound to a chosen port and verify it is actually bound. :contentReference[oaicite:8]{index=8}
- Stop the running server instance. :contentReference[oaicite:9]{index=9}

### Port “reservation” (Windows firewall allow-rule + config)
- Reserve a port for a specific executable path (writes `port_reservations.json`). :contentReference[oaicite:10]{index=10}
- Release a reserved port (removes firewall rule + updates config). :contentReference[oaicite:11]{index=11}

### GUI (PyQt6)
A tabbed interface with:
- **Connections**: list + save
- **Port Management**: check port / kill PID / block-unblock
- **Server**: start/stop
- **Reservations**: reserve/release  
:contentReference[oaicite:12]{index=12} :contentReference[oaicite:13]{index=13}

### Tests
Includes pytest-based tests for:
- core logic (with mocking for system calls) :contentReference[oaicite:14]{index=14}
- cleanup helper script :contentReference[oaicite:15]{index=15}
- GUI interactions using pytest-qt style patterns :contentReference[oaicite:16]{index=16}
- ZeroMQ pub/sub simulation scenarios (optional / integration-style) :contentReference[oaicite:17]{index=17}

---

## Project layout

Typical files in this repo:

- `core.py` — `PortManagerCore` implementation (connections/ports/firewall/server/reservations) :contentReference[oaicite:18]{index=18}  
- `cli.py` — CLI entrypoint with subcommands (argparse) :contentReference[oaicite:19]{index=19}  
- `gui.py` — PyQt6 GUI frontend (`PortManagerGUI`) :contentReference[oaicite:20]{index=20}  
- `cleanup_ports.py` — helper script to terminate processes holding common ports + remove firewall rules :contentReference[oaicite:21]{index=21}  
- `tests/` — `test_core.py`, `test_gui.py`, `test_cleanup.py`, `test_zeromq.py`, plus `conftest.py` fixtures :contentReference[oaicite:22]{index=22}

Runtime-generated files (created next to `core.py` by default):
- `port_logs.txt` — activity log :contentReference[oaicite:23]{index=23}
- `port_reservations.json` — port reservation config :contentReference[oaicite:24]{index=24}

---

## Requirements

Core runtime:
- Python 3.x
- `psutil`
- `pyzmq` (only if you use the ZeroMQ simulation utilities) :contentReference[oaicite:25]{index=25}

GUI:
- `PyQt6`

Tests:
- `pytest`
- `pytest-qt` (for GUI tests)
- `pytest-timeout` (used by the ZeroMQ scenario tests) :contentReference[oaicite:26]{index=26}

Quick install (example):
```bash
pip install psutil pyzmq PyQt6 pytest pytest-qt pytest-timeout
```
Usage
CLI
Run:

```bash
python cli.py --help
```
Available commands (high level):

- list
- check-port <port>
- kill <pid>
- block <port> <TCP|UDP>
- unblock <port> <TCP|UDP>
- start-server <port> <TCP|UDP>
- stop-server
- reserve <port> <TCP|UDP> --exe-path <path>
- release <port>
- save <filename> 

Confirmation gating: potentially destructive commands require confirmation, either by:

- passing -y/--yes, or
- letting the command return “Confirmation required…” (depending on how you’re invoking it). 

## Examples:


### List active network connections
```bash
python cli.py list
```
### Check if port 8080 is in use
```bash
python cli.py check-port 8080
```
### Block inbound TCP port 8080 (Windows Firewall) with auto-confirm
```bash
python cli.py -y block 8080 TCP
```
### Reserve TCP 8888 for a specific executable
```bash
python cli.py -y reserve 8888 TCP --exe-path "C:\Windows\System32\notepad.exe"
```
### Save connection snapshot to a file
```bash
python cli.py save connections.txt
```

GUI
Run:

```bash
python gui.py
```
You’ll get a tabbed window:

- Connections tab: list connections into a sortable table + save to file 
- Port Management tab: check port / kill PID / block-unblock 
- Server tab: start/stop TCP/UDP listener 
- Reservations tab: reserve/release by port + exe path 

### Cleanup helper

cleanup_ports.py is a convenience script to:

- terminate processes holding a set of ports, and
- delete matching firewall rules for both TCP and UDP. 

Run:
```bash
python cleanup_ports.py
```

## Running tests
From the repo root:

```bash
pytest -q
```
Notes:

- Many tests mock system dependencies (psutil, subprocess, file I/O) to remain deterministic and safe. 
- GUI tests rely on pytest-qt. 
- ZeroMQ scenario tests are longer-running and include timeouts. 
  
## Platform notes

- Firewall features are Windows-oriented (via netsh advfirewall). 
- Connection listing via psutil is cross-platform, but process naming and permissions can vary.

## License
Choose a license that matches how you want others to use this.
If you’re unsure, MIT is the common “keep it simple” default for small utilities.
