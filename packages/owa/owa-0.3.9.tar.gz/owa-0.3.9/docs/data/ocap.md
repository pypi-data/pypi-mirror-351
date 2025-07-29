# ocap

High-performance desktop recorder for Windows. Captures screen, audio, keyboard, mouse, and window events.

<!-- ![ocap recording demo](../images/ocap-demo.gif) -->

<video controls>
    <source src="../ocap.mkv" type="video/mp4">
</video>

## What is ocap?

**ocap** (Omnimodal CAPture) captures all essential desktop signals in synchronized format. Records screen video, audio, keyboard/mouse input, and window events. Built for the _open-world-agents_ project but works for any desktop recording needs.

> **TL;DR**: Complete, high-performance desktop recording tool for Windows. Captures everything in one command.

## Key Features

- **Complete desktop recording**: Video, audio, keyboard/mouse events, window events
- **High performance**: Hardware-accelerated with Windows APIs and [GStreamer](https://gstreamer.freedesktop.org/)
- **Efficient encoding**: [H265/HEVC](https://en.wikipedia.org/wiki/High_Efficiency_Video_Coding) for high quality and small file size
- **Simple operation**: `ocap FILE_LOCATION` (stop with Ctrl+C)
- **Clean architecture**: Core logic in [single 250-line Python file](https://github.com/open-world-agents/open-world-agents/blob/main/projects/ocap/owa/ocap/record.py)
- **Modern formats**: MKV with embedded timestamps, [MCAP format](https://mcap.dev/) for events

## System Requirements

Based on OBS Studio recommended specs + NVIDIA GPU requirements:

| Component | Specification |
|-----------|---------------|
| **OS** | Windows 11 (64-bit) |
| **Processor** | Intel i7 8700K / AMD Ryzen 1600X |
| **Memory** | 8 GB RAM |
| **Graphics** | **NVIDIA GeForce 10 Series or newer** ⚠️ |
| **DirectX** | Version 11 |
| **Storage** | 600 MB + ~100MB per minute recording |

> ⚠️ **NVIDIA GPU Required**: Currently only supports NVIDIA GPUs for hardware acceleration. AMD/Intel GPU support possible through GStreamer framework - **contributions welcome**!

## Installation & Usage

### Option 1: Download Release
1. Download `ocap.zip` from [releases](https://github.com/open-world-agents/open-world-agents/releases)
2. Unzip and run:
    - Double-click `run.bat` (opens terminal with virtual environment)
    - Or in CLI: `run.bat --help`

### Option 2: Conda Install

[![conda-forge](https://img.shields.io/conda/vn/conda-forge/ocap.svg)](https://anaconda.org/conda-forge/ocap)

```sh
$ conda install ocap
```

### Basic Usage

```sh
# Start recording (stop with Ctrl+C)
$ ocap my-recording

# Show all options
$ ocap --help

# Advanced options
$ ocap FILENAME --window-name "App"   # Record specific window
$ ocap FILENAME --monitor-idx 1       # Record specific monitor
$ ocap FILENAME --fps 60              # Set framerate
$ ocap FILENAME --no-record-audio     # Disable audio
```

### Output Files
- `.mcap` — Event log (keyboard, mouse, windows)
- `.mkv`  — Video/audio with embedded timestamps

Your recording files will be ready immediately!

## Feature Comparison

| **Feature**                              | **ocap**                 | [OBS](https://obsproject.com/) | [wcap](https://github.com/mmozeiko/wcap) | [pillow](https://github.com/python-pillow/Pillow)/[mss](https://github.com/BoboTiG/python-mss) |
|------------------------------------------|--------------------------|--------------------------------|------------------------------------------|----------------------------------|
| Advanced data formats (MCAP/MKV)     | ✅ Yes                   | ❌ No                          | ❌ No                                    | ❌ No                            |
| Timestamp aligned logging                | ✅ Yes                   | ❌ No                          | ❌ No                                    | ❌ No                            |
| Customizable event definition & Listener | ✅ Yes                   | ❌ No                          | ❌ No                                    | ❌ No                            |
| Single python file                       | ✅ Yes                   | ❌ No                          | ❌ No                                    | ❌ No                            |
| Audio + Window + Keyboard + Mouse        | ✅ Yes                   | ⚠️ Partial                    | ❌ No                                    | ❌ No                            |
| Hardware-accelerated encoder             | ✅ Yes                   | ✅ Yes                         | ✅ Yes                                   | ❌ No                            |
| Supports latest Windows APIs             | ✅ Yes                   | ✅ Yes                         | ✅ Yes                                   | ❌ No (legacy APIs only)         |
| Optional mouse cursor capture            | ✅ Yes                   | ✅ Yes                         | ✅ Yes                                   | ❌ No                            |

## Technical Architecture

Built on GStreamer with clean, maintainable design:

```mermaid
flowchart TD
    %% Input Sources
    A[owa.env.desktop] --> B[Keyboard Events]
    A --> C[Mouse Events] 
    A --> D[Window Events]
    E[owa.env.gst] --> F[Screen Capture]
    E --> G[Audio Capture]
    
    %% Core Processing
    B --> H[Event Queue]
    C --> H
    D --> H
    F --> H
    F --> I[Video/Audio Pipeline]
    G --> I
    
    %% Outputs
    H --> J[MCAP Writer]
    I --> K[MKV Pipeline]
    
    %% Files
    J --> L[📄 events.mcap]
    K --> M[🎥 video.mkv]
    
    style A fill:#e1f5fe
    style E fill:#e1f5fe
    style H fill:#fff3e0
    style L fill:#e8f5e8
    style M fill:#e8f5e8
```

- **Easy to verify**: Extensive [OWA's Env](../env/index.md) design enables customizable [`record.py`](https://github.com/open-world-agents/open-world-agents/blob/main/projects/ocap/owa/ocap/record.py)
- **Native performance**: Direct Windows API integration ([DXGI](https://learn.microsoft.com/en-us/windows/win32/direct3ddxgi/d3d10-graphics-programming-guide-dxgi)/[WGC](https://learn.microsoft.com/en-us/uwp/api/windows.graphics.capture?view=winrt-26100), [WASAPI](https://learn.microsoft.com/en-us/windows/win32/coreaudio/wasapi))

## Troubleshooting

- **Record terminates right after start?** Re-run same command multiple times. It's because of crash in GStreamer, where the cause is unknown.
- **Audio not recording?** In default setting, only audio from target process is recorded. You can turn off by manually editing [gstreamer pipeline](https://github.com/open-world-agents/open-world-agents/blob/fbbfdd8d3b5f9695cf295e860467776575fb1046/projects/owa-env-gst/owa/env/gst/pipeline_builder/factory.py#L71).
- **Large file sizes?** Easiest way to reduce file size is adjusting [`gop-size`](https://gstreamer.freedesktop.org/documentation/nvcodec/nvd3d11h265enc.html?gi-language=c#nvd3d11h265enc:gop-size) parameter in `nvd3d11h265enc` element. Check [pipeline.py](https://github.com/open-world-agents/open-world-agents/blob/3b339897ed8eb15ac04b527c0ef1fb5baf52a2e2/projects/owa-env-gst/owa/env/gst/pipeline_builder/pipeline.py)
- **Performance tips:** Close unnecessary applications before recording, use SSD storage for better write performance, record to different drive than your OS drive

## FAQ

- **How much disk space do recordings use?** ~100MB per minute for 1080p H265 recording.
- **Can I customize recorded events?** Yes. Enable/disable audio, keyboard, mouse, and window events individually. Since [record.py](https://github.com/open-world-agents/open-world-agents/blob/main/projects/ocap/owa/ocap/record.py) is just a 250-line single python script, you may customize it easily.
- **Will ocap slow down my computer?** Minimal impact with hardware acceleration. Designed for low overhead.
- **What formats are supported?** MKV with H265/HEVC encoding for video and MCAP format for events for efficient storage and querying is supported, but you may customize it easily. (e.g. saving `jsonl` instead of `mcap` file takes minimal effort by editing [record.py](https://github.com/open-world-agents/open-world-agents/blob/main/projects/ocap/owa/ocap/record.py))

## When to Use ocap

- **Agent training**: Capture all inputs and outputs for AI training
- **Workflow documentation**: Record exact steps with precise timing
- **Performance testing**: Low-overhead recording during intensive tasks
- **Complete screen recording**: When you need more than just video