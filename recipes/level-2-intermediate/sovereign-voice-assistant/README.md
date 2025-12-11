# Sovereign Voice Assistant - Banking Support with Speech

A production-ready, fully sovereign voice banking assistant that runs 100% on-premise using **Local ASR** (Faster-Whisper), **Local TTS** (NeuTTS Air), and **Local LLM** (Ministral/Ollama).

## Overview

This recipe demonstrates:
- **100% Local Voice Stack** (No data leaves your machine)
- **Microservice Architecture** for ASR (Decoupled from Rasa Core)
- **High-Fidelity Neural TTS** with real-time transcoding
- **End-to-End Voice Testing** pipeline injecting raw WAV files
- **Voice-optimized conversation flows** with proper slot management
- **Natural language processing** for banking operations

## Use Case

A privacy-first voice banking assistant that helps customers:
- Check account balances (voice-optimized)
- Transfer money between accounts (with confirmation)
- Report lost or stolen cards (with verification)
- Speak naturally without rigid command structures

## Features

- ✅ **Fully Sovereign** - Runs offline (Air-gapped compatible)
- ✅ **Local "Ears"** - Faster-Whisper ASR (WebSocket Microservice)
- ✅ **Local "Mouth"** - NeuTTS Air (Neural 24kHz TTS)
- ✅ **Local "Brain"** - Ministral 8B via Ollama
- ✅ **Browser-based voice interface** - No phone number needed
- ✅ **Automated E2E Testing** - Injects audio -> ASR -> Rasa -> TTS -> Audio
- ✅ **Silence detection** - handled via Rasa endpointing
- ✅ **Action server integration** - Custom banking actions

## Prerequisites

- Python 3.10 or 3.11
- Valid Rasa Pro license
- **Ollama** installed and running (`ollama serve`)
- **ffmpeg** installed (`brew install ffmpeg`)
- **espeak** installed (`brew install espeak`)
- Modern web browser with microphone access
- **Three terminal windows** (Rasa + Action Server + ASR Server)

## Quick Start

### 1. Navigate to Recipe
```bash
cd recipes/level-2-intermediate/sovereign-voice-assistant
````

### 2\. Set Up Environment

```bash
# Create .env file from template
make setup-env

# Edit .env with your credentials
# Required:
#   RASA_LICENSE=your-rasa-pro-license
#   DEEPGRAM_API_KEY (Only for testing reference, optional for local stack)
```

### 3\. Install Dependencies

```bash
# Install Rasa, NeuTTS, and Local ASR dependencies
make setup-recipe
make install-neutts
make install-local-asr
```

### 4\. Configure Local LLM

```bash
# Ensure Ollama is running
ollama pull ministral-8b
make config-local
```

### 5\. Train the Model

```bash
make train
```

### 6\. Run the Assistant

**You need THREE terminals running simultaneously:**

**Terminal 1 - Local ASR Server:**

```bash
make run-local-asr
# Starts WebSocket server on ws://localhost:9001
```

**Terminal 2 - Action Server:**

```bash
make run-actions
# Starts on http://localhost:5055
```

**Terminal 3 - Rasa Server:**

```bash
make run
# Starts on http://localhost:5005
```

### 7\. Interact

**Terminal 4 - Manual Test:**

```bash
make inspect-voice
# Opens browser. Click microphone to talk.
```

## Architecture: The "Sovereign Stack"

This assistant uses a microservice architecture to decouple heavy AI workloads from the dialogue loop.

| Component | Technology | Role | Protocol |
| :--- | :--- | :--- | :--- |
| **Ears (ASR)** | **Faster-Whisper** | Transcribes audio to text | WebSocket (ws://localhost:9001) |
| **Brain (NLU)** | **Rasa + Ministral** | Dialogue Management | HTTP / REST |
| **Mouth (TTS)** | **NeuTTS Air** | Synthesizes text to audio | In-process Python Class |
| **Client** | **Web Browser** | Capture/Play audio | SocketIO |

### Key Innovations

1.  **ASR Microservice:** Instead of blocking Rasa's event loop, we stream audio to a local Python server running Faster-Whisper.
2.  **TTS Transcoding:** NeuTTS generates 24kHz Float32 audio. A custom wrapper (`NeuTTSService`) downsamples this to 8kHz $\mu$-law in real-time to match Rasa's telephony standards.

## Testing Pipeline

### Automated End-to-End Voice Testing

We built a custom pipeline to verify the entire stack without speaking a word.

```bash
# 1. Generate test audio files (from text)
make generate-test-audio

