#!/usr/bin/env python3
"""
Production Voice Testing with Real ASR/TTS
Uses actual speech services (Azure, Deepgram, etc.) for testing
"""

import asyncio
import os
from pathlib import Path
from typing import Optional

import aiohttp


# Color codes for terminal output
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'


# ============================================================================
# ASR (Speech-to-Text) Integration
# ============================================================================

async def transcribe_audio_azure(audio_file: Path) -> str:
    """Transcribe audio using Azure Speech Service."""
    try:
        import azure.cognitiveservices.speech as speechsdk
    except ImportError:
        raise ImportError("Install: pip install azure-cognitiveservices-speech")
    
    api_key = os.getenv("AZURE_SPEECH_API_KEY")
    region = os.getenv("AZURE_SPEECH_REGION", "eastus")
    
    if not api_key:
        raise ValueError("AZURE_SPEECH_API_KEY environment variable not set")
    
    speech_config = speechsdk.SpeechConfig(subscription=api_key, region=region)
    audio_config = speechsdk.audio.AudioConfig(filename=str(audio_file))
    
    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        audio_config=audio_config
    )
    
    result = speech_recognizer.recognize_once()
    
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text
    elif result.reason == speechsdk.ResultReason.NoMatch:
        raise Exception(f"No speech recognized in {audio_file}")
    else:
        raise Exception(f"ASR failed: {result.reason}")


async def transcribe_audio_deepgram(audio_file: Path) -> str:
    """Transcribe audio using Deepgram API."""
    api_key = os.getenv("DEEPGRAM_API_KEY")
    if not api_key:
        raise ValueError("DEEPGRAM_API_KEY environment variable not set")
    
    url = "https://api.deepgram.com/v1/listen"
    
    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "audio/wav"
    }
    
    params = {
        "model": "nova-2-general",
        "language": "en",
        "smart_format": "true"
    }
    
    with open(audio_file, "rb") as audio:
        audio_data = audio.read()
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, params=params, data=audio_data) as response:
            if response.status == 200:
                data = await response.json()
                transcript = data["results"]["channels"][0]["alternatives"][0]["transcript"]
                return transcript
            else:
                text = await response.text()
                raise Exception(f"Deepgram API error: {response.status} - {text}")


# ============================================================================
# TTS (Text-to-Speech) Integration
# ============================================================================

async def synthesize_speech_azure(text: str, output_file: Path) -> None:
    """Convert text to speech using Azure TTS."""
    try:
        import azure.cognitiveservices.speech as speechsdk
    except ImportError:
        raise ImportError("Install: pip install azure-cognitiveservices-speech")
    
    api_key = os.getenv("AZURE_SPEECH_API_KEY")
    region = os.getenv("AZURE_SPEECH_REGION", "eastus")
    
    if not api_key:
        raise ValueError("AZURE_SPEECH_API_KEY environment variable not set")
    
    speech_config = speechsdk.SpeechConfig(subscription=api_key, region=region)
    speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"
    
    audio_config = speechsdk.audio.AudioOutputConfig(filename=str(output_file))
    
    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=audio_config
    )
    
    result = synthesizer.speak_text_async(text).get()
    
    if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
        raise Exception(f"TTS failed: {result.reason}")


async def synthesize_speech_rime(text: str, output_file: Path) -> None:
    """Convert text to speech using Rime TTS."""
    api_key = os.getenv("RIME_API_KEY")
    if not api_key:
        raise ValueError("RIME_API_KEY environment variable not set")
    
    url = "https://users.rime.ai/v1/rime-tts"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "text": text,
        "speaker": "cove",
        "modelId": "mist",
        "speedAlpha": 1.0,
        "reduceLatency": False
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            if response.status == 200:
                # Rime returns JSON with audio data
                data = await response.json()
                
                # The response contains base64-encoded audio or URL
                if 'audioContent' in data:
                    # Base64 encoded audio
                    import base64
                    audio_bytes = base64.b64decode(data['audioContent'])
                    output_file.write_bytes(audio_bytes)
                    print(f"    Decoded {len(audio_bytes)} bytes from base64")
                    
                elif 'audio' in data:
                    # Might be base64 in 'audio' field
                    import base64
                    audio_bytes = base64.b64decode(data['audio'])
                    output_file.write_bytes(audio_bytes)
                    print(f"    Decoded {len(audio_bytes)} bytes from base64")
                    
                elif 'url' in data:
                    # Audio is at a URL
                    audio_url = data['url']
                    async with session.get(audio_url) as audio_response:
                        audio_bytes = await audio_response.read()
                        output_file.write_bytes(audio_bytes)
                        print(f"    Downloaded {len(audio_bytes)} bytes from URL")
                        
                else:
                    # Unknown format - show what we got
                    print(f"    Rime response keys: {list(data.keys())}")
                    print(f"    Response sample: {str(data)[:200]}")
                    raise Exception(f"Unexpected Rime response format. Keys: {list(data.keys())}")
                    
            else:
                text_resp = await response.text()
                raise Exception(f"Rime TTS error: {response.status} - {text_resp}")


