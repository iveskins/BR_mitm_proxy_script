# Project Title

## Description

This project is designed to capture job details from your Bizreach inbox as you browse. It utilizes `mitmproxy`, an interactive HTTPS proxy, to intercept and process web traffic from specific URLs. The parsed job details are then saved to a SQLite database for easy access and analysis.

## Prerequisites

Before you begin, ensure you have the following installed:
- Python (version 3.10 or newer)
- pipx
- mitmproxy

## Installation

### Step 1: Install Python

Download and install Python (3.10 or newer) from the [Python website](https://www.python.org/downloads/).

### Step 2: Install pipx

Install `pipx` for isolated Python package management. Instructions are available on the [pipx installation page](https://pipx.pypa.io/latest/installation/).

### Step 3: Install mitmproxy

Install `mitmproxy` via pipx:

```bash
pipx install mitmproxy
```

### Step 4: Inject Dependencies

Inject the required Python packages into the mitmproxy environment:

```bash
pipx inject mitmproxy BeautifulSoup4
pipx inject mitmproxy logging
pipx inject mitmproxy bs4
```

## Running the Script

To run the script with `mitmproxy`, use:
If its not in you path it should be
```bash
/home/<user>/.local/bin/mitmproxy -s capture_and_parse_response.py
```

Replace `capture_and_parse_response.py` with your script's path if different.

## Using mitmproxy

1. **Configure mitmproxy**: After installation, configure your browser to use `mitmproxy` as its HTTP/HTTPS proxy. The default address is usually `127.0.0.1` (localhost) with port `8080`.

2. **Install mitmproxy's Root Certificate**: For HTTPS interception, install the root certificate generated by `mitmproxy`. Refer to the [official documentation](https://docs.mitmproxy.org/stable/concepts-certificates/) for guidance on installing the certificate.

3. **Browser Plugin**: To easily switch traffic through `mitmproxy`, consider using a browser plugin like the Container Proxy extension in Firefox. This allows you to redirect only specific tabs or containers through the proxy.

4. **Browsing Bizreach Inbox**: As you browse through your Bizreach inbox, `mitmproxy` captures the job details from the pages you visit and stores them in a SQLite database. This process happens seamlessly in the background.

## Project Specifics

This project is specifically tailored to capturing and storing job postings from Bizreach. As you navigate through different job listings in your inbox, the script extracts relevant information and saves it for later review and analysis. The SQLite database serves as a convenient and efficient way to store and access this data.


## Next step.
I wanted to make this so i could then extraxt the jobs details easily into a Notion table or google spread sheet. This way I can compare opporunities better. and get and overview on what out there, and track my applications if I make them.
I tried making another script to use cahtgpt functioncalling to extract more rich fields from the text data into a more details json schema. but it has been very hit and miss, and most me $10 already in api calls just testing .

