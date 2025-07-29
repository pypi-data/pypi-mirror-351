# Peeky

A Minimal Port & Process Inspector - A cross-platform CLI tool to inspect and manage network ports and processes.

## Features

- 🔍 **peeky scan** - List open ports with process information
- ⚠️ **peeky conflicts** - Detect conflicting processes on ports
- 📊 **peeky stats** - View network statistics and summary
- 🧨 **peeky kill** - Kill processes by port or PID
- 🧼 **peeky clean** - Clean up zombie or idle port-bound processes
- 🌐 **peeky whois** - Look up information about IP addresses and domains
- 🔒 **peeky secure** - Identify security risks in network configuration

## Installation

### From PyPI (Recommended)

```bash
# Install from PyPI
pip install peeky

# Now you can use the 'peeky' command directly
peeky --help
```

### From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/peeky.git
cd peeky

# Install in development mode
pip install -e .

# Now you can use the 'peeky' command directly
peeky --help
```

### Manual Use (without installation)

If you prefer not to install, you can also use the included scripts directly:

#### Windows Users

```
# Run directly using the batch file
.\peeky.bat scan
.\peeky.bat conflicts
```

#### Linux/Mac Users

```bash
# Make the script executable
chmod +x peeky.py

# Run the script
./peeky.py scan
```

## Usage

### Scan for Open Ports

```bash
# List all open ports
peeky scan

# Filter by port
peeky scan --port 8080

# Show only TCP connections
peeky scan --tcp

# Filter by process name
peeky scan --filter node

# Show command that started process
peeky scan --command
```

### Detect Port Conflicts

```bash
# Find processes competing for the same ports
peeky conflicts
```

### View Network Statistics

```bash
# Display summary statistics and top processes/ports
peeky stats
```

### Kill Processes

```bash
# Kill by port number
peeky kill 8080

# Kill by PID
peeky kill 1234

# Force kill (SIGKILL)
peeky kill 8080 --force

# Skip confirmation prompts
peeky kill 1234 --yes
```

### Clean Up Idle Processes

```bash
# Find and clean up idle/zombie processes
peeky clean

# Just list the processes without cleaning
peeky clean --list

# Clean without confirmation
peeky clean --yes

# Force kill processes
peeky clean --force
```

### WHOIS Lookup

```bash
# Look up information about a domain
peeky whois example.com

# Look up information about an IP address
peeky whois 8.8.8.8

# Use only local resolution (no API calls)
peeky whois example.com --local
```

### Security Risk Analysis

```bash
# Identify potential security risks in network configuration
peeky secure
```

### Configure API Keys

```bash
# Set up the WHOIS API key (APILayer)
peeky config --set-whois-key

# Show configured API keys (masked)
peeky config --show-keys
```

## API Integration

Peeky uses the APILayer WHOIS API for enhanced domain lookups. To use this feature:

1. Get an API key from [APILayer WHOIS API](https://apilayer.com/marketplace/whois-api)
2. Configure your API key:
   ```bash
   peeky config --set-whois-key
   ```
   
Alternatively, you can set the API key as an environment variable:
```bash
# For Windows
set PEEKY_WHOIS_API_KEY=your_api_key_here

# For Linux/Mac
export PEEKY_WHOIS_API_KEY=your_api_key_here
```

## Requirements

- Python 3.7 or higher
- Dependencies:
  - rich >= 14.0.0
  - typer >= 0.16.0
  - psutil >= 7.0.0
  - click >= 8.2.1
  - requests >= 2.25.0

## Development

1. Clone the repository
2. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
3. Run tests:
   ```bash
   pytest
   ```

## License

MIT 