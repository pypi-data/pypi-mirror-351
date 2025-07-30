"""
This engine has been extracted from here:
- https://ttsmp3.com/

This voice engine has just a limit of
3.000 characters of input when generating
with normal voices, and 1.000 daily
characters when using AI. AI is disabled
by now as the limit makes it not
interesting for our purpose.
"""
from yta_audio.voice.consts import DEFAULT_VOICE
from yta_audio.voice.enums import NarrationLanguage, VoiceEmotion, VoiceSpeed, VoicePitch
from yta_audio.voice.generation.voice import NarrationVoice
from yta_file_downloader import Downloader
from yta_programming.output import Output
from yta_constants.file import FileType
from yta_constants.enum import YTAEnum as Enum
from typing import Union

import requests


"""
The options below are specified even if we
don't use them later when processing the 
voice narration. This is to keep the same
structure for any voice narration and to
simplify the way we offer the options in
an API that is able to make requests.
"""

# 1. The voices we accept, as Enums
class Ttsmp3VoiceName(Enum):
    # Normal voices below:
    DEFAULT = DEFAULT_VOICE
    LUPE = 'Lupe' # US Spanish
    PENELOPE = 'Penelope' # US Spanish
    MIGUEL = 'Miguel' # US Spanish
    # TODO: There are more voices for the different
    # languages, so jus copy the names here and you
    # will be able to use them
    # AI voices below:
    # ALLOY = 'alloy' # female
    # ECHO = 'echo' # male
    # FABLE = 'fable' # male
    # ONYX = 'onyx' # male (deeper voice)
    # NOVA = 'nova' # female (soft)
    # SHIMMER = 'shimmer' # female

# 2. The languages we accept
LANGUAGE_OPTIONS = [
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

class Ttsmp3NarrationVoice(NarrationVoice):
    """
    Voice instance to be used when narrating with
    Ttsmp3 engine.
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
            Ttsmp3VoiceName.MIGUEL.value
            if Ttsmp3VoiceName.to_enum(self.name) == Ttsmp3VoiceName.DEFAULT else
            Ttsmp3VoiceName.to_enum(self.name).value
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
        # This engine has the language set in the voice
        # names so you should select a voice name that
        # is specific of the language you need
        return None

    def validate_and_process(
        self,
        name: str,
        emotion: VoiceEmotion,
        speed: VoiceSpeed,
        pitch: VoicePitch,
        language: NarrationLanguage
    ):
        Ttsmp3VoiceName.to_enum(name)
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
        return Ttsmp3NarrationVoice(
            name = Ttsmp3VoiceName.DEFAULT.value,
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
            Ttsmp3VoiceName.DEFAULT.value,
            Ttsmp3VoiceName.LUPE.value,
            Ttsmp3VoiceName.MIGUEL.value,
            Ttsmp3VoiceName.PENELOPE.value
        ]
    }[language]

# All the remaining functionality we need to make it
# work properly
# TODO: Check this because I don't know if this webpage is using the tts (coqui)
# library as the generator engine. If that, I have this engine in 'coqui.py' file
# so I don't need this (that is not stable because is based in http requests)
def narrate_tts3(
    text: str,
    voice: Ttsmp3NarrationVoice = Ttsmp3NarrationVoice.default(),
    output_filename: Union[str, None] = None
) -> str:
    """
    This makes a narration based on an external platform. You
    can change some voice configuration in code to make the
    voice different.

    Aparrently not limited. Check, because it has time breaks 
    and that stuff to enhance the narration.
    """
    # From here: https://ttsmp3.com/
    headers = {
        'accept': '*/*',
        'accept-language': 'es-ES,es;q=0.9',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://ttsmp3.com',
        'referer': 'https://ttsmp3.com/',
        'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    }

    data = {
        'msg': text,
        'lang': voice.processed_name,
        'source': 'ttsmp3',
    }

    """
    There is an AI voices version but it has a
    daily limit of only 1.000 characters so it
    is not interesting, that is why I leave the
    code but commented.

    The way to request AI voice narrations is
    the same, but using the AI url and the AI
    voices names instead of the normal ones.
    """
    # AI_VERSION_HEADERS = {
    #     'accept': '*/*',
    #     'accept-language': 'es-ES,es;q=0.9',
    #     'content-type': 'application/x-www-form-urlencoded',
    #     'origin': 'https://ttsmp3.com',
    #     'priority': 'u=1, i',
    #     'referer': 'https://ttsmp3.com/ai',
    #     'sec-ch-ua': '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
    #     'sec-ch-ua-mobile': '?0',
    #     'sec-ch-ua-platform': '"Windows"',
    #     'sec-fetch-dest': 'empty',
    #     'sec-fetch-mode': 'cors',
    #     'sec-fetch-site': 'same-origin',
    #     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
    # }
    # AI_VERSION_URL = 'https:ttsmp3.com/makemp3_ai.php'

    response = requests.post('https://ttsmp3.com/makemp3_new.php', headers = headers, data = data)
    response = response.json()
    url = response['URL']

    output_filename = Output.get_filename(output_filename, FileType.AUDIO)

    # This is one example of a valid url we receive
    # as response:
    # https://ttsmp3.com/created_mp3/8b38a5f2d4664e98c9757eb6db93b914.mp3
    return Downloader.download_audio(url, output_filename).filename