"""
This link could be interesting:
- https://github.com/DarinRowe/googletrans

You have a lot of information here:
- https://en.wikipedia.org/wiki/IETF_language_tag
- https://pypi.org/project/langcodes/
- https://gtts.readthedocs.io/en/latest/module.html#languages-gtts-lang
"""
from yta_audio.voice.consts import DEFAULT_VOICE
from yta_audio.voice.enums import NarrationLanguage, VoiceEmotion, VoiceSpeed, VoicePitch
from yta_audio.voice.generation.voice import NarrationVoice
from yta_constants.enum import YTAEnum as Enum
from yta_programming.output import Output
from yta_constants.file import FileType
from typing import Union
from gtts import gTTS


"""
This specific voice narration engine needs
specific values and a different parameter
handling.
"""

class GoogleNarrationLanguage(Enum):
    """
    The google narration languages accepted by their
    API
    """

    SPANISH = 'es'
    ENGLISH = 'en'

    @staticmethod
    def from_general_language(
        language: NarrationLanguage
    ) -> 'GoogleNarrationLanguage':
        """
        Turn a general 'language' instance into a Google
        narration language instance.
        """
        return {
            NarrationLanguage.DEFAULT: GoogleNarrationLanguage.SPANISH,
            NarrationLanguage.SPANISH: GoogleNarrationLanguage.SPANISH,
            NarrationLanguage.ENGLISH: GoogleNarrationLanguage.ENGLISH,
        }[NarrationLanguage.to_enum(language)]

"""
The options below are specified even if we
don't use them later when processing the 
voice narration. This is to keep the same
structure for any voice narration and to
simplify the way we offer the options in
an API that is able to make requests.

If the engine doesn't have one specific
option (I mean, you cannot handle the 
narration speed, for example) we will allow
the user choose 'normal' value and it will
be handled just by ignoring it, but the user
will be able to choose it.
"""

# 1. The voices we accept, as Enums
class GoogleTld(Enum):

    DEFAULT = DEFAULT_VOICE
    SPANISH_SPAIN = 'es'
    SPANISH_MEXICO = 'com.mx'
    SPANISH_US = 'us'
    # TODO: How can I get the list of Tlds?I need it

    @staticmethod
    def from_google_language(
        language: GoogleNarrationLanguage
    ) -> 'GoogleTld':
        """
        Turn the Google narration 'language' into the
        corresponding Google TLD.
        """
        return {
            GoogleNarrationLanguage.SPANISH: GoogleTld.SPANISH_SPAIN,
            # TODO: Change this
            GoogleNarrationLanguage.ENGLISH:  GoogleTld.SPANISH_US,
        }[GoogleNarrationLanguage.to_enum(language)]

# 2. The languages we accept
LANGUAGE_OPTIONS = [
    NarrationLanguage.SPANISH,
    # TODO: Unavailable until I detect some valid TLDs
    #NarrationLanguage.ENGLISH, 
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
    VoiceSpeed.SLOW,
]

# 5. The pitches we accept
PITCH_OPTIONS = [
    VoicePitch.DEFAULT,
    VoicePitch.NORMAL,
]


class GoogleNarrationVoice(NarrationVoice):
    """
    Voice instance to be used when narrating with
    Google engine.
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
            GoogleTld.SPANISH_SPAIN.value
            if GoogleTld.to_enum(self.name) == GoogleTld.DEFAULT else
            GoogleTld.to_enum(self.name).value
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
    ) -> bool:
        """
        Get the usable speed value from the one that
        has been set when instantiating the instance.
        """
        # This value is actually saying if we are using
        # the slow mode or not
        return {
            VoiceSpeed.SLOW: True,
            VoiceSpeed.DEFAULT: False,
            VoiceSpeed.NORMAL: False
        }[self.speed]

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
        return GoogleNarrationLanguage.from_general_language(self.language).value

    def validate_and_process(
        self,
        name: str,
        emotion: VoiceEmotion,
        speed: VoiceSpeed,
        pitch: VoicePitch,
        language: NarrationLanguage
    ):
        GoogleTld.to_enum(name)
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
        return GoogleNarrationVoice(
            name = GoogleTld.DEFAULT.value,
            emotion = VoiceEmotion.DEFAULT,
            speed = VoiceSpeed.DEFAULT,
            pitch = VoicePitch.DEFAULT,
            language = NarrationLanguage.DEFAULT
        )
        # TODO: This was in the previous version, remove when
        # confirmed that the above is working
        # return GoogleNarrationVoice('', '', 130, 1.0, NarrationLanguage.DEFAULT)
    
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
            GoogleTld.DEFAULT.value,
            GoogleTld.SPANISH_SPAIN.value,
            GoogleTld.SPANISH_MEXICO.value,
            GoogleTld.SPANISH_US.value
        ]
    }[language]


# All the remaining functionality we need to make it
# work properly
def narrate(
    text: str,
    voice: GoogleNarrationVoice = GoogleNarrationVoice.default(),
    output_filename: Union[str, None] = None
):
    """
    Creates an audio narration of the provided 'text' with the Google voice and stores it
    as 'output_filename'. This will use the provided 'language' language for the narration.
    """
    output_filename = Output.get_filename(output_filename, FileType.AUDIO)
    
    tld = GoogleTld.from_google_language(voice.processed_language).value

    gTTS(
        text = text,
        lang = voice.processed_language,
        tld = tld,
        slow = voice.processed_speed
    ).save(
        output_filename
    )

    return output_filename