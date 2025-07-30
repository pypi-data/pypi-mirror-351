from yta_audio.voice.enums import NarrationLanguage, VoiceSpeed, VoiceEmotion, VoicePitch
from dataclasses import dataclass
from abc import abstractmethod


@dataclass
class NarrationVoice:
    """
    Dataclass to be implemented by other custom
    dataclasses that will determine the narration
    voice parameters of our voice narration 
    engines.
    """

    name: str
    """
    The voice narration name.
    """
    emotion: VoiceEmotion
    """
    The voice narration emotion.
    """
    speed: VoiceSpeed
    """
    The voice narration desired speed.
    """
    pitch : VoicePitch
    """
    The voice narration desired pitch.
    """
    language: NarrationLanguage
    """
    The language to be used with the voice narration.
    """
    # TODO: Maybe add something more like
    # pitch or something

    def __init__(
        self,
        name: str = '',
        emotion: VoiceEmotion = VoiceEmotion.DEFAULT,
        speed: VoiceSpeed = VoiceSpeed.DEFAULT,
        pitch: VoicePitch = VoicePitch.DEFAULT,
        language: NarrationLanguage = NarrationLanguage.DEFAULT
    ):
        self.validate(name, emotion, speed, pitch, language)

        # TODO: Maybe we could receive an Enum name 
        # and we need to parse it
        self.name = name
        self.emotion = VoiceEmotion.to_enum(emotion)
        self.speed = VoiceSpeed.to_enum(speed)
        self.pitch = VoicePitch.to_enum(pitch)
        self.language = NarrationLanguage.to_enum(language)

    @abstractmethod
    def validate(
        self,
        name: str,
        emotion: VoiceEmotion,
        speed: VoiceSpeed,
        pitch: VoicePitch,
        language: NarrationLanguage
    ):
        """
        Check if the parameters provided are valid or not
        and raise an Exception if not.

        This method can also process the attributes to make
        some modifications and return them to be stored
        once they have been modified.

        This method must be overwritten.
        """
        pass

    @staticmethod
    @abstractmethod
    def default():
        """
        Return an instance of your Narration Voice custom
        class with the default values for that type of 
        class.

        This method must be overwritten.
        """
        pass

