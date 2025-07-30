from yta_audio.voice.enums import NarrationLanguage, VoiceEmotion, VoiceSpeed, VoicePitch
from yta_audio.voice.consts import DEFAULT_VOICE
from yta_audio.voice.generation.voice import NarrationVoice
from yta_constants.enum import YTAEnum as Enum
from yta_programming.output import Output
from yta_constants.file import FileType
from typing import Union

import pyttsx3


"""
The options below are specified even if we
don't use them later when processing the 
voice narration. This is to keep the same
structure for any voice narration and to
simplify the way we offer the options in
an API that is able to make requests.
"""

# 1. The voices we accept, as Enums
class MicrosoftVoiceName(Enum):
    """
    Available voices. The value is what is used
    for the audio creation.
    """

    DEFAULT = DEFAULT_VOICE
    SPANISH_SPAIN = 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_ES-ES_HELENA_11.0'
    SPANISH_MEXICO = 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_ES-MX_SABINA_11.0'
    # TODO: There are more voices

# 2. The languages we accept
LANGUAGE_OPTIONS = [
    NarrationLanguage.DEFAULT,
    NarrationLanguage.SPANISH
]

# 3. The emotions we accept
EMOTION_OPTIONS = [
    VoiceEmotion.DEFAULT,
    VoiceEmotion.NORMAL,
]

# 4. The speeds we accept
SPEED_OPTIONS = [
    VoiceSpeed.DEFAULT,
    VoiceSpeed.NORMAL,
    VoiceSpeed.SLOW,
    VoiceSpeed.FAST
]

# 5. The pitches we accept
PITCH_OPTIONS = [
    VoicePitch.DEFAULT,
    VoicePitch.NORMAL,
]


class MicrosoftNarrationVoice(NarrationVoice):
    """
    Voice instance to be used when narrating with
    Microsoft engine.
    """

    @property
    def processed_name(
        self
    ) -> str:
        """
        Get the usable name value from the one that has
        been set when instantiating the instance.
        """
        # TODO: Maybe this DEFAULT value has to exist
        # for each language so it chooses one voice name
        # for that language
        return (
            MicrosoftVoiceName.SPANISH_SPAIN.value
            if MicrosoftVoiceName.to_enum(self.name) == MicrosoftVoiceName.DEFAULT else
            MicrosoftVoiceName.to_enum(self.name).value
        )

    @property
    def processed_emotion(
        self
    ) -> str:
        """
        Get the usable emotion value from the one that
        has been set when instantiating the instance.
        """
        # This narration is not able to handle any 
        # emotion (at least by now)
        return None
    
    @property
    def processed_speed(
        self
    ) -> int:
        """
        Get the usable speed value from the one that
        has been set when instantiating the instance.
        """
        # This value is actually the amount of words per
        # minute to be said during the speech
        speed = (
            VoiceSpeed.NORMAL
            if self.speed == VoiceSpeed.DEFAULT else
            self.speed
        )

        return {
            VoiceSpeed.SLOW: 160,
            VoiceSpeed.NORMAL: 200,
            VoiceSpeed.FAST: 240
        }[speed]

    @property
    def processed_pitch(
        self
    ) -> float:
        """
        Get the usable pitch value from the one that
        has been set when instantiating the instance.
        """
        # By now we are not handling the pitch with
        # this voice
        return None
    
    @property
    def processed_language(
        self
    ) -> str:
        """
        Get the usable language value from the one that
        has been set when instantiating the instance.
        """
        # By now we are not handling the language with
        # this voice
        return None

    def validate_and_process(
        self,
        name: str,
        emotion: VoiceEmotion,
        speed: VoiceSpeed,
        pitch: VoicePitch,
        language: NarrationLanguage
    ):
        MicrosoftVoiceName.to_enum(name)
        if VoiceEmotion.to_enum(emotion) not in EMOTION_OPTIONS:
            raise Exception(f'The provided {emotion} is not valid for this narration voice.')
        if VoiceSpeed.to_enum(speed) not in SPEED_OPTIONS:
            raise Exception(f'The provided {speed} is not valid for this narration voice.')
        if VoicePitch.to_enum(pitch) not in PITCH_OPTIONS:
            raise Exception(f'The provided {pitch} is not valid for this narration voice.')
        if NarrationLanguage.to_enum(language) not in LANGUAGE_OPTIONS:
            raise Exception(f'The provided {language} is not valid for this narration voice.')
        
    @staticmethod
    def default():
        return MicrosoftNarrationVoice(
            name = MicrosoftVoiceName.DEFAULT.value,
            emotion = VoiceEmotion.DEFAULT,
            speed = VoiceSpeed.DEFAULT,
            pitch = VoicePitch.DEFAULT,
            language = NarrationLanguage.DEFAULT
        )

# The voices but for a specific language, to be able to
# choose one when this is requested from the outside
def get_narrator_names_by_language(
    language: NarrationLanguage
) -> list[str]:
    language = NarrationLanguage.to_enum(language)
    language = (
        NarrationLanguage.SPANISH
        if language is NarrationLanguage.DEFAULT else
        language
    )

    return {
        NarrationLanguage.SPANISH: [
            MicrosoftVoiceName.DEFAULT.value,
            MicrosoftVoiceName.SPANISH_SPAIN.value,
            MicrosoftVoiceName.SPANISH_MEXICO.value
        ]
    }[language]

# All the remaining functionality we need to make it
# work properly
def narrate(
    text: str,
    voice: MicrosoftNarrationVoice = MicrosoftNarrationVoice.default(),
    output_filename: Union[str, None] = None
):
    """
    Creates an audio narration of the provided 'text'
    and stores it as 'output_filename'.
    """
    output_filename = Output.get_filename(output_filename, FileType.AUDIO)
    
    engine = pyttsx3.init()
    engine.setProperty('voice', voice.processed_name)
    # Default speed is 200 (wpm)
    engine.setProperty('rate', voice.processed_speed)
    engine.save_to_file(text, output_filename)
    engine.runAndWait()

    return output_filename