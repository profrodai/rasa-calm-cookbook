# Voice Assistant - Banking Support with Speech

A voice-enabled banking assistant that handles account inquiries, transactions, and customer support through natural speech interaction using Rime TTS and Deepgram ASR.

## Overview

This recipe demonstrates:
- Voice input/output with browser audio
- Speech-to-text with Deepgram
- Text-to-speech with Rime AI
- Voice-optimized conversation flows
- Silence handling and timeout management
- Natural language processing for voice interactions

## Use Case

A voice banking assistant that helps customers:
- Check account balances
- Transfer money between accounts
- Report lost or stolen cards
- Get transaction history
- Speak naturally without rigid command structures

## Features

- **Browser-based voice interface** - No phone number needed
- **Natural speech recognition** - Deepgram Nova 2 model
- **High-quality voice synthesis** - Rime AI TTS
- **Voice-optimized flows** - Shorter responses for voice
- **Silence detection** - Automatic timeout handling
- **Error recovery** - Voice-specific repair patterns

## Prerequisites

- Python 3.10 or 3.11
- Valid Rasa Pro license
- Deepgram API key (get from https://deepgram.com)
- Rime AI API key (get from https://rime.ai)
- OpenAI API key (or alternative LLM provider)
- Modern web browser with microphone access

## Quick Start

### 1. Navigate to Recipe
```bash
cd recipes/level-2-intermediate/voice-assistant
```

### 2. Set Up Environment
```bash
# Create .env file
make setup-env

# Edit .env with your credentials
# Required:
#   RASA_LICENSE
#   OPENAI_API_KEY
#   DEEPGRAM_API_KEY
#   RIME_API_KEY
```

### 3. Install Dependencies
```bash
make setup-recipe
```

### 4. Configure LLM Provider
```bash
make config-openai  # or config-azure, config-local
```

### 5. Train and Test
```bash
# Train the model
make train

# Test with voice in browser
make inspect-voice

# Or test with text
make inspect
```

## Voice Testing

### Browser Audio Testing
The `make inspect-voice` command starts Rasa inspector with voice enabled:

1. Opens browser to inspector interface
2. Click microphone icon to enable voice
3. Grant microphone permissions
4. Speak your request
5. Hear AI response

### Voice Commands to Try
- "What's my account balance?"
- "I want to transfer $500 to my savings account"
- "I lost my credit card"
- "Show me recent transactions"
- "Help me with my account"

## Configuration Options

### Speech Services

**Deepgram ASR (Speech-to-Text)**
- Model: `nova-2-general`
- Language: English (US)
- Features: Smart formatting, punctuation
- Endpointing: 400ms silence detection

**Rime TTS (Text-to-Speech)**
- Speaker: `cove` (natural male voice)
- Model: `mistv2`
- Speed: Normal (1.0)
- Streaming: Real-time audio generation

### Alternative Providers

You can switch speech providers by editing `credentials.yml`:
```yaml
browser_audio:
  asr:
    name: azure  # or deepgram
  tts:
    name: cartesia  # or azure, deepgram, rime
```

## Voice-Specific Design Patterns

### 1. Shorter Responses
Voice responses are more concise than text:
```yaml
responses:
  utter_ask_transfer_amount:
    - text: "How much would you like to transfer?"  # Voice
    - text: "Please enter the amount you'd like to transfer. You can specify it in dollars (e.g., $100 or 100 dollars)."  # Text
      metadata:
        channel: web
```

### 2. Confirmation Patterns
Always confirm critical actions:
```yaml
- collect: transfer_confirmation
  description: "Confirm the transfer details"
  rejections:
    - if: not slots.transfer_confirmation
      utter: utter_transfer_cancelled
```

### 3. Silence Handling
Configure timeout for user responses:
```yaml
# endpoints.yml
interaction_handling:
  global_silence_timeout: 7  # seconds
```

### 4. Error Recovery
Voice-specific error messages:
```yaml
responses:
  utter_did_not_understand:
    - text: "Sorry, I didn't catch that. Could you repeat?"
  utter_please_speak_clearly:
    - text: "I'm having trouble hearing you. Please speak clearly."
```

## Project Structure

### Flows (`data/flows.yml`)
- `check_balance` - Account balance inquiry
- `transfer_money` - Inter-account transfers
- `report_lost_card` - Card loss reporting
- `transaction_history` - Recent transaction viewing

### Custom Actions (`actions/actions.py`)
- `action_get_account_balance` - Retrieves balance from mock database
- `action_get_accounts` - Lists user's accounts
- `action_process_transfer` - Executes money transfer
- `action_block_card` - Blocks lost/stolen card

### Voice Configuration (`credentials.yml`)
- Browser audio channel setup
- Deepgram ASR configuration
- Rime TTS configuration
- Audio format settings

## Testing

### End-to-End Tests
```bash
# Run all tests
make test-e2e

# Test voice flows specifically
make test-voice
```

### Manual Testing
```bash
# Text-based testing
make shell

# Voice testing in browser
make inspect-voice

# Run action server separately
make run-actions
```

## Sample Conversations

### Balance Check
User: "What's my balance?"
Bot: "Your checking account has a balance of $2,450.75."

### Money Transfer
User: "I need to transfer money"
Bot: "Which account would you like to transfer from?"
User: "My checking account"
Bot: "Where would you like to transfer to?"
User: "Savings"
Bot: "How much would you like to transfer?"
User: "Five hundred dollars"
Bot: "Transferring $500 from checking to savings. Is that correct?"
User: "Yes"
Bot: "Done. $500 has been transferred."

### Lost Card
User: "I lost my credit card"
Bot: "I'm sorry to hear that. I'll help you block your card right away."
Bot: "For security, which is the last four digits of your card?"
User: "4532"
Bot: "Thank you. Your card ending in 4532 has been blocked."

## Voice-Specific Considerations

### Best Practices
1. **Keep responses under 3 sentences** for voice
2. **Use natural, conversational language**
3. **Avoid complex numbers** - say "twenty-five hundred" not "2,500.00"
4. **Provide clear next steps** in each response
5. **Handle silence gracefully** with prompts

### Common Issues

**Microphone not working**
- Check browser permissions
- Ensure HTTPS or localhost
- Try different browser

**Poor recognition**
- Speak clearly and at normal pace
- Reduce background noise
- Check microphone quality

**Voice cuts off**
- Adjust silence timeout in endpoints.yml
- Increase `endpointing` value in credentials.yml

## Production Deployment

For production voice assistants:

1. **Use HTTPS** - Required for microphone access
2. **Configure CDN** - For audio file delivery
3. **Monitor latency** - Track speech recognition delays
4. **Set up analytics** - Log voice interaction metrics
5. **Plan fallbacks** - Text input as backup

## Next Steps

After mastering this recipe:
- [Enterprise Search](../enterprise-search/) - Add voice-based FAQ
- [Multi-LLM Routing](../multi-llm-routing/) - Optimize costs
- [Fine-Tuning](../../level-3-advanced/fine-tuning/) - Improve performance

## Troubleshooting

See [Voice Assistant Troubleshooting](../../../docs/troubleshooting.md#voice-assistant-issues) for common solutions.

## Resources

- [Rasa Voice Documentation](https://rasa.com/docs/rasa-pro/voice)
- [Deepgram Documentation](https://developers.deepgram.com)
- [Rime AI Documentation](https://rime.ai/docs)
- [Browser Audio Channel](https://rasa.com/docs/rasa-pro/channels/browser-audio)