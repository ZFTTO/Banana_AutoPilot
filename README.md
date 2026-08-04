# 🍌 Banana AutoPilot

```
  _______   ________   ___   __    ________   ___   __    ________
/_______/\ /_______/\ /__/\ /__/\ /_______/\ /__/\ /__/\ /_______/\
\::: _  \ \\::: _  \ \\::`_\\  \ \\::: _  \ \\::`_\\  \ \\::: _  \ \
 \::\_\  \/_\::\_\  \ \\:. `-\  \ \\::\_\  \ \\:. `-\  \ \\::\_\  \ \
  \::  _  \ \\:: __  \ \\:. _    \ \\:: __  \ \\:. _    \ \\:: __  \ \
   \::\_\  \ \\:.\ \  \ \\. \`-\  \ \\:.\ \  \ \\. \`-\  \ \\:.\ \  \ \
 ___\_______\/ \__\/\__\/_\__\/ `__\/_\__\/\__\/ \__\/_`__\/_\__\/\__\/____   _________
/_______/\ /_/\/_/\ /________/\/_____/\ /_____/\ /_______/\/_/\     /_____/\ /________/\
\::: _  \ \\:\ \:\ \\__.::.__\/\:::_ \ \\:::_ \ \\__.::._\/\:\ \    \:::_ \ \\__.::.__\/
 \::\_\  \ \\:\ \:\ \  \::\ \   \:\ \ \ \\:\_\ \ \  \::\ \  \:\ \    \:\ \ \ \  \::\ \
  \:: __  \ \\:\ \:\ \  \::\ \   \:\ \ \ \\: ___\/  _\::\ \__\:\ \____\:\ \ \ \  \::\ \
   \:.\ \  \ \\:\_\:\ \  \::\ \   \:\_\ \ \\ \ \   /__\::\__/\\:\/___/\\:\_\ \ \  \::\ \
    \__\/\__\/ \_____\/   \__\/    \_____\/ \_\/   \________\/ \_____\/ \_____\/   \__\/
```

## Overview

**Banana AutoPilot** is a low-cost autonomous driving platform based on:

- ESP32-S3 camera module
- Behavior Cloning (BC)
- Computer Vision
- WebSocket real-time control
- Python AI inference pipeline

## Architecture

```
Camera
  |
  v
ESP32-S3
  |
  | MJPEG Stream
  |
  v
Python Recorder
  |
  +--> Dataset
  |
  v
Behavior Cloning Model
  |
  v
Steering + Throttle Control
  |
  v
ESP32 Vehicle
```

## Features

- 📷 Real-time camera streaming
- 🎮 Manual driving data collection
- 🧠 Neural network based driving policy
- 🚗 Autonomous steering control
- 🔌 Low-cost ESP32 hardware

## Project Structure

```
Banana_AutoPilot/
│
├── firmware/
│   └── esp32/
│
├── recorder/
│   ├── mjpeg_reader.py
│   ├── websocket_client.py
│   └── dataset_writer.py
│
├── behavior_cloning/
│   ├── model.py
│   ├── train.py
│   └── inference.py
│
└── README.md
```

## Quick Start

### 1. Clone repository

```bash
git clone https://github.com/yourname/Banana_AutoPilot.git
cd Banana_AutoPilot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run recorder

```bash
python -m recorder.recorder
```

### 4. Train model

```bash
python behavior_cloning/train.py
```

## Roadmap

- [x] ESP32 camera streaming
- [x] WebSocket control
- [x] Data recording pipeline
- [ ] Behavior cloning training
- [ ] Real-time autonomous driving
- [ ] Reinforcement learning experiments

## License

MIT License