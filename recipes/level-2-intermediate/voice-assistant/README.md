# Voice Assistant - Banking Support with Speech

A production-ready voice-enabled banking assistant that handles account inquiries, transactions, and customer support through natural speech interaction using Deepgram ASR and Rime TTS.

## Overview

This recipe demonstrates:
- **Real voice input/output** with Deepgram ASR and Rime TTS
- **Voice-optimized conversation flows** with proper slot management
- **Automated voice testing pipeline** with real ASR/TTS services
- **Multi-turn conversation handling** with state persistence
- **Voice-specific regex patterns** for transcribed input (e.g., "4 5 3 2" → "4532")
- **Natural language processing** for banking operations

## Use Case

A voice banking assistant that helps customers:
- Check account balances (voice-optimized)
- Transfer money between accounts (with confirmation)
- Report lost or stolen cards (with verification)
- Get transaction history
- Speak naturally without rigid command structures

## Features

- ✅ **Browser-based voice interface** - No phone number needed
- ✅ **Natural speech recognition** - Deepgram Nova 2 model with smart formatting
- ✅ **High-quality voice synthesis** - Rime AI TTS with natural voice
- ✅ **Voice-optimized flows** - Flexible regex for voice-transcribed digits
- ✅ **Silence detection** - 7-second global timeout with graceful handling
- ✅ **Automated testing** - Production voice testing with real ASR/TTS services
- ✅ **Slot reset management** - Proper cleanup between conversation flows
- ✅ **Action server integration** - Custom banking actions with error handling

## Prerequisites

