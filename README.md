# 🍌 Banana AutoPilot

An educational ESP32-S3 driving project: collect camera images and manual driving commands, inspect recordings, and learn behavior cloning through Google Colab notebooks.

**Non-commercial use only.** Commercial use requires prior written permission. See [LICENSE](LICENSE).

## Workflow and current status

```text
Local computer (VS Code)              Google Colab
Record a driving session
        ↓
Replay and inspect the dataset ─────→ Explore data and train a model
                                             ↓
Run local inference           ←───── Export weights and model settings
```

| Component | Status |
| --- | --- |
| Camera streaming and keyboard / Switch controller input | Implemented; requires compatible hardware |
| Recording JPEG images and driving labels | Implemented |
| Local dataset replay | Implemented; no vehicle connection required |
| Colab teaching notebooks | Drafts; existing training notebook uses outdated paths and module names |
| Behavior cloning model, training and evaluation in `bc/` | Placeholder files |
| Local autonomous driving | Placeholder file; not ready to run |

The intended teaching notebook will explain data loading, preprocessing, model structure, the training loop, evaluation and model export step by step. Training and inference should eventually share model and preprocessing definitions.

## Project structure

```text
Banana_AutoPilot/
├── core/
│   ├── command.py              # DriveCommand: throttle and steering
│   ├── controller.py           # Keyboard / Switch input and ControllerState
│   ├── camera_stream.py        # MJPEG reception and image decoding
│   ├── websocket_client.py     # Vehicle commands and telemetry
│   ├── dataset_writer.py       # Session images, labels and metadata
│   ├── display.py              # Live image and status display
│   └── utils.py                # Timing helpers
├── workflows/
│   ├── recording.py            # Manual driving and data collection
│   ├── replay.py               # Recorded-session playback
│   └── autonomous_driving.py   # Planned local inference workflow
├── configs/                    # Connection, controller and recording settings
├── bc/                         # Planned behavior cloning implementation
├── colab_notebooks/             # Teaching and environment experiments
├── datasets/                   # Recorded sessions
├── runs/                       # Reserved for training outputs
├── tests/
├── test1.py                     # Manual experiment scripts
├── test2.py
├── pyproject.toml
├── uv.lock
└── LICENSE
```

`ControllerState` contains a `DriveCommand` and an optional button action. The recording workflow sends the command to the vehicle and saves the same throttle and steering values alongside each image. Button actions control recording and exit; they are not vehicle commands.

## Setup

Use Python 3.12 or later, matching `pyproject.toml`. Run commands from the repository root. A desktop display is needed for the Pygame windows.

With `uv` installed:

```bash
git clone https://github.com/ZFTTO/Banana_AutoPilot.git
cd Banana_AutoPilot
uv sync
```

In VS Code, select the Python interpreter inside `.venv`.

Recording additionally requires an ESP32-S3 vehicle serving compatible MJPEG and WebSocket endpoints. Firmware is not included in this repository. The current WebSocket client sends throttle and steering as two space-separated decimal values, not JSON.

## Record a driving session

1. Connect the computer to a network that can reach the ESP32.
2. Check `configs/esp32.py`. Current defaults are:

   | Setting | Default |
   | --- | --- |
   | Host | `192.168.4.1` |
   | Camera stream | `http://192.168.4.1:81/stream` |
   | Vehicle control | `ws://192.168.4.1:80/ws` |

3. Choose the controller in `workflows/recording.py`:

   ```python
   ctrl_config = ControllerConfig(control_mode="keyboard")
   ```

   Change `"keyboard"` to `"switch"` to use a connected controller. Button and axis mappings are in `configs/controller.py`.

4. Start recording mode:

   ```bash
   uv run python -m workflows.recording
   ```

Keep the Pygame window focused for keyboard input.

| Keyboard key | Action |
| --- | --- |
| W / S | Positive / negative throttle |
| A / D | Left / right steering |
| R | Start or stop a recording session |
| Q | Exit |

