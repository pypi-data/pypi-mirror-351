"""
For anything else you need, check this:
- https://www.tetyys.com/SAPI4/

Each voice has an specific pitch and speed
so please, pay attention to it. Here are
some examples of this:
'Male Whisper' p: 113, s: 140
'Female Whisper' p: 169, s: 140
'Mary' p: 169, s: 140
"""
from yta_audio.voice.consts import DEFAULT_VOICE
from yta_audio.voice.enums import NarrationLanguage, VoiceEmotion, VoiceSpeed, VoicePitch
from yta_audio.voice.generation.voice import NarrationVoice
from yta_file.handler import FileHandler
from yta_constants.enum import YTAEnum as Enum
from yta_programming.output import Output
from yta_constants.file import FileType
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
class TetyysVoiceName(Enum):
    """
    Available voices. The value is what is used
    for the audio creation.
    """

    DEFAULT = DEFAULT_VOICE
    SAM = 'Sam'
    MALE_WHISPER = 'Male Whisper'
    FEMALE_WHISPER = 'Female Whisper'
    MARY = 'Mary'
    MARY_IN_SPACE = 'Mary in Space'
    MIKE_IN_SPACE = 'Mike in Space'
    ROBOSOFT_ONE = 'RobosoftOne'
    # TODO: There are more voices

# 2. The languages we accept
LANGUAGE_OPTIONS = [
    NarrationLanguage.ENGLISH,
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


class TetyysNarrationVoice(NarrationVoice):
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
            TetyysVoiceName.SAM.value
            if TetyysVoiceName.to_enum(self.name) == TetyysVoiceName.DEFAULT else
            TetyysVoiceName.to_enum(self.name).value
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
        # By now all the voices I'm using have the same
        # speed value so I'm just returning it
        return 140

    @property
    def processed_pitch(
        self
    ) -> int:
        """
        Get the usable pitch value from the one that
        has been set when instantiating the instance.
        """
        return {
            TetyysVoiceName.MALE_WHISPER: 113,
            TetyysVoiceName.FEMALE_WHISPER: 169,
            TetyysVoiceName.MARY: 169,
            TetyysVoiceName.MARY_IN_SPACE: 169,
            TetyysVoiceName.MIKE_IN_SPACE: 113,
            TetyysVoiceName.SAM: 100
        }[TetyysVoiceName.to_enum(self.processed_name)]
    
    @property
    def processed_language(
        self
    ) -> str:
        """
        Get the usable language value from the one that
        has been set when instantiating the instance.
        """
        # TODO: There is not language associated with this
        # narration voice engine
        return None

    def validate_and_process(
        self,
        name: str,
        emotion: VoiceEmotion,
        speed: VoiceSpeed,
        pitch: VoicePitch,
        language: NarrationLanguage
    ):
        TetyysVoiceName.to_enum(name)
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
        return TetyysNarrationVoice(
            name = TetyysVoiceName.DEFAULT.value,
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
        NarrationLanguage.ENGLISH
        if language is NarrationLanguage.DEFAULT else
        language
    )

    return {
        NarrationLanguage.ENGLISH: [
            TetyysVoiceName.DEFAULT.value,
            TetyysVoiceName.SAM.value,
            TetyysVoiceName.MALE_WHISPER.value,
            TetyysVoiceName.FEMALE_WHISPER.value,
            TetyysVoiceName.MARY.value,
            TetyysVoiceName.MARY_IN_SPACE.value,
            TetyysVoiceName.MIKE_IN_SPACE.value,
        ]
    }[language]

# All the remaining functionality we need to make it
# work properly
def narrate_tetyys(
    text: str,
    voice: TetyysNarrationVoice = TetyysNarrationVoice.default(),
    output_filename: Union[str, None] = None
) -> str:
    """
    This method creates an audio voice narration of the provided
    'text' read with tthe tetyys system voice (Microsoft Speech
    API 4.0 from 1998) and stores it as 'output_filename'. It is 
    only available for ENGLISH speaking.

    You can change some voice parameters in code to make it a
    different voice.

    This method is requesting an external (but apparently stable
    website).

    This method returns the filename that has been written.
    """
    headers = {
        'accept': '*/*',
        'accept-language': 'es-ES,es;q=0.9',
        'priority': 'u=1, i',
        'referer': 'https://www.tetyys.com/SAPI4/',
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    }

    params = {
        'text': text,
        # Inspect options 'value' from https://www.tetyys.com/SAPI4/ but
        # each voice has a pre-set 'pitch' and 'speed' 
        'voice': voice.processed_name, 
        'pitch': str(voice.processed_pitch),
        'speed': str(voice.processed_speed)
    }

    """
    Some VOICE options:
    'Male Whisper' 113, 140
    'Female Whisper' 169, 140
    'Mary' 169, 140
    'Mary in Space'|'Mary in Hall'|'Mary in Stadium'|Mary (for Telephone) 169, 140
    'Mike in Space'|... 113, 140
    'RobosoftOne'|'RobosoftTwo'
    'Sam' 100, 140
    """

    output_filename = Output.get_filename(output_filename, FileType.AUDIO)

    response = requests.get('https://www.tetyys.com/SAPI4/SAPI4', params = params, headers = headers)

    return FileHandler.write_binary(output_filename, response.content)