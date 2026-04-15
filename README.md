# Drone Secure Video System

Secure real-time video transmission system between a Raspberry Pi-based drone platform and a ground station PC using ROS 2 Humble, GStreamer, SRT, Tailscale VPN, and RTT monitoring.

## Project Objective

The objective of this project is to design, implement, and validate a secure real-time video transmission system for drone applications. The system must provide:

- low-latency video streaming
- encrypted communication
- stable transmission over WiFi and 4G
- experimental validation with network performance metrics
- compatibility with embedded platforms such as Raspberry Pi

## Technologies Used

- ROS 2 Humble
- Python 3
- OpenCV
- CvBridge
- GStreamer
- SRT
- Tailscale VPN
- ModemManager / NetworkManager
- Wireshark

## Main Features

- Subscription to ROS 2 image topic `/image_raw`
- Video conversion and resizing using OpenCV
- H.264 real-time encoding
- MPEG-TS multiplexing
- Secure SRT streaming
- VPN overlay with Tailscale
- RTT / latency / jitter measurement using UDP probes
- HUD display on receiver side
- Video recording on ground station
- Wireshark-based communication validation

## Experimental Setup

The system was tested using:

- Raspberry Pi 4 as onboard processing unit
- Ground station PC as receiver
- WiFi and 4G connectivity
- Tailscale VPN tunnel
- SRT secure streaming
- Orange and Ooredoo 4G dongles
- Smartphone 4G hotspot

## Key Parameters

- Resolution: 640x480
- FPS: 30
- Bitrate: 2000 kbps
- Codec: H.264
- SRT Port: 9000
- RTT Port: 9001
- SRT passphrase enabled
- `pbkeylen = 32`

## Measured Results

Example measured results from experimental tests:

- Distance between sender and receiver: 2 km
- Average latency with smartphone 4G hotspot: ~90 ms
- Average jitter: ~25 ms
- Latency with Orange 4G dongle: ~300 ms

## Project Structure

See the folders:
- `src/` for Raspberry Pi sender logic
- `receiver/` for ground station receiver logic
- `config/` for parameters
- `docs/` for technical documentation
- `scripts/` for startup scripts

## Installation

### Raspberry Pi
Install:
- ROS 2 Humble
- OpenCV
- GStreamer
- Tailscale
- ModemManager
- NetworkManager

### PC
Install:
- Python 3
- OpenCV
- GStreamer
- Tailscale
- Wireshark


## Network Architecture

The system operates over different network configurations:

- Local WiFi network
- Smartphone 4G hotspot
- USB 4G dongle (Orange / Ooredoo)
- Secure overlay network using Tailscale VPN

Due to CGNAT and IPv6 limitations in mobile networks, Tailscale is used to ensure stable communication between the Raspberry Pi and the ground station.

---

## Security Features

- SRT encrypted video transport (AES)
- Tailscale VPN tunnel (WireGuard-based)
- Private IP addressing (100.x.x.x)
- Wireshark validation of encrypted traffic

---




## Run

### On Raspberry Pi
```bash
bash scripts/run_bridge.sh