async def synthesize_speech_deepgram(text: str, output_file: Path) -> None:
    """Convert text to speech using Deepgram TTS."""
    api_key = os.getenv("DEEPGRAM_API_KEY")
    if not api_key:
        raise ValueError("DEEPGRAM_API_KEY environment variable not set")
    
    url = "https://api.deepgram.com/v1/speak"
    
    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "application/json"
    }
    
    params = {
        "model": "aura-2-andromeda-en"
    }
    
    payload = {
        "text": text
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, params=params, json=payload) as response:
            if response.status == 200:
                audio_data = await response.read()
                output_file.write_bytes(audio_data)
            else:
                text_resp = await response.text()
                raise Exception(f"Deepgram TTS error: {response.status} - {text_resp}")


# ============================================================================
# Auto-detect which service to use
# ============================================================================

async def transcribe_audio(audio_file: Path) -> str:
    """Auto-detect and use available ASR service."""
    
    if os.getenv("DEEPGRAM_API_KEY"):
        print(f"  Using Deepgram ASR")
        return await transcribe_audio_deepgram(audio_file)
    elif os.getenv("AZURE_SPEECH_API_KEY"):
        print(f"  Using Azure ASR")
        return await transcribe_audio_azure(audio_file)
    else:
        raise ValueError(
            "No ASR service configured. Set one of:\n"
            "  - DEEPGRAM_API_KEY\n"
            "  - AZURE_SPEECH_API_KEY"
        )


async def synthesize_speech(text: str, output_file: Path) -> None:
    """Auto-detect and use available TTS service."""
    
    # Priority: Rime (matches Rasa config) > Deepgram > Azure
    if os.getenv("RIME_API_KEY"):
        print(f"  Using Rime TTS")
        await synthesize_speech_rime(text, output_file)
    elif os.getenv("DEEPGRAM_API_KEY"):
        print(f"  Using Deepgram TTS")
        await synthesize_speech_deepgram(text, output_file)
    elif os.getenv("AZURE_SPEECH_API_KEY"):
        print(f"  Using Azure TTS")
        await synthesize_speech_azure(text, output_file)
    else:
        raise ValueError(
            "No TTS service configured. Set one of:\n"
            "  - RIME_API_KEY (recommended - matches Rasa config)\n"
            "  - DEEPGRAM_API_KEY\n"
            "  - AZURE_SPEECH_API_KEY"
        )


# ============================================================================
# Example usage
# ============================================================================

async def example_test():
    """Example: Full voice test with real ASR/TTS."""
    
    print("Testing voice pipeline with real services...\n")
    
    sender_id = "voice-production-test"
    
    # 1. Transcribe test audio
    test_audio = Path("tests/audio/check_balance.wav")
    if not test_audio.exists():
        print(f"Test audio not found: {test_audio}")
        return
    
    print(f"1. Transcribing: {test_audio}")
    user_text = await transcribe_audio(test_audio)
    print(f"   Transcribed: '{user_text}'\n")
    
    # 2. Send to Rasa
    print(f"2. Sending to Rasa...")
    async with aiohttp.ClientSession() as session:
        response = await session.post(
            "http://localhost:5005/webhooks/rest/webhook",
            json={"sender": sender_id, "message": user_text}
        )
        
        if response.status == 200:
            bot_responses = await response.json()
        elif response.status == 404:
            print(f"   {Colors.RED}Error: REST channel not configured{Colors.RESET}")
            print(f"\n   {Colors.YELLOW}Solution:{Colors.RESET}")
            print(f"   1. Add this to data/credentials.yml:")
            print(f"      {Colors.GREEN}rest:{Colors.RESET}")
            print(f"   2. Restart Rasa: {Colors.GREEN}make run{Colors.RESET}\n")
            return
        else:
            error_text = await response.text()
            print(f"   {Colors.RED}Error: {response.status} - {error_text}{Colors.RESET}\n")
            return
    
    bot_text = " ".join([msg['text'] for msg in bot_responses if 'text' in msg])
    
    if not bot_text:
        print(f"   {Colors.YELLOW}Warning: Bot returned no text response{Colors.RESET}")
        print(f"   This might mean the flow is waiting for user input")
        print(f"   or the conversation hasn't started properly.\n")
        return
    
    print(f"   Bot said: '{bot_text}'\n")
    
    # 3. Convert bot response to speech
    output_audio = Path("tests/audio_responses/bot_response.wav")
    output_audio.parent.mkdir(exist_ok=True)
    
    print(f"3. Synthesizing speech...")
    await synthesize_speech(bot_text, output_audio)
    print(f"   Saved to: {output_audio}\n")
    
    print("✓ Full voice pipeline completed successfully!")


if __name__ == "__main__":
    asyncio.run(example_test())