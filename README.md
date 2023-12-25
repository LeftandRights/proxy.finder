# Proxy Tester

The Proxy Tester is a Python script designed to test and manage a list of proxy servers. It checks the validity and responsiveness of proxy servers obtained from various sources, allowing you to maintain an updated list of working proxies.

## Features

- **Proxy Testing**: Verifies the status and connectivity of the obtained proxy servers.
- **Proxy Management**: Manages a list of tested proxies and updates the list based on their performance.
- **Ngrok Integration**: Uses Ngrok to expose a local server for proxy testing.
- **Flask Web Interface**: Provides a simple web interface to view the tested proxies.

## Setup

### Prerequisites

- Python 3.6+
- `pyngrok`, `requests`, `Flask` Python libraries

### Installation

1. Clone or download the repository.

    ```bash
    git clone https://github.com/LeftandRights/proxy.finder.git
    ```

2. Install the required Python libraries.

    ```bash
    pip install pyngrok requests Flask
    ```

### Configuration

1. Open `config.yaml` to configure settings such as maximum workers, proxy timeout, and verbosity.

2. Update `proxyProvider` with URLs pointing to plain text lists of proxy addresses.

3. Ensure base64-encoded format for proxy URLs to bypass Replit restrictions.

## Usage

1. Run the script.

    ```bash
    python proxy_tester.py
    ```

2. Access the Flask web interface at `https://<repl_name>.<replit_username>.repl.co/` to view the tested proxies.

3. The script will continuously test and manage the proxies in the background.

## Notes

- Customize configurations based on your requirements and adjust maximum worker settings for performance.
