"""
This voice engine is based in Coqui and I
have another voice engine which is Coqui,
but using other voice narrators.

TODO: Consider mixing both voice engines
and appending this voice narrator to the
Coqui system and keep only one of them.

-- Update 19/04/2025 --
I've found that they created a fork in
https://github.com/idiap/coqui-ai-TTS with
a new version that is maintained, and the 
'tts' was generating conflicts.
"""
from yta_audio.voice.consts import DEFAULT_VOICE
from yta_audio.voice.enums import NarrationLanguage, VoiceEmotion, VoiceSpeed, VoicePitch
from yta_audio.voice.generation.voice import NarrationVoice
from yta_constants.enum import YTAEnum as Enum
from yta_programming.output import Output
from yta_constants.file import FileType
from typing import Union
from TTS.api import TTS


"""
The options below are specified even if we
don't use them later when processing the 
voice narration. This is to keep the same
structure for any voice narration and to
simplify the way we offer the options in
an API that is able to make requests.
"""

# 1. The voices we accept, as Enums
class TortoiseVoiceName(Enum):
    """
    Available voices. The value is what is used
    for the audio creation.
    """

    DEFAULT = DEFAULT_VOICE
    SPANISH = 'es_002'
    MEXICAN = 'es_mx_002'
    # TODO: There a a lot of English US and more languages voices

# 2. The languages we accept
LANGUAGE_OPTIONS = [
    NarrationLanguage.SPANISH,
    NarrationLanguage.DEFAULT
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
]

# 5. The pitches we accept
PITCH_OPTIONS = [
    VoicePitch.DEFAULT,
    VoicePitch.NORMAL,
]

class TortoiseNarrationVoice(NarrationVoice):
    """
    Voice instance to be used when narrating with
    Tortoise engine.
    """

    @property
    def processed_name(
        self
    ) -> str:
        """
        Get the usable name value from the one that has
        been set when instantiating the instance.
        """
        # TODO: We are not using voice names here
        return None

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
        # This is not used here
        return None

    @property
    def processed_pitch(
        self
    ) -> int:
        """
        Get the usable pitch value from the one that
        has been set when instantiating the instance.
        """
        # This is not used here
        return None
    
    @property
    def processed_language(
        self
    ) -> str:
        """
        Get the usable language value from the one that
        has been set when instantiating the instance.
        """
        language = (
            NarrationLanguage.SPANISH
            if self.language == NarrationLanguage.DEFAULT else
            self.language
        )

        return {
            NarrationLanguage.SPANISH: 'es'
        }[language]

    def validate_and_process(
        self,
        name: str,
        emotion: VoiceEmotion,
        speed: VoiceSpeed,
        pitch: VoicePitch,
        language: NarrationLanguage
    ):
        TortoiseVoiceName.to_enum(name)
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
        return TortoiseNarrationVoice(
            name = TortoiseVoiceName.DEFAULT.value,
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
            TortoiseVoiceName.DEFAULT.value,
        ]
    }[language]

# All the remaining functionality we need to make it
# work properly
def narrate(
    text: str,
    voice: TortoiseNarrationVoice = TortoiseNarrationVoice.default(),
    output_filename: Union[str, None] = None
):
    """
    @deprecated

    TODO: Remove this file and method if useless. Please, read below to check.
    This method should be removed and also the file as it is only one specific
    model in TTS narration library. It is not a different system. So please,
    remove it if it won't be used.
    """
    output_filename = Output.get_filename(output_filename, FileType.AUDIO)

    # TODO: Delete tortoise lib?
    # TODO: Delete en/multi-datase/tortoise-v2 model
    tts = TTS("tts_models/es/multi-dataset/tortoise-v2")

    # Check code here: https://docs.coqui.ai/en/latest/models/tortoise.html
    tts.tts_to_file(text = text, language = voice.processed_language, file_path = output_filename)

    return output_filename

    #reference_clips = [utils.audio.load_audio(p, 22050) for p in clips_paths]
    
    #pcm_audio = tts.tts(text)
    #pcm_audio = tts.tts_with_preset("your text here", voice_samples=reference_clips, preset='fast')
    
    #from tortoise.utils.audio import load_audio, load_voice