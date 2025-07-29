from __future__ import annotations

import sys
from enum import StrEnum
from os import path
from pathlib import Path
from subprocess import run
from tempfile import gettempdir
from typing import Any
from uuid import uuid4

from moviepy.audio.io.AudioFileClip import AudioFileClip


class Synthesizer(StrEnum):
    AMAZON_POLLY = "AMAZON_POLLY"
    ESPEAK_NG = "ESPEAK_NG"
    MAC_OS = "MAC_OS"


class SimpleTalk:
    def __init__(
        self,
        *,
        voice: str | None = None,
        synthesizer: Synthesizer = Synthesizer.MAC_OS,
        engine: str | None = None,
    ) -> None:
        if synthesizer == Synthesizer.MAC_OS and sys.platform != "darwin":
            msg = "You must run the specified synthesizer on macOS."
            raise ValueError(msg)

        if synthesizer == Synthesizer.AMAZON_POLLY:
            import boto3
            self.__polly_client = boto3.client("polly")

            if not voice or not engine:
                msg = "You must specify engine and voice for Amazon Polly."
                raise ValueError(msg)

        self.__voice: str | None = voice
        self.__synthesizer: Synthesizer = synthesizer

    def talk(
        self,
        text: str,
        filename: str | None = None,
    ) -> str | AudioFileClip:
        return_clip: bool = filename is None
        filename = filename or path.join(gettempdir(), str(uuid4()))

        match self.__synthesizer:
            case Synthesizer.MAC_OS:
                filename = self.__talk_macos(text, filename)
            case Synthesizer.ESPEAK_NG:
                filename = self.__talk_espeak(text, filename)
            case Synthesizer.AMAZON_POLLY:
                filename = self.__talk_polly(text, filename)
            case _:
                msg = "The specified synthesizer is not implemented yet."
                raise NotImplementedError(msg)

        return AudioFileClip(filename) if return_clip else filename

    def __talk_macos(
        self,
        text: str,
        filename: str,
    ) -> str:
        run(
            args=[
                "say",
                text,
                # Specify voice if necessary
                *(
                    [
                        "-v",
                        self.__voice,
                    ] if self.__voice
                    else []
                ),
                "--file-format=mp4f",
                "-o",
                filename + ".mp4",
            ],
            check=True,
        )

        return filename + ".mp4"

    def __talk_espeak(
        self,
        text: str,
        filename: str,
    ) -> str:
        run(
            args=[
                "espeak-ng",
                text,
                # Specify voice if necessary
                *(
                    [
                        "-v",
                        self.__voice,
                    ] if self.__voice
                    else []
                ),
                "-w",
                filename + ".wav",
            ],
            check=True,
        )

        return filename + ".wav"

    def __talk_polly(
        self,
        text: str,
        filename: str,
    ) -> str:
        response: dict[str, Any] = self.__polly_client.synthesize_speech(
            OutputFormat="mp3",
            Text=text,
            VoiceId=self.__voice,
        )

        Path(filename + ".mp3").write_bytes(response["AudioStream"].read())

        return filename + ".mp3"
