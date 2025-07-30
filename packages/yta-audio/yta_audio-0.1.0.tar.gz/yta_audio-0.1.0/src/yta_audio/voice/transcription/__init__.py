"""
Audio transcription made simple by using the classes
contained in this module.
"""
from yta_audio.voice.transcription.whisper import transcribe_whisper_without_timestamps, transcribe_whisper_with_timestamps, WhisperModel
from yta_audio.voice.transcription.objects import AudioTranscriptionWord, AudioTranscription, AudioTranscriptionWordTimestamp
from yta_validation import PythonValidator
from yta_file.handler import FileHandler
from yta_temp import Temp
from abc import ABC, abstractmethod
from typing import Union, BinaryIO
from io import BytesIO

import numpy as np


class _AudioTranscriptor(ABC):
    """
    Abstract class to be inherited by audio
    transcriptors that do not include timestamps.
    """

    @staticmethod
    @abstractmethod
    def transcribe(
        audio: any,
        initial_prompt: str
    ):
        """
        Transcribe the provided 'audio' with the help of
        the 'initial_prompt' if provided and get the
        transcripted text.
        """
        pass

class _TimestampedAudioTranscriptor(ABC):
    """
    Abstract class to be inherited by audio
    transciptors that include timestamps.
    """

    @staticmethod
    @abstractmethod
    def transcribe(
        audio: any,
        initial_prompt: str
    ):
        """
        Transcribe the provided 'audio' with the help of
        the 'initial_prompt' if provided and get the
        transcripted text with the time moments in which
        each word is detected.
        """
        pass

class DefaultAudioTranscriptor(_AudioTranscriptor):
    """
    Class to make the transcription more simple by
    choosing a transcriptor for you. You don't
    know which transcriptor you want to use? Use
    this one.
    """

    @staticmethod
    def transcribe(
        audio: Union[str, BinaryIO, BytesIO, np.ndarray],
        initial_prompt: Union[str, None] = None,
    ):
        return WhisperAudioTranscriptor.transcribe(audio, initial_prompt)
    
class DefaultTimestampedAudioTranscriptor(_TimestampedAudioTranscriptor):
    """
    Class to make the timestamped transcription more
    simple by choosing a timestamped transcriptor for
    you. You don't know which transcriptor you want
    to use? Use this one.
    """

    @staticmethod
    def transcribe(
        audio: Union[str, BinaryIO, BytesIO, np.ndarray],
        initial_prompt: Union[str, None] = None,
    ):
        return WhisperTimestampedAudioTranscriptor.transcribe(audio, initial_prompt)

class WhisperAudioTranscriptor(_AudioTranscriptor):
    """
    Whisper simple audio transcriptor that does
    not give timestamps of the the words said.
    """

    @staticmethod
    def transcribe(
        audio: Union[str, BinaryIO, BytesIO, np.ndarray],
        initial_prompt: Union[str, None] = None,
        model: WhisperModel = WhisperModel.BASE
    ):
        if (
            not PythonValidator.is_string(audio) and
            not PythonValidator.is_instance(audio, [BinaryIO, BytesIO]) and
            not PythonValidator.is_numpy_array(audio)
        ):
            raise Exception('The provided "audio" parameter is not a string, a BinaryIO nor a numpy array.')
        
        if (
            initial_prompt is not None and
            not PythonValidator.is_string(initial_prompt)
        ):
            raise Exception('The parameter "initial_prompt" given is not None nor a valid string.')

        # TODO: Try to do this without writing a file because
        # we could have no permission in the remote server
        # This below is very interesting for that purpose:
        # https://community.openai.com/t/openai-whisper-send-bytes-python-instead-of-filename/84786/5
        if PythonValidator.is_instance(audio, BytesIO):
            audio = FileHandler.write_binary(filename = Temp.get_filename('audio.wav'), binary_data = audio.read())
        elif PythonValidator.is_instance(audio, BinaryIO):
            audio = FileHandler.write_binary(filename = Temp.get_filename('audio.wav'), binary_data = audio.get_buffer())

        transcription = transcribe_whisper_without_timestamps(audio, initial_prompt, model)

        return AudioTranscription([
            # TODO: Do I have confidence here (?)
            AudioTranscriptionWord(
                word = word,
                timestamp = None,
                confidence = None
            )
            for word in transcription.split(' ')
        ])
    
class WhisperTimestampedAudioTranscriptor(_TimestampedAudioTranscriptor):
    """
    Whisper transcriptor that gives you the 
    timestamps of each of the transcripted words.
    """

    @staticmethod
    def transcribe(
        audio: Union[str, BinaryIO, BytesIO, np.ndarray],
        initial_prompt: Union[str, None] = None,
        model: WhisperModel = WhisperModel.BASE
    ):
        if (
            not PythonValidator.is_string(audio) and
            # TODO: If this is working, set 'BytesIO' in all of them
            not PythonValidator.is_instance(audio, [BinaryIO, BytesIO]) and
            not PythonValidator.is_numpy_array(audio)
        ):
            raise Exception('The provided "audio" parameter is not a string, a BinaryIO nor a numpy array.')
        
        if (
            initial_prompt is not None and
            not PythonValidator.is_string(initial_prompt)
        ):
            raise Exception('The parameter "initial_prompt" given is not None nor a valid string.')
        
        # TODO: Try to do this without writing a file because
        # we could have no permission in the remote server
        # This below is very interesting for that purpose:
        # https://community.openai.com/t/openai-whisper-send-bytes-python-instead-of-filename/84786/5
        if PythonValidator.is_instance(audio, BytesIO):
            audio = FileHandler.write_binary(filename = Temp.get_filename('audio.wav'), binary_data = audio.read())
        elif PythonValidator.is_instance(audio, BinaryIO):
            audio = FileHandler.write_binary(filename = Temp.get_filename('audio.wav'), binary_data = audio.get_buffer())
            
        words, _ = transcribe_whisper_with_timestamps(audio, initial_prompt, model)

        return AudioTranscription([
            AudioTranscriptionWord(
                word = word['text'],
                timestamp = AudioTranscriptionWordTimestamp(word['start'], word['end']),
                confidence = word['confidence']
            ) for word in words
        ])