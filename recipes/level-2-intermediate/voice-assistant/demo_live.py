#!/usr/bin/env python3
import asyncio
import os
import io
import time
import sys
from pathlib import Path
from dotenv import load_dotenv
import aiohttp
from pydub import AudioSegment
from pydub.playback import play
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.align import Align

# Load env variables
load_dotenv()
console = Console()

# Configuration
RASA_URL = "http://localhost:5005/webhooks/rest/webhook"
RIME_API_KEY = os.getenv("RIME_API_KEY")
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
AUDIO_DIR = Path("tests/audio")

# The Story Script
CONVERSATION_STEPS = [
    {"file": "user_input_1.wav", "label": "Transfer Request"},
    {"file": "user_input_2.wav", "label": "Account Selection"},
    {"file": "user_input_3.wav", "label": "Account Destination"},
    {"file": "user_input_4.wav", "label": "Amount"},
    {"file": "user_input_5.wav", "label": "Confirmation"},
]

def make_layout():
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
        Layout(name="status", size=3),
    )
    return layout

async def play_audio_data(audio_bytes: bytes):
    """Play raw audio bytes."""
    try:
        audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="wav")
        play(audio)
    except Exception as e:
        console.print(f"[red]Audio Error: {e}[/red]")

async def deepgram_transcribe(audio_path: Path) -> str:
    """Send audio to Deepgram."""
    url = "https://api.deepgram.com/v1/listen?model=nova-2&smart_format=true"
    headers = {"Authorization": f"Token {DEEPGRAM_API_KEY}", "Content-Type": "audio/wav"}
    
    with open(audio_path, "rb") as f:
        audio_data = f.read()

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=audio_data) as resp:
            data = await resp.json()
            return data['results']['channels'][0]['alternatives'][0]['transcript']

async def rime_tts(text: str) -> bytes:
    """Send text to Rime."""
    url = "https://users.rime.ai/v1/rime-tts"
    headers = {
        "Authorization": f"Bearer {RIME_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "speaker": "cove", 
        "modelId": "mistv2",
        "speedAlpha": 1.0,
        "reduceLatency": True 
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            data = await resp.json()
            import base64
            # Rime usually returns base64 in audioContent
            return base64.b64decode(data['audioContent'])

async def run_demo():
    layout = make_layout()
    
    header_text = Text("🎁 Unwrap the Future: Voice Orchestration", style="bold white on magenta", justify="center")
    layout["header"].update(Panel(header_text))
    
    with Live(layout, refresh_per_second=4) as live:
        
        for step in CONVERSATION_STEPS:
            audio_path = AUDIO_DIR / step['file']
            
            # --- STATE: USER SPEAKING ---
            status = Text(f"🔊 User is speaking... [{step['label']}]", style="bold cyan")
            layout["status"].update(Panel(status))
            layout["main"].update(Panel(Align.center(Text("Listening...", style="dim cyan")), title="User"))
            
            # Play user audio
            play(AudioSegment.from_wav(str(audio_path)))
            
            # --- STATE: TRANSCRIBING ---
            layout["status"].update(Panel(Text("⚡ Deepgram Transcribing...", style="bold yellow")))
            transcript = await deepgram_transcribe(audio_path)
            
            main_display = Text()
            main_display.append(f"User: ", style="bold cyan")
            main_display.append(f"{transcript}\n\n")
            layout["main"].update(Panel(main_display, title="Conversation Log"))
            
            # --- STATE: RASA THINKING ---
            layout["status"].update(Panel(Text("🧠 Rasa Thinking...", style="bold green")))
            async with aiohttp.ClientSession() as session:
                async with session.post(RASA_URL, json={"sender": "demo-user", "message": transcript}) as resp:
                    bot_responses = await resp.json()
            
            # --- STATE: AGENT SPEAKING ---
            for response in bot_responses:
                if 'text' in response:
                    agent_text = response['text']
                    
                    # Update UI
                    main_display.append(f"Agent: ", style="bold green")
                    main_display.append(f"{agent_text}\n")
                    layout["main"].update(Panel(main_display, title="Conversation Log"))
                    
                    layout["status"].update(Panel(Text("🗣️ Rime Generating & Speaking...", style="bold magenta")))
                    
                    # Generate and Play
                    audio_bytes = await rime_tts(agent_text)
                    await play_audio_data(audio_bytes)

            time.sleep(1) # Dramatic pause

        layout["status"].update(Panel(Text("✨ Demo Complete", style="bold white on green")))
        # Keep the final screen visible for a moment
        await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(run_demo())
    except KeyboardInterrupt:
        sys.exit(0)