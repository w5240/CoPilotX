---
name: sysinfo
description: Query system information including CPU, memory, disk, network, and process details. Use when user needs to check system status, monitor resources, or get hardware information.
allowed-tools: Bash(uv run python ~/.openclaw/skills/sysinfo/sysinfo.py *)
---

# System Information Query

Quickly query system information including CPU, memory, disk, network, and running processes.

## Usage

### Get All System Info

Display comprehensive system information:

```bash
sysinfo all
```

### CPU Information

Get CPU details:

```bash
sysinfo cpu
```

### Memory Information

Get memory usage:

```bash
sysinfo memory
```

### Disk Information

Get disk usage:

```bash
sysinfo disk
```

### Network Information

Get network details:

```bash
sysinfo network
```

### Process Information

Get running processes:

```bash
sysinfo processes
```

### Quick Summary

Get a quick system summary:

```bash
sysinfo summary
```

## Examples

```bash
# Check all system info
sysinfo all

# Check CPU usage
sysinfo cpu

# Check memory usage
sysinfo memory

# Check disk space
sysinfo disk

# Check network status
sysinfo network

# Check running processes
sysinfo processes

# Quick summary
sysinfo summary
```

## Output Format

The skill returns system information in a human-readable format with key metrics highlighted.

## Platform Support

- macOS: Full support
- Linux: Full support
- Windows: Limited support (some features may not work)
