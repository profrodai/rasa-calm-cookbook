# Meeting Intelligence Agent 🎙️

A production-ready **voice-enabled meeting assistant** that processes multi-speaker recordings (earnings calls, executive meetings) and allows natural voice Q&A with intelligent answers.

Built with **open-weight models** for complete local deployment:
- 🎤 **Whisper** (faster-whisper) for speech recognition
- 🗣️ **NeuTTS Air** for natural voice synthesis with instant cloning
- 👥 **pyannote** for speaker diarization
- 🧠 **ChromaDB** for semantic search
- 🤖 **Rasa Pro** for conversational AI

---

## 🎯 Use Case

Process recorded meetings and ask questions via voice:

**Example Questions:**
- "What did the CFO say about operating margins?"
- "Summarize the CEO's comments on AI investments"
- "Which analyst asked about Q4 guidance?"

**You Get:**
- ✅ Accurate text answers with speaker attribution
- ✅ Natural spoken responses via NeuTTS Air
- ✅ Timestamps for reference

**Target Meetings:**
- Quarterly earnings calls
- Executive committee meetings
- Board meetings
- Public hearings
- Clinical case reviews

---

## ✨ Features

- ✅ **Multi-speaker diarization** with pyannote (SPEAKER_0, SPEAKER_1, etc.)
- ✅ **High-accuracy transcription** with faster-whisper (optimized for M4 Mac)
- ✅ **Semantic search** with ChromaDB + sentence-transformers
- ✅ **Voice interface** via browser with real-time ASR/TTS
- ✅ **Instant voice cloning** with NeuTTS Air (3+ reference voices included)
- ✅ **LLM-powered answers** using Rasa's built-in capabilities
- ✅ **End-to-end voice testing** with synthetic test questions
- ✅ **Fully local** - no cloud dependencies required

---

## 📋 Prerequisites

### System Requirements
- **macOS M4** (optimized for Apple Silicon)
- **Python 3.11**
- **16GB+ RAM** (for Whisper medium + embeddings)
- **10GB+ disk space** (models + meetings)

### Required Tools
- `uv` (Astral package manager)
- `ffmpeg` (audio processing)
- `espeak-ng` (for NeuTTS Air phonemization)

### API Keys
- **Rasa Pro License** (required)
- **OpenAI API Key** (for LLM answer generation)
- **Hugging Face Token** (for pyannote model access)

---

## 🚀 Quick Start

### 1. Install System Dependencies

```bash
# macOS (M4)
brew install ffmpeg espeak-ng

# Verify installations
ffmpeg -version
espeak --version
```

### 2. Setup Python Environment

From repository root:

```bash
# Create virtual environment and install dependencies
cd /path/to/rasa-calm-cookbook
make setup
source .venv/bin/activate

# Navigate to this recipe
cd recipes/level-3-advanced/meeting-intelligence-agent
```

### 3. Install Recipe Dependencies

```bash
# Install meeting intelligence specific dependencies
make setup-recipe
```

This installs:
- `pyannote.audio` (speaker diarization)
- `faster-whisper` (ASR with CoreML optimization)
- `neutts-air` (TTS)
- `chromadb` (vector database)
- `sentence-transformers` (embeddings)

### 4. Configure Environment

```bash
# Create .env file
make setup-env

# Edit .env with your credentials
nano .env
```

Required variables:
```bash
RASA_LICENSE=your-rasa-pro-license-here
OPENAI_API_KEY=your-openai-key-here
HF_TOKEN=your-huggingface-token-here
```

### 5. Accept Hugging Face Model Terms