- Python 3.10 or 3.11
- Valid Rasa Pro license
- **Deepgram API key** (get from https://deepgram.com)
- **Rime AI API key** (get from https://rime.ai)
- OpenAI API key (or alternative LLM provider)
- Modern web browser with microphone access
- **Two terminal windows** for running Rasa + action servers

## Quick Start

### 1. Navigate to Recipe
```bash
cd recipes/level-2-intermediate/voice-assistant
```

### 2. Set Up Environment
```bash
# Create .env file from template
make setup-env

# Edit .env with your credentials
# Required:
#   RASA_LICENSE=your-rasa-pro-license
#   OPENAI_API_KEY=your-openai-key
#   DEEPGRAM_API_KEY=your-deepgram-key
#   RIME_API_KEY=your-rime-key
```

### 3. Install Dependencies
```bash
# Verify dependencies are installed (from repo root)
make setup-recipe
```

### 4. Configure LLM Provider
```bash
make config-openai  # or config-azure, config-local
```

### 5. Train the Model
```bash
make train
```

### 6. Run the Assistant

**You need TWO terminals running simultaneously:**

**Terminal 1 - Rasa Server:**
```bash
make run
# Server starts on http://localhost:5005
```

**Terminal 2 - Action Server:**
```bash
make run-actions
# Action server starts on http://localhost:5055
```

### 7. Test with Voice

**Terminal 3 - Run Voice Tests:**
```bash
# Automated voice testing with real ASR/TTS
make test-voice-production
```

**OR manually test in browser:**
```bash
make inspect-voice
```

## Voice Testing Pipeline

### Automated Production Testing

This recipe includes a **complete automated voice testing system** that uses real ASR/TTS services:

```bash
make generate-test-audio
make test-voice-production
```

**What it does:**
1. **Transcribes** pre-generated audio files using Deepgram ASR
2. **Sends** transcribed text to Rasa REST API
3. **Receives** agent responses from conversation flows
4. **Synthesizes** audio responses using Rime TTS
5. **Saves** all audio outputs for manual verification
6. **Validates** complete multi-turn conversations

**Test flows included:**
- ✅ Check Balance (2 turns)
- ✅ Transfer Money (5 turns) - Tests custom actions
- ✅ Lost Card (2 turns) - Tests card blocking action

**Output:**
```
tests/audio_responses/
├── check_balance/
│   ├── turn_1_response.wav
│   └── turn_2_response.wav
├── transfer_money/
│   ├── turn_1_response.wav
│   ├── turn_2_response.wav
│   ├── turn_3_response.wav
│   ├── turn_4_response.wav
│   └── turn_5_response.wav
└── lost_card/
    ├── turn_1_response.wav
    └── turn_2_response.wav
```

### Pre-generated Test Audio

Test audio inputs are pre-generated and stored in:
```
tests/audio/
├── check_balance.wav
├── checking.wav
├── savings.wav
├── five_hundred.wav
├── yes.wav
├── lost_card.wav
├── card_digits.wav
└── ...
```

These files simulate realistic voice input for automated testing without requiring live microphone input.

### Browser Audio Testing
```bash
make inspect-voice
```

1. Opens browser to inspector interface
2. Click microphone icon to enable voice
3. Grant microphone permissions when prompted
4. Speak your request naturally
5. Hear AI-generated voice response

### Voice Commands to Try

**Balance Check:**
- "What's my balance?"
- "Check my account balance"
- "How much money do I have?"

**Money Transfer:**
- "I want to transfer money"
- "Transfer five hundred dollars to savings"
- "Move money between accounts"

**Lost Card:**
- "I lost my credit card"
- "My card was stolen"
- "I need to block my card"

**Transaction History:**
- "Show me recent transactions"
- "What are my latest purchases?"
- "Transaction history"

## Voice-Specific Implementation Details

### 1. Flexible Digit Recognition

Voice transcription often adds spaces between digits. Our flows handle this:

**Before (Failed):**
```yaml
# Strict regex - fails on voice input
validation:
  - type: regex
    pattern: "^\\d{4}$"  # Only matches "4532"
```

**After (Works with Voice):**
```yaml
# Flexible regex - handles "4 5 3 2" or "4532"
validation:
  - type: regex
    pattern: "^\\d[\\s]?\\d[\\s]?\\d[\\s]?\\d$"
```

**Action Processing:**
```python
def clean_digits(text: str) -> str:
    """Remove spaces from voice-transcribed digits"""
    return ''.join(c for c in text if c.isdigit())

# "4 5 3 2" → "4532"
```

### 2. Slot Reset Management

**Critical for multi-conversation handling:**

```yaml
# flows-voice-fixed.yml
- action: action_process_transfer
- set_slots:
    - transfer_from_account: null
    - transfer_to_account: null
    - transfer_amount: null
    - transfer_confirmation: null
```

Without slot resets:
- ❌ Previous values persist across conversations
- ❌ "checking" repeats on every question
- ❌ Flows get stuck in loops

With slot resets:
- ✅ Clean state for each conversation
- ✅ No value persistence between flows
- ✅ Proper multi-turn handling

### 3. Voice-Optimized Responses

**Concise for voice, detailed for text:**

```yaml
responses:
  utter_ask_transfer_amount:
    - text: "How much would you like to transfer?"
      # Short and natural for voice

  utter_transfer_complete:
    - text: "Done. ${transfer_amount} has been transferred from your {transfer_from_account} to your {transfer_to_account}."
      # Clear confirmation with all details
```

### 4. Silence Handling

**Global timeout configuration:**

```yaml
# endpoints.yml
interaction_handling:
  global_silence_timeout: 7  # seconds
  consecutive_silence_timeouts: 0
```

**Per-conversation timeout:**
```yaml
# credentials.yml
browser_audio:
  asr:
    endpointing: 400  # ms - when to stop listening
    utterance_end_ms: 1000  # ms - silence before processing
```

## Configuration

### Speech Services Configuration

**Deepgram ASR (credentials.yml):**
```yaml
browser_audio:
  asr:
    name: "deepgram"
    language: "en"
    model: "nova-2-general"
    smart_format: true
    endpointing: 400
    utterance_end_ms: 1000
```

**Rime TTS (credentials.yml):**
```yaml
  tts:
    name: "rime"
    speaker: "cove"
    model_id: "mistv2"
    speed_alpha: 1.0
    segment: "immediate"
    timeout: 30
```

### Action Server Configuration

**endpoints.yml:**
```yaml
action_endpoint:
  url: "http://localhost:5055/webhook"
```

**Must run action server separately:**
```bash
make run-actions  # Terminal 2
```

## Project Structure

### Core Files

```
.
 │   actions
 │    │   __pycache__
 │    │   actions.py
 │   config-azure.yml
 │   config-local.yml
 │   config-openai.yml
 │   config.yml
 │   conversations
 │    │   sample_conversations.md
 │   credentials.yml
 │   data
 │    │   flows.yml
 │   domain.yml
 │   endpoints.yml
 │   Makefile
 │   models
 │    │   20251210-100424-purple-fern.tar.gz
 │   pyproject.toml
 │   README.md
 │   tests
 │    │   e2e_test_cases.yml
 │    │   generate_test_audio.py
 │    │   test_voice_automated.py
 │    │   test_voice_full_pipeline.py
 │    │   test_voice_production.py

```

### Conversation Flows

**1. Check Balance (`check_balance`)**
- Single-turn or with account type specification
- Retrieves balance from mock database
- Voice-optimized response format

**2. Transfer Money (`transfer_money`)**
- Multi-turn conversation (5 turns)
- Collects: from account, to account, amount
- Confirms before executing
- **Requires action server** for `action_process_transfer`
- Resets all slots after completion

**3. Report Lost Card (`report_lost_card`)**
- Security-focused flow
- Collects last 4 digits with flexible regex
- **Requires action server** for `action_block_card`
- Provides timeline for replacement card

**4. Transaction History (`transaction_history`)**
- Retrieves recent account activity
- Requires action server for `action_get_transactions`

### Custom Actions

Located in `actions/actions.py`:

```python
# action_get_account_balance
# Returns balance for specified account type

# action_process_transfer
# Executes money transfer between accounts
# Cleans voice-transcribed amounts

# action_block_card
# Blocks lost/stolen card
# Handles space-separated digits from voice

# action_get_transactions
# Retrieves transaction history

# action_get_accounts
# Lists all user accounts
```

## Testing

### Automated Voice Testing

**Production testing with real services:**
```bash
make generate-test-audio
make test-voice-production
```

**Requirements:**
- ✅ Rasa server running (Terminal 1)
- ✅ Action server running (Terminal 2)
- ✅ DEEPGRAM_API_KEY in environment
- ✅ RIME_API_KEY in environment

**Output:**
- Console: Turn-by-turn conversation logs
- Files: Audio responses in `tests/audio_responses/`
- Validation: All flows pass/fail status

### Manual Testing

**Voice testing in browser:**
```bash
make inspect-voice
```

**Text-based testing:**
```bash
make shell
# or
make inspect
```

**End-to-end tests:**
```bash
make test-e2e
```

## Sample Conversations

### Balance Check (Voice-Optimized)

```
User: "What's my balance?"
Bot: "Your checking account has a balance of $2,450.75. Is there anything else I can help you with?"

User: "Checking"
Bot: "Is there anything else I can help you with?"
```

### Money Transfer (Complete Flow)

```
User: "I want to transfer money"
Bot: "Which account would you like to transfer from?"

User: "Checking"
Bot: "Which account should I transfer to?"

User: "Savings"
Bot: "How much would you like to transfer?"

User: "Five hundred dollars"
Bot: "Transferring $500 from Checking to Savings. Is that correct?"

User: "Yes"
Bot: "Done. $500 has been transferred from your Checking to your Savings. Is there anything else I can help you with?"
```

### Lost Card (Voice Digits Handling)

```
User: "I lost my card"
Bot: "I'm sorry to hear that. I'll help you block your card right away. For security, what are the last four digits of your card?"

User: "4 5 3 2"  # Voice transcription with spaces
Bot: "Your card ending in 4532 has been blocked. A replacement will be sent in five to seven business days. Is there anything else I can help you with?"
```

## Development Workflow

### Typical Development Session

**1. Start servers (2 terminals):**
```bash
# Terminal 1
make train
make run

# Terminal 2
make run-actions
```

**2. Make changes to flows:**
```bash
# Edit data/flows.yml
# Edit actions/actions.py
```

**3. Retrain and test:**
```bash
# Terminal 3
make generate-test-audio
make test-voice-production
```

**4. Manual verification:**
```bash
make inspect-voice
# Test with real microphone
```

### Adding New Flows

1. **Define flow** in `data/flows.yml`
2. **Add responses** in `domain.yml`
3. **Create action** (if needed) in `actions/actions.py`
4. **Add test audio** in `tests/audio/`
5. **Update test script** in `tests/test_voice_production.py`
6. **Train and test:**
   ```bash
   make train
   make generate-test-audio
   make test-voice-production
   ```

### Voice-Specific Design Patterns

**✅ DO:**
- Keep responses under 2-3 sentences
- Use natural, conversational language
- Always confirm critical actions (transfers, blocks)
- Handle spaces in voice-transcribed numbers
- Reset slots after completing flows
- Provide clear next steps

**❌ DON'T:**
- Use complex numbers in speech ("two thousand four hundred fifty point seven five")
- Require exact formatting for voice input
- Carry over slot values between conversations
- Skip confirmation for destructive actions
- Use technical jargon or long explanations

## Troubleshooting

### Action Server Errors

**Error:** `Cannot connect to host localhost:5055`

**Solution:**
```bash
# Make sure action server is running in separate terminal
make run-actions

# Verify it's listening:
# Should see: "Action endpoint is up and running on http://0.0.0.0:5055"
```

### Voice Tests Failing

**Error:** `Connection refused to localhost:5005`

**Solution:**
```bash
# Ensure Rasa server is running
make run

# Verify: http://localhost:5005 is accessible
```

### Microphone Not Working

**Check:**
1. Browser permissions granted
2. Using HTTPS or localhost
3. Microphone works in other apps
4. Try different browser (Chrome recommended)

### Poor Recognition Quality

**Solutions:**
- Reduce background noise
- Speak clearly at normal pace
- Use good quality microphone
- Check Deepgram service status

### Slot Values Persisting

**Problem:** Previous conversation values appear in new conversations

**Solution:** Ensure slot resets are in flows:
```yaml
- action: your_action
- set_slots:
    - slot_name: null  # Reset to null
```

### Voice Tests Show "Did not understand"

**Check:**
1. Test audio files exist in `tests/audio/`
2. Deepgram API key is valid
3. Rime API key is valid
4. Network connectivity to services

## Production Considerations

### Deployment Checklist

- ✅ **HTTPS enabled** (required for microphone access)
- ✅ **Action server** running and accessible
- ✅ **API keys** stored securely (not in code)
- ✅ **Monitoring** for ASR/TTS latency
- ✅ **Error handling** for speech service failures
- ✅ **Rate limiting** on speech API calls
- ✅ **Fallback to text** if voice unavailable
- ✅ **Analytics** for conversation metrics

### Performance Optimization

**ASR Latency:**
- Adjust `endpointing` in credentials.yml
- Use Deepgram's streaming mode
- Monitor network latency to services

**TTS Quality:**
- Test different Rime voices/models
- Adjust `speed_alpha` for pacing
- Cache common responses

**Action Server:**
- Use connection pooling for database
- Implement retry logic for failures
- Add health check endpoints

## Cost Optimization

**Deepgram ASR:**
- Pre-process audio to reduce dead time
- Use appropriate model (nova-2 is fast + accurate)

**Rime TTS:**
- Cache common responses
- Minimize response length

**OpenAI API:**
- Use prompt caching where available
- Consider cheaper models for simple queries
- Implement request deduplication

## Next Steps

After mastering this recipe:

1. **Add more banking flows** - Bill payment, loan inquiry
2. **Implement authentication** - Voice biometrics, PIN verification
3. **Multi-language support** - Spanish, French using Deepgram
4. **Custom voice** - Brand-specific TTS with Rime
5. **Analytics dashboard** - Track conversation metrics
6. **A/B testing** - Test response variations

### Related Recipes

- [Enterprise Search](../enterprise-search/) - Add voice-based FAQ
- [Multi-LLM Routing](../multi-llm-routing/) - Optimize LLM costs
- [Guardrails](../guardrails/) - Add content safety
- [Fine-Tuning](../../level-3-advanced/fine-tuning/) - Improve accuracy

## Resources

### Documentation
- [Rasa Speech Integration](https://rasa.com/docs/reference/integrations/speech-integrations)
- [Deepgram API Reference](https://developers.deepgram.com/reference)
- [Rime AI Documentation](https://docs.rime.ai/)
- [Rasa Voice Assistants](https://rasa.com/docs/pro/build/voice-assistants)

### Community
- [Rasa Forum](https://forum.rasa.com/)
- [Agent Engineering Community](https://info.rasa.com/community)

## Support

For issues specific to this recipe:
1. Check the troubleshooting section above
2. Review logs in Rasa server output
3. Verify action server is running
4. Test with `make shell` first (text mode)
5. Post in the Agent Engineering Community with logs

## License

This recipe is part of the Rasa Pro examples and follows the same license terms.

---

*Last updated: December 2025*