With the default Switch mapping, axis 1 controls throttle, axis 0 controls steering, button 1 toggles recording, and button 0 exits. Adjust these indices for your controller.

Driving commands are sent even when recording is off. Each new recording creates a new session under `RecorderConfig.dataset_root`, which defaults to `datasets`. The workflow currently sets controller mode and connection timing directly; not every field in `RecorderConfig` is wired into the workflow. The displayed live FPS is currently fixed at `30.0`, not measured.

## Replay a session

Replay runs locally and does not send commands to the vehicle.

```bash
uv run python -m workflows.replay --session datasets/session_001
```

Start at half speed:

```bash
uv run python -m workflows.replay --session datasets/session_001 --speed 0.5
```

| Key | Action |
| --- | --- |
| Space | Play / pause; restart after reaching the last frame |
| Left / Right | Step backward / forward and pause |
| Up / Down | Increase / decrease speed, from 0.125× to 8× |
| Home | Rewind |
| Q / Esc | Exit |

The player uses recorded timestamps and shows frame position, elapsed time, throttle and steering. Missing images, invalid labels and backwards timestamps are reported as errors.

## Dataset format

```text
datasets/session_001/
├── images/
│   ├── 000001.jpg
│   └── ...
├── labels.csv
└── metadata.json
```

`labels.csv` contains:

```csv
frame,image,timestamp,throttle,steering
1,000001.jpg,251201.508190,-0.19677734375,0.09942626953125
```

- `image` is relative to the session's `images/` directory.
- `timestamp` is the host's monotonic time in seconds when the sample is written, not a wall-clock date or a camera capture timestamp.
- `throttle` and `steering` are requested commands, not measured vehicle speed or steering angle.
- `metadata.json` is written when the session is stopped. Its hardware and resolution descriptions are currently hard-coded in the writer.

## Colab teaching and model transfer

The intended workflow is to upload recorded sessions, teach and run training in Colab, then download weights and the corresponding settings for local inference.

`colab_notebooks/BananaTrain_0.ipynb` is an older draft. It references `LuluLab_AutoDrive` and `behavior_cloning`, while this repository uses `Banana_AutoPilot` and `bc`. Updating those names alone will not make training work: the `bc` modules still need implementation.

For the teaching implementation:

1. Preserve each session's `images/` and `labels.csv` structure when transferring data.
2. Explore labels and images before training; split by session where possible to reduce leakage between neighboring frames.
3. Explain image preprocessing, the model, loss and optimization directly in the notebook.
4. Save weights together with model settings, preprocessing settings and output definitions.
5. Keep training outputs in persistent storage before the Colab runtime ends.

There is no working training or autonomous-driving command yet.

## Connection troubleshooting

| Message | Meaning and first checks |
| --- | --- |
| `Broken pipe` | The WebSocket connection broke while writing. Check for an ESP32 restart, server disconnect or network interruption. |
| `No route to host` | The host is unreachable. Check the selected Wi-Fi network, ESP32 address and whether the device is powered on. |
| `Stream read error: timed out` | No stream data arrived within the timeout. Check the camera endpoint and ESP32 state. |

If both camera and control fail together, check shared network connectivity and power first. These messages alone do not establish the cause. The WebSocket client attempts reconnection; the camera stream currently stops after a read error and does not reconnect automatically. Restart the recording workflow after restoring connectivity.

## License

Copyright (c) 2026 ZFTTO.

This project uses the custom **Banana AutoPilot Non-Commercial License 1.0**, not the MIT License. Non-commercial use, modification and redistribution are permitted subject to [LICENSE](LICENSE). Keep the copyright and license notices and identify your modifications. Commercial use, including paid products, services and training, requires prior written permission from the relevant copyright holder.

This is source-available software with a non-commercial restriction. Third-party dependencies remain under their own licenses. For commercial permission, contact the maintainer through the [project repository](https://github.com/ZFTTO/Banana_AutoPilot).
