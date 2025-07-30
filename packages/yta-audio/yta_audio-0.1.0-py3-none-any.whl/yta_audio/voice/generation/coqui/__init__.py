"""
You can see anything you need here:
- https://docs.coqui.ai/en/latest/

As this is the first voice generator engine,
I will explain some things here that are
important for all the voice narrator engines
that we are creating.

We have options, and we will have all the 
array options fulfilled with, at least, a
NORMAL and a DEFAULT options. This, even if
the voice narrator engine doesn't use those
options, will be handled. Then, when 
generating the voice narration, it will be
ignored by our system.

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
class CoquiVoiceName(Enum):
    """
    Available voices. The value is what is used
    for the audio creation.
    """

    # tts_es_fastpitch_multispeaker.nemo
    # These below are the 2 Spanish models that exist
    DEFAULT = DEFAULT_VOICE
    SPANISH_MODEL_A = 'tts_models/es/mai/tacotron2-DDC'
    SPANISH_MODEL_B = 'tts_models/es/css10/vits'
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
]

# 5. The pitches we accept
PITCH_OPTIONS = [
    VoicePitch.DEFAULT,
    VoicePitch.NORMAL,
]

class CoquiNarrationVoice(NarrationVoice):
    """
    Voice instance to be used when narrating with
    Coqui engine.
    """

    @property
    def processed_name(
        self
    ) -> str:
        """
        Get the usable name value from the one that has
        been set when instantiating the instance.
        """
        return (
            CoquiVoiceName.SPANISH_MODEL_A.value
            if CoquiVoiceName.to_enum(self.name) == CoquiVoiceName.DEFAULT else
            CoquiVoiceName.to_enum(self.name).value
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
    ) -> float:
        """
        Get the usable speed value from the one that
        has been set when instantiating the instance.
        """
        # By now we are not handling the speed with
        # this voice
        return 1.0

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
        return self.language.value

    def validate(
        self,
        name: str,
        emotion: VoiceEmotion,
        speed: VoiceSpeed,
        pitch: VoicePitch,
        language: NarrationLanguage
    ):
        CoquiVoiceName.to_enum(name)
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
        return CoquiNarrationVoice(
            name = CoquiVoiceName.DEFAULT.value, 
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
    """
    Get the voices that are available for the
    given 'language'.
    """
    language = NarrationLanguage.to_enum(language)
    language = (
        NarrationLanguage.SPANISH
        if language is NarrationLanguage.DEFAULT else
        language
    )

    return {
        NarrationLanguage.SPANISH: [
            CoquiVoiceName.DEFAULT.value,
            CoquiVoiceName.SPANISH_MODEL_A.value,
            CoquiVoiceName.SPANISH_MODEL_B.value
        ]
    }[language]


# All the remaining functionality we need to make it
# work properly
def narrate(
    text: str,
    voice: CoquiNarrationVoice = CoquiNarrationVoice.default(),
    output_filename: Union[str, None] = None
) -> str:
    """
    Generates a narration audio file with the provided 'text' that
    will be stored as 'output_filename' file.

    This method uses a Spanish model so 'text' must be in Spanish.

    This method will take some time to generate the narration.
    """
    output_filename = Output.get_filename(output_filename, FileType.AUDIO)

    TTS(
        model_name = voice.processed_name
    ).tts_to_file(
        # TODO: Implement 'emotion', 'speed', etc. when known
        # how they work, the accepted values, etc. By now I'm
        # using the properties but with the default values
        text = text,
        speaker = None,
        language = None,
        emotion = voice.processed_emotion,
        speed = voice.processed_speed,
        file_path = output_filename
    )
    
    # TODO: This was in the previous version, remove when the
    # above is working.
    # tts = TTS(model_name = voice.name)
    # # There is 'language', 'emotion', 'speed'...
    # tts.tts_to_file(text = text, file_path = output_filename)

    return output_filename

def narrate_imitating_voice(
    text: str,
    input_filename: str,
    output_filename: Union[str, None] = None
):
    """
    Narrates the provided 'text' by imitating the provided 'input_filename'
    audio file (that must be a voice narrating something) and saves the 
    narration as 'output_filename'.

    The 'input_filename' could be an array of audio filenames.

    Language is set 'es' in code by default.

    This method will take time as it will recreate the voice parameters with
    which the narration will be created after that.

    ANNOTATIONS: This method is only copying the way the narration voice 
    talks, but not the own voice. This is not working as expected, as we are
    not cloning voices, we are just imitating the tone. We need another way
    to actually clone the voice as Elevenlabs do.
    """
    # TODO: This is not validating if audio file...
    if not input_filename:
        raise Exception('No "input_filename" provided.')
    
    output_filename = Output.get_filename(output_filename, FileType.AUDIO)

    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
    # This below will use the latest XTTS_v2 (needs to download the model)
    #tts = TTS('xtts')

    # TODO: Implement a way of identifying and storing the voices we create to
    # be able to use again them without recreating them twice.

    # input_filename can be an array of wav files
    # generate speech by cloning a voice using default settings
    tts.tts_to_file(text = text, file_path = output_filename, speaker_wav = input_filename, language = 'es')

    return output_filename