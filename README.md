# Turboscan 🐱

An ultra-fast, stable, and lightweight asynchronous TCP port scanner written in Python. Featuring structured console outputs, a custom cat-themed ASCII UI, and native output logging to a custom file format.

## Features

- **High-Performance Asyncio:** Leverages non-blocking network sockets for extreme speeds without thread-scheduling overhead.
- **Custom Aesthetic:** Clean terminal output styled with colorama and a cat-themed ASCII banner.
- **Verbose Mode (-v):** Real-time monitoring of connection attempts.
- **Structured Reports (-oN):** Exports clean scan results directly into a custom .turboscan report format.

## Installation

Clone the repository and install the minimal dependencies:

git clone https://github.com/l4st98/turboscan.git
cd turboscan
pip install -r requirements.txt

## Requirements

The project uses only one external helper library for native OS terminal styling:
- colorama

## CLI Usage & Flags

python turboscan.py --ip <TARGET> [FLAGS]

| Flag | Description | Default |
| :--- | :--- | :--- |
| --ip | [Required] Target IPv4 address or domain name. | *None* |
| -p, --ports | Port list or range to scan (e.g., 22,80,443-1000). | 1-1024 |
| -c, --concurrency | Max simultaneous TCP connections to open. | 1000 |
| -t, --timeout | Max socket connection wait time in seconds. | 1.0 |
| -v, --verbose | Print every connection attempt in real-time. | False |
| -oN | Output results to a clean <filename>.turboscan report. | *None* |

### Quick Examples

#### Scan common ports on scanme.nmap.org with real-time logging:
python turboscan.py --ip scanme.nmap.org -p 22,80,443 -v

#### Run an aggressive full port scan and save the output:
python turboscan.py --ip 192.168.1.1 -p 1-65535 -c 2000 -t 0.5 -oN home_router

## License

This project is licensed under the MIT License - see the LICENSE file for details.

Developed with 💻 by l4st
