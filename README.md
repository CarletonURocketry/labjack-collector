# Labjack Collector

The labjack collector is a system that collects, logs and relays data over network from the labjack data collection system.

<https://labjack.com/blogs/faq/what-is-a-labjack>

Documentation of the labjack library can be found here: <https://support.labjack.com/docs/ljm-library-overview>

Labjack library examples: <https://github.com/labjack/labjack-ljm-python>

## Installation

Install the labjack support library for your OS here: <https://support.labjack.com/docs/ljm-software-installer-downloads-t4-t7-t8-digit>, for context, we have a labjack T7

Clone this repository

```shell
python3 -m venv .venv
```

```shell
pip install -r requirements.txt
```

## Systemd Service

To run the collector as a persistent service that starts on boot:

```shell
# Copy service file to systemd
sudo cp labjack-collector.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable on boot
sudo systemctl enable labjack-collector.service

# Start the service
sudo systemctl start labjack-collector.service
```

### Managing the Service

```shell
# Check status
sudo systemctl status labjack-collector.service

# Restart the service
sudo systemctl restart labjack-collector.service

# Stop the service
sudo systemctl stop labjack-collector.service

# View logs
journalctl -u labjack-collector.service -f
```