Visit and accept terms:
- [pyannote/speaker-diarization-community-1](https://huggingface.co/pyannote/speaker-diarization-community-1)

### 6. Download Sample Earnings Call

```bash
# Download a sample public earnings call
make download-sample-call
```

Or place your own meeting audio in `recordings/`:
```bash
cp /path/to/your-meeting.wav recordings/my_meeting.wav
```

### 7. Process Meeting

```bash
# Process the sample call (takes 5-15 minutes)
make process-meeting MEETING_ID=sample_earnings_call
```

This will:
1. Run speaker diarization (pyannote)
2. Transcribe with Whisper
3. Create embeddings with ChromaDB
4. Save structured transcript

Output files:
```
meetings/processed/sample_earnings_call_diarization.json
meetings/processed/sample_earnings_call_transcript.json
meetings/processed/sample_earnings_call_embeddings/  # ChromaDB
```

### 8. Train Rasa Model

```bash
make train
```

### 9. Test with Voice!

```bash
# Start Rasa with voice interface (Terminal 1)
make inspect-voice

# In another terminal, start action server (Terminal 2)
make run-actions
```

Then:
1. Browser opens at `http://localhost:5005/assistants/voice`
2. Click microphone icon
3. Grant permissions
4. Ask: **"What did the CFO say about margins?"**
5. Get spoken answer!

---

## 📖 Detailed Usage

### Processing Your Own Meetings

#### Option A: From Audio File

```bash
# 1. Copy your meeting to recordings/
cp /path/to/quarterly_call.wav recordings/q3_2024_call.wav

# 2. Process it
make process-meeting MEETING_ID=q3_2024_call TITLE="Q3 2024 Earnings Call"

# 3. (Optional) Create speaker map
cat > meetings/speaker_maps/q3_2024_call_speaker_map.json << EOF
{
  "SPEAKER_0": "CEO - Jane Smith",
  "SPEAKER_1": "CFO - John Doe",
  "SPEAKER_2": "Analyst - Morgan Stanley",
  "SPEAKER_3": "Analyst - Goldman Sachs"
}
EOF

# 4. Re-process to apply speaker labels
make process-meeting MEETING_ID=q3_2024_call
```

#### Option B: From Public Source

Edit `recordings/download_sample_call.py` to download from SEC EDGAR or other public sources.

### Audio Requirements

For best results, meeting audio should be:
- **Format**: WAV (other formats auto-converted via ffmpeg)
- **Sample Rate**: 16kHz+ (higher is better)
- **Duration**: 10 minutes to 2 hours
- **Quality**: Clear speech, minimal background noise
- **Channels**: Mono or Stereo (stereo will be converted)

### Managing Multiple Meetings

```bash
# Process multiple meetings
make process-meeting MEETING_ID=q1_2024_call
make process-meeting MEETING_ID=q2_2024_call
make process-meeting MEETING_ID=q3_2024_call

# List processed meetings
ls -lh meetings/processed/

# Switch active meeting (edit domain.yml)
# Change initial_value of meeting_id slot
```

### Voice Reference Customization

NeuTTS Air uses voice cloning. Included references:
- `reference_voices/male_professional.wav` - Male executive voice
- `reference_voices/female_professional.wav` - Female executive voice

Add your own:
```bash
# 1. Record 5-10 seconds of clean speech
# 2. Save as 16-44kHz mono WAV
cp /path/to/custom_voice.wav reference_voices/my_voice.wav

# 3. Update credentials.yml to use it:
# tts:
#   reference_audio: reference_voices/my_voice.wav
```

---

## 🏗️ Architecture

### Meeting Processing Pipeline

```
Raw Audio (WAV)
    ↓
[pyannote] Speaker Diarization
    ↓
Segments with Speaker Labels
    ↓
[faster-whisper] Transcription
    ↓
Structured Transcript (JSON)
    ↓
[sentence-transformers] Embeddings
    ↓
[ChromaDB] Vector Storage
```

### Voice Q&A Pipeline

```
User Voice Question
    ↓
[faster-whisper] ASR → Text
    ↓
[Rasa] Intent Recognition
    ↓
[ChromaDB] Semantic Search → Relevant Segments
    ↓
[Rasa LLM] Answer Generation
    ↓
[NeuTTS Air] TTS → Voice Answer
    ↓
User Hears Response
```

### Key Components

1. **meeting_processing/** - Python module for ingestion
   - `diarization.py` - pyannote integration
   - `transcription.py` - Whisper integration
   - `vectordb.py` - ChromaDB management
   - `retrieval.py` - Semantic search

2. **addons/neutts_tts.py** - Custom Rasa TTS component
   - Integrates NeuTTS Air GGUF models
   - Handles voice cloning
   - Resamples 24kHz → 8kHz mulaw for Rasa

3. **actions/actions.py** - Rasa custom actions
   - `ActionAnswerMeetingQuestion` - Main Q&A logic
   - Uses ChromaDB for retrieval
   - Uses Rasa's LLM for answer generation

---

## 🧪 Testing

### End-to-End Voice Tests

```bash
# Generate synthetic test questions (using NeuTTS Air)
make generate-test-audio

# Run automated voice tests
# (Requires Rasa + actions running in other terminals)
make test-voice-production
```

Test questions include:
- "What did the CEO say about AI investments?"
- "Summarize the CFO's margin commentary"
- "Which analyst asked about guidance?"

### Manual Testing

```bash
# Text-based testing
make shell

# Voice testing
make inspect-voice

# REST API testing
curl -X POST http://localhost:5005/webhooks/rest/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "test_user",
    "message": "What did the CFO say about margins?"
  }'
```

### Validate Configuration

```bash
# Check all files and settings
make validate

# Check environment status
make status
```

---

## 🔧 Configuration

### LLM Provider

Default: OpenAI GPT-4

```bash
# Use OpenAI (default)
make config-openai

# Use Azure OpenAI
make config-azure

# Use local LLM (e.g., Ollama)
make config-local
```

### Voice Settings

Edit `credentials.yml`:

```yaml
browser_audio:
  # Speech Recognition (ASR)
  asr:
    name: addons.whisper_asr.WhisperASR
    model: "medium.en"
    device: "cpu"  # or "mps" for M4 GPU
    
  # Text-to-Speech (TTS)
  tts:
    name: addons.neutts_tts.NeuTTSTTS
    backbone_model: "neuphonic/neutts-air-q4-gguf"
    reference_audio: "reference_voices/male_professional.wav"
    reference_text: "reference_voices/male_professional.txt"
```

### Retrieval Settings

Edit `meeting_processing/config.py`:

```python
# Semantic search parameters
RETRIEVAL_TOP_K = 10  # Number of segments to retrieve
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # sentence-transformers model
CHUNK_OVERLAP = 50  # Token overlap between segments
```

---

## 📁 Project Structure

```
meeting-intelligence-agent/
├── README.md                          # This file
├── Makefile                           # All commands
├── pyproject.toml                     # Dependencies
├── .env.example                       # Environment template
├── .env                               # Your credentials (gitignored)
│
├── config.yml                         # Active Rasa config
├── config-openai.yml                  # OpenAI config
├── credentials.yml                    # Voice settings (ASR/TTS)
├── domain.yml                         # Rasa domain
├── endpoints.yml                      # Action server config
│
├── data/
│   └── flows.yml                      # Conversation flows
│
├── recordings/                        # Input audio files
│   ├── download_sample_call.py        # Download public calls
│   └── sample_earnings_call.wav       # Sample meeting (downloaded)
│
├── meetings/                          # Processed meetings
│   ├── processed/
│   │   ├── sample_earnings_call_diarization.json
│   │   ├── sample_earnings_call_transcript.json
│   │   └── sample_earnings_call_embeddings/  # ChromaDB
│   └── speaker_maps/
│       └── sample_earnings_call_speaker_map.json
│
├── meeting_processing/                # Python module for ingestion
│   ├── __init__.py
│   ├── config.py                      # Central configuration
│   ├── diarization.py                 # pyannote integration
│   ├── transcription.py               # Whisper integration
│   ├── storage.py                     # JSON read/write
│   ├── vectordb.py                    # ChromaDB management
│   └── retrieval.py                   # Semantic search
│
├── actions/                           # Rasa custom actions
│   ├── __init__.py
│   ├── actions.py                     # Main Q&A action
│   └── llm_helper.py                  # LLM utilities
│
├── addons/                            # Custom Rasa components
│   ├── neutts_tts.py                  # NeuTTS Air TTS
│   └── whisper_asr.py                 # Whisper ASR (optional)
│
├── reference_voices/                  # Voice cloning samples
│   ├── male_professional.wav
│   ├── male_professional.txt
│   ├── female_professional.wav
│   ├── female_professional.txt
│   └── README.md
│
└── tests/                             # Testing
    ├── audio/                         # Test questions (generated)
    ├── audio_responses/               # Test answers (generated)
    ├── test_meeting_pipeline.py       # Pipeline tests
    ├── test_voice_production.py       # E2E voice tests
    └── generate_test_audio.py         # Generate test questions
```

---

## 🐛 Troubleshooting

### pyannote Authentication Error

```bash
# Make sure you've accepted model terms at:
# https://huggingface.co/pyannote/speaker-diarization-community-1

# Then login with your HF token:
huggingface-cli login
```

### Whisper Running Slow

```bash
# Enable Apple Silicon GPU acceleration
# Edit meeting_processing/config.py:
WHISPER_DEVICE = "mps"  # Instead of "cpu"
```

### NeuTTS Air Import Error

```bash
# Install espeak-ng if missing
brew install espeak-ng

# Verify phonemizer can find it
python -c "from phonemizer.backend import EspeakBackend; print('OK')"
```

### ChromaDB Persistence Error

```bash
# Clear and rebuild vector database
rm -rf meetings/processed/*/embeddings/
make process-meeting MEETING_ID=your_meeting
```

### Action Server Connection Failed

```bash
# Check if action server is running
curl http://localhost:5055/health

# If not, start it:
make run-actions
```

### Low Audio Quality

For NeuTTS Air, if audio sounds robotic:
1. Use better reference voice (10+ seconds, clear speech)
2. Increase sample rate in credentials.yml
3. Try different backbone model (Q8 instead of Q4)

---

## 🎓 Learning Path

### For Junior Developers

Follow this order:

1. **Setup & First Meeting**
   - Run quick start
   - Process sample earnings call
   - Ask basic questions via voice

2. **Understand Pipeline**
   - Read `meeting_processing/config.py`
   - Examine output JSON files
   - Review ChromaDB structure

3. **Customize Voice**
   - Record your own reference voice
   - Update credentials.yml
   - Test with your voice

4. **Process Your Meeting**
   - Get your own meeting audio
   - Create speaker map
   - Process and test

5. **Extend Functionality**
   - Add new question types in flows.yml
   - Customize retrieval logic
   - Add multi-meeting support

### Advanced Topics

- **Multi-turn conversations** - Context maintenance
- **Speaker verification** - Voice biometrics with pyannote
- **Real-time processing** - Streaming diarization + transcription
- **Multi-language support** - Whisper multilingual models
- **Custom embeddings** - Fine-tune sentence-transformers
- **Production deployment** - Docker, Redis, PostgreSQL

---

## 📚 Resources

### Documentation
- [Rasa Pro Docs](https://rasa.com/docs/rasa-pro/)
- [pyannote.audio](https://github.com/pyannote/pyannote-audio)
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
- [NeuTTS Air](https://github.com/neuphonic/neutts-air)
- [ChromaDB](https://docs.trychroma.com/)

### Related Recipes
- `level-2-intermediate/voice-assistant` - Voice banking assistant
- `level-1-basic/llm-flow-assistant` - Basic LLM flows
- `level-3-advanced/rag-assistant` - RAG patterns

### Community
- [Rasa Community Forum](https://forum.rasa.com/)
- [GitHub Discussions](https://github.com/ducktyper-ai/rasa-calm-cookbook/discussions)

---

## 🤝 Contributing

Improvements welcome! Areas of interest:
- Additional meeting source integrations (Zoom, Teams, etc.)
- Multi-language support
- Real-time streaming
- Better speaker identification
- UI improvements

---

## 📄 License

AGPL-3.0 - See repository root for details.

---

## 🙏 Acknowledgments

Built with:
- **Rasa** - Conversational AI framework
- **pyannote** - Speaker diarization toolkit  
- **OpenAI Whisper** - Speech recognition
- **Neuphonic** - NeuTTS Air voice synthesis
- **ChromaDB** - Vector database
- **Hugging Face** - Model hosting

Special thanks to the open-source AI community!

---

**Ready to talk to your meetings?** 🎙️

Start with: `make setup-recipe && make download-sample-call && make process-meeting`