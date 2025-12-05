# Reference Voices for NeuTTS Air

This directory contains reference voice samples for NeuTTS Air voice cloning.

## Provided Reference Voices

### 1. male_professional.wav (Default)
- **Description**: Professional male executive voice
- **Use case**: CEO, CFO, male analyst responses
- **Duration**: ~8 seconds
- **Sample text** (in male_professional.txt):
  > "Thank you for joining our quarterly earnings call. We're pleased to report strong results across all business segments."

### 2. female_professional.wav
- **Description**: Professional female executive voice
- **Use case**: Female executive, investor relations
- **Duration**: ~8 seconds
- **Sample text** (in female_professional.txt):
  > "Good morning everyone. I'll be walking through our financial performance and key business metrics for the quarter."

## How Voice Cloning Works

NeuTTS Air uses **instant voice cloning** - it only needs 3-10 seconds of clean speech to clone a voice.

The system learns:
- Voice characteristics (pitch, timbre, accent)
- Speaking style (pace, intonation patterns)
- Natural speech patterns

## Creating Your Own Reference Voice

### Requirements

1. **Duration**: 5-10 seconds (longer is not always better)
2. **Content**: Natural, continuous speech (like a sentence or two)
3. **Quality**: Clean recording, minimal background noise
4. **Format**: WAV or MP3, 16-44kHz, mono channel
5. **Text file**: Transcription of the audio (must be exact)

### Steps

1. **Record your voice**:
   ```bash
   # macOS: Use QuickTime Player or Voice Memos
   # Export as: my_voice.wav
   ```

2. **Transcribe exactly**:
   Create `my_voice.txt` with the exact words spoken:
   ```
   This is my sample voice for testing the meeting intelligence system.
   ```

3. **Place in this directory**:
   ```bash
   cp my_voice.wav reference_voices/
   cp my_voice.txt reference_voices/
   ```

4. **Update credentials.yml**:
   ```yaml
   browser_audio:
     tts:
       reference_audio: reference_voices/my_voice.wav
       reference_text: reference_voices/my_voice.txt
   ```

5. **Test**:
   ```bash
   make train
   make inspect-voice
   ```

## Tips for Best Results

### ✅ Good Reference Audio
- Clear, crisp speech
- Natural conversation tone
- Single speaker, continuous
- No music or effects
- Professional recording environment

### ❌ Poor Reference Audio
- Multiple speakers overlapping
- Heavy background noise
- Whispered or shouted speech
- Phone call quality
- Echo or reverb

### Example Good Samples

**CEO introduction**:
> "Good afternoon. I'm pleased to be here today to discuss our company's strategic direction and financial performance."

**Analyst response**:
> "Thank you for taking my question. I'd like to understand more about your growth strategy in the Asian markets."

**Professional narration**:
> "In this meeting, we'll review our quarterly results, discuss market trends, and outline our plans for the coming year."

## Technical Specifications

All reference voices should meet:

- **Sample Rate**: 16-44kHz
- **Bit Depth**: 16-bit
- **Channels**: Mono (1 channel)
- **Format**: WAV (uncompressed) or MP3
- **Size**: < 5MB
- **Duration**: 3-15 seconds (optimal: 5-10s)

## Converting Audio Files

### To mono:
```bash
ffmpeg -i input.wav -ac 1 output_mono.wav
```

### To 16kHz:
```bash
ffmpeg -i input.wav -ar 16000 output_16k.wav
```

### Extract segment:
```bash
# Extract 8 seconds starting at 10s
ffmpeg -i input.wav -ss 10 -t 8 output_segment.wav
```

## Pre-encoded Reference Codes

For faster synthesis, NeuTTS Air can pre-encode reference voices:

```bash
# Pre-encode (saves as .pt file)
python -c "
from neuttsair.neutts import NeuTTSAir
tts = NeuTTSAir(backbone_repo='neuphonic/neutts-air-q4-gguf')
codes = tts.encode_reference('reference_voices/my_voice.wav')
import torch
torch.save(codes, 'reference_voices/my_voice.pt')
"
```

Then use in streaming mode for lower latency.

## Troubleshooting

### Issue: Voice sounds robotic
- **Solution**: Use longer, more natural speech sample (8-10s)
- **Solution**: Ensure reference audio is high quality (no compression artifacts)
- **Solution**: Try a different reference (some voices clone better than others)

### Issue: Voice doesn't match reference
- **Solution**: Make sure reference_text exactly matches the audio
- **Solution**: Check that reference audio is clean (no noise)
- **Solution**: Try re-recording with clearer speech

### Issue: Synthesis is slow
- **Solution**: Pre-encode reference voice (saves ~500ms per synthesis)
- **Solution**: Use GGUF Q4 model instead of Q8 (faster, minimal quality loss)
- **Solution**: Enable M4 GPU: set backbone_device='mps' in credentials.yml

## Example Use Cases

### 1. CEO Voice for Earnings Calls
Use male_professional.wav for natural-sounding CEO responses

### 2. Analyst Voice for Q&A
Create analyst_voice.wav with question-asking tone

### 3. Multi-speaker Scenarios
Create multiple reference voices:
- ceo_voice.wav
- cfo_voice.wav
- analyst1_voice.wav
- analyst2_voice.wav

Switch between them in your application logic.

---

**Need help?** See the main README.md for more information on NeuTTS Air configuration.