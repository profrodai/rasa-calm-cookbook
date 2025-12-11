import asyncio
import json
import logging
import websockets
from dataclasses import dataclass
from typing import Any, Dict, Optional

from rasa.core.channels.voice_stream.asr.asr_engine import ASREngine, ASREngineConfig
from rasa.core.channels.voice_stream.asr.asr_event import ASREvent, NewTranscript
from rasa.core.channels.voice_stream.audio_bytes import RasaAudioBytes

logger = logging.getLogger(__name__)

@dataclass
class LocalASRConfig(ASREngineConfig):
    """Configuration for Local ASR."""
    endpoint: str = "ws://localhost:9001"

class LocalASR(ASREngine[LocalASRConfig]):
    """
    Rasa ASR Engine that connects to a local Faster-Whisper WebSocket server.
    """
    def __init__(self, config: LocalASRConfig):
        super().__init__(config)
        self.websocket = None

    @classmethod
    def from_config_dict(cls, config: Dict[str, Any]) -> "LocalASR":
        return cls(LocalASRConfig.from_dict(config))

    @staticmethod
    def get_default_config() -> LocalASRConfig:
        return LocalASRConfig()

    async def open_websocket_connection(self):
        """Establishes connection to the local Python server."""
        try:
            self.websocket = await websockets.connect(self.config.endpoint)
            logger.info(f"Connected to Local ASR at {self.config.endpoint}")
            return self.websocket
        except Exception as e:
            logger.error(f"Failed to connect to Local ASR: {e}. Is 'make run-local-asr' running?")
            raise

    async def signal_audio_done(self):
        """
        Called when Rasa detects silence (VAD).
        We send a JSON signal to the server to process the buffered audio.
        """
        if self.websocket:
            await self.websocket.send(json.dumps({"action": "transcribe"}))

    def rasa_audio_bytes_to_engine_bytes(self, chunk: RasaAudioBytes) -> bytes:
        """Pass raw bytes through (transcoding happens on server)."""
        return chunk

    def engine_event_to_asr_event(self, event: Any) -> Optional[ASREvent]:
        """
        Convert server response to Rasa Event.
        Server sends: {"text": "Hello world", "is_final": true}
        """
        try:
            data = json.loads(event)
            if "text" in data and data["text"]:
                return NewTranscript(data["text"])
        except Exception:
            pass
        return None