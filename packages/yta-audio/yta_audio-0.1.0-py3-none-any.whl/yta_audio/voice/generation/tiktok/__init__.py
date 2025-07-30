"""
This was extracted from here:
- https://gesserit.co/tiktok

And you have more projects here:
- Project to use Tiktok API and cookie (https://github.com/Steve0929/tiktok-tts)
- Pproject to use Tiktok API and session id (https://github.com/oscie57/tiktok-voice)
- Project that is install and play (I think) https://github.com/Giooorgiooo/TikTok-Voice-TTS/blob/main/tiktokvoice.py
"""
from yta_audio.voice.consts import DEFAULT_VOICE
from yta_audio.voice.enums import NarrationLanguage, VoiceEmotion, VoiceSpeed, VoicePitch
from yta_text.handler import TextHandler
from yta_audio.voice.generation.voice import NarrationVoice
from yta_file.handler import FileHandler
from yta_constants.enum import YTAEnum as Enum
from yta_programming.output import Output
from yta_constants.file import FileType
from typing import Union

import requests
import base64


"""
The options below are specified even if we
don't use them later when processing the 
voice narration. This is to keep the same
structure for any voice narration and to
simplify the way we offer the options in
an API that is able to make requests.
"""

# 1. The voices we accept, as Enums
class TiktokVoiceName(Enum):
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

class TiktokNarrationVoice(NarrationVoice):
    """
    Voice instance to be used when narrating with
    Tiktok engine.
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
            TiktokVoiceName.SPANISH.value
            if TiktokVoiceName.to_enum(self.name) == TiktokVoiceName.DEFAULT else
            TiktokVoiceName.to_enum(self.name).value
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
        # TODO: There is not language associated with this
        # narration voice engine. The language is set in
        # the voice name
        return None

    def validate_and_process(
        self,
        name: str,
        emotion: VoiceEmotion,
        speed: VoiceSpeed,
        pitch: VoicePitch,
        language: NarrationLanguage
    ):
        TiktokVoiceName.to_enum(name)
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
        return TiktokNarrationVoice(
            name = TiktokVoiceName.DEFAULT.value,
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
            TiktokVoiceName.DEFAULT.value,
            TiktokVoiceName.SPANISH.value,
            TiktokVoiceName.MEXICAN.value
        ]
    }[language]
    
# All the remaining functionality we need to make it
# work properly
def narrate_tiktok(
    text: str,
    voice: TiktokNarrationVoice = TiktokNarrationVoice.default(),
    output_filename: Union[str, None] = None
) -> str:
    """
    This is the tiktok voice based on a platform that generates it.
    This will make a narration with the tiktok voice. You can
    change the code to use the mexican voice.

    As this is based on an external platform, it could fail.

    This method returns the filename that has been written.
    """
    headers = {
        'accept': '*/*',
        'accept-language': 'es-ES,es;q=0.9',
        'content-type': 'text/plain;charset=UTF-8',
        'origin': 'https://gesserit.co',
        'referer': 'https://gesserit.co/tiktok',
        'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    }

    # Non-English characters are not accepted by Tiktok TTS generation, so:
    text = TextHandler.remove_non_ascii_characters(text)
    
    #data = f'{"text":"{text}","voice":"{voice.name}"}'
    data = '{"text":"' + text + '","voice":"' + voice.processed_name + '"}'

    base64_content = requests.post('https://gesserit.co/api/tiktok-tts', headers = headers, data = data).json()['base64']

    output_filename = Output.get_filename(output_filename, FileType.AUDIO)
    
    return FileHandler.write_binary(
        filename = output_filename,
        binary_data = base64.b64decode(base64_content)
    )
    