# 2. Run the full pipeline test
make test-voice-automated
```

**What the test does:**

1.  Injects raw WAV files (`tests/audio/`) into the **Local ASR Server**.
2.  Sends the transcription to **Rasa**.
3.  Feeds the bot's response text to **NeuTTS**.
4.  Records the generated audio response.
5.  **Stitches** the User Audio + Bot Audio into a single `conversation.wav` file.

**Output:**
Listen to the full conversations in `tests/audio_responses_real/`:

  - `full_balance_check.wav`
  - `full_transfer.wav`
  - `full_lost_card.wav`

## Voice-Specific Implementation Details

### 1\. Flexible Digit Recognition

Voice transcription often adds spaces between digits. Our flows handle this:

  * **Transcript:** "four five three two" -\> "4 5 3 2"
  * **Action Logic:** Strips spaces before validating against account numbers.

### 2\. Slot Reset Management

Critical for voice interfaces where context switches are frequent. We explicitly reset slots (`transfer_amount`, `confirmation`) at the end of flows to prevent stale data in the next conversation turn.

### 3\. Silence Handling

  * **Rasa Endpointing:** Configured to `400ms`. When the user pauses, Rasa sends a signal to the Local ASR server to finalize the transcription.

## Configuration

### Credentials (`credentials.yml`)

The stack is configured to use local services by default:

```yaml
browser_audio:
  server_url: localhost
  
  # Local Ears (Whisper)
  asr:
    name: services.local_asr_client.LocalASR
    endpoint: "ws://localhost:9001"
    endpointing: 400 

  # Local Mouth (NeuTTS)
  tts:
    name: services.neutts_service.NeuTTSService
    config:
      backbone_repo: neuphonic/neutts-air-q8-gguf
      codec_repo: neuphonic/neucodec
      device: cpu
      auto_generate_reference: true
```

## Project Structure

```
.
├── actions/                 # Banking logic
├── config.yml               # NLU configuration
├── credentials.yml          # Voice channel config
├── data/                    # Training data (flows.yml)
├── services/
│   ├── local_asr_server.py  # Standalone Whisper Server
│   ├── local_asr_client.py  # Rasa Adapter for Whisper
│   └── neutts_service.py    # Rasa Adapter for NeuTTS
├── tests/
│   ├── audio/               # Input WAV files
│   ├── audio_responses_real/# Generated conversation WAVs
│   └── test_voice_automated.py # E2E Pipeline Script
└── ...
```

## Troubleshooting

### "ASR Connection Refused"

  * **Cause:** The local ASR server isn't running.
  * **Fix:** Run `make run-local-asr` in a separate terminal.

### "NeuTTS Initialization Failed"

  * **Cause:** Missing system dependencies (usually `espeak`).
  * **Fix:** Run `brew install espeak` (macOS) or `sudo apt install espeak` (Linux).

### "Audio Glitches / Silence"

  * **Cause:** Mismatch in sample rates (24k vs 8k).
  * **Fix:** Ensure you are using the updated `NeuTTSService` class which handles resampling/transcoding automatically.

## Resources

  - [Faster Whisper](https://github.com/SYSTRAN/faster-whisper)
  - [NeuTTS Air](https://github.com/neuphonic/neutts-air)
  - [Rasa Voice Documentation](https://www.google.com/search?q=https://rasa.com/docs/rasa/connectors/your-own-website/%23voice-channel)

-----

*Last updated: December 2025*