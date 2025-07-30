import base64
import io
import json
from typing import Generator, Optional

import requests

from .http_client import HttpClient
from .typings.tts import AudioConfig
from .typings.tts import TTSLanguageCodes
from .typings.tts import TTSVoices
from .typings.tts import VoiceResponse


class TTS:
    """TTS API client"""

    def __init__(
        self,
        client: HttpClient,
        audioConfig: Optional[AudioConfig] = None,
        languageCode: Optional[TTSLanguageCodes] = None,
        modelId: Optional[str] = None,
        voice: Optional[TTSVoices] = None,
    ):
        """Constructor for TTS class"""
        self.__audioConfig = audioConfig or None
        self.__client = client
        self.__languageCode = languageCode or "en-US"
        self.__modelId = modelId or None
        self.__voice = voice or "Emma"

    @property
    def audioConfig(self) -> AudioConfig:
        """Get default audio config"""
        return self.__audioConfig

    @audioConfig.setter
    def audioConfig(self, audioConfig: AudioConfig):
        """Set default audio config"""
        self.__audioConfig = audioConfig

    @property
    def languageCode(self) -> TTSLanguageCodes:
        """Get default language code"""
        return self.__languageCode

    @languageCode.setter
    def languageCode(self, languageCode: TTSLanguageCodes):
        """Set default language code"""
        self.__languageCode = languageCode

    @property
    def modelId(self) -> str:
        """Get default model ID"""
        return self.__modelId

    @modelId.setter
    def modelId(self, modelId: str):
        """Set default model ID"""
        self.__modelId = modelId

    @property
    def voice(self) -> TTSVoices:
        """Get default voice"""
        return self.__voice

    @voice.setter
    def voice(self, voice: TTSVoices):
        """Set default voice"""
        self.__voice = voice

    def synthesizeSpeech(
        self,
        input: str,
        voice: Optional[TTSVoices] = None,
        languageCode: Optional[TTSLanguageCodes] = None,
        modelId: Optional[str] = None,
        audioConfig: Optional[AudioConfig] = None,
    ) -> dict:
        """Synthesize speech"""
        data = {
            "input": {"text": input},
            "voice": {
                "name": voice or self.__voice,
                "languageCode": languageCode or self.__languageCode,
            },
        }

        if audioConfig or self.__audioConfig:
            data["audioConfig"] = audioConfig or self.__audioConfig

        if modelId or self.__modelId:
            data["modelId"] = modelId or self.__modelId

        return self.__client.request(
            "post",
            "/tts/v1alpha/text:synthesize-sync",
            data=data,
        )

    def synthesizeSpeechAsWav(
        self,
        input: str,
        voice: Optional[TTSVoices] = None,
        languageCode: Optional[TTSLanguageCodes] = None,
        modelId: Optional[str] = None,
        audioConfig: Optional[AudioConfig] = None,
    ) -> io.BytesIO:
        """Synthesize speech as WAV response"""
        if audioConfig is not None:
            audioConfig["audioEncoding"] = "AUDIO_ENCODING_UNSPECIFIED"

        response = self.synthesizeSpeech(
            input=input,
            voice=voice,
            languageCode=languageCode,
            modelId=modelId,
            audioConfig=audioConfig,
        )

        decoded_audio_bytes = base64.b64decode(response.get("audioContent"))

        return io.BytesIO(decoded_audio_bytes)

    def synthesizeSpeechStream(
        self,
        input: str,
        voice: Optional[TTSVoices] = None,
        languageCode: Optional[TTSLanguageCodes] = None,
        modelId: Optional[str] = None,
        audioConfig: Optional[AudioConfig] = None,
    ) -> requests.Response:
        """Synthesize speech as a stream"""
        data = {
            "input": {"text": input},
            "voice": {
                "name": voice or self.__voice,
                "languageCode": languageCode or self.__languageCode,
            },
        }

        if audioConfig or self.__audioConfig:
            data["audioConfig"] = audioConfig or self.__audioConfig

        if modelId or self.__modelId:
            data["modelId"] = modelId or self.__modelId

        return self.__client.stream(
            "post",
            "/tts/v1alpha/text:synthesize",
            data=data,
        )

    def synthesizeSpeechStreamAsWav(
        self,
        input: str,
        modelId: Optional[str] = None,
        voice: Optional[TTSVoices] = None,
        languageCode: Optional[TTSLanguageCodes] = None,
        audioConfig: Optional[AudioConfig] = None,
    ) -> Generator[bytes, None, io.BytesIO]:
        """Synthesize speech as WAV response from streamed data"""
        if audioConfig is not None:
            audioConfig["audioEncoding"] = "AUDIO_ENCODING_UNSPECIFIED"

        response = self.synthesizeSpeechStream(
            input=input,
            modelId=modelId,
            voice=voice,
            languageCode=languageCode,
            audioConfig=audioConfig,
        )

        audio_buffer = io.BytesIO()
        for chunk in response.iter_lines():
            if chunk:
                try:
                    chunk_data = json.loads(chunk)
                    if "result" in chunk_data and "audioContent" in chunk_data["result"]:
                        audio_data = base64.b64decode(chunk_data["result"]["audioContent"])
                        audio_buffer.write(audio_data)
                        yield audio_data
                except json.JSONDecodeError:
                    continue

        audio_buffer.seek(0)
        return audio_buffer

    def voices(
        self,
        languageCode: Optional[TTSLanguageCodes] = None,
        modelId: Optional[str] = None,
    ) -> list[VoiceResponse]:
        """Get voices"""
        data = {}
        if languageCode:
            data["languageCode"] = languageCode
        if modelId:
            data["modelId"] = modelId

        response = self.__client.request("get", "/tts/v1alpha/voices", data=data)
        return response.get("voices")
