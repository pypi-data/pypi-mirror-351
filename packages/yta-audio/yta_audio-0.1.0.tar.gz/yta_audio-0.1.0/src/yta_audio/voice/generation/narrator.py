from yta_audio.voice.generation.voice import NarrationVoice
from yta_audio.voice.enums import NarrationLanguage, VoiceEmotion, VoiceSpeed, VoicePitch
from yta_audio.voice.generation.coqui import narrate as narrate_coqui, CoquiNarrationVoice, LANGUAGE_OPTIONS as COQUI_LANGUAGE_OPTIONS, get_narrator_names_by_language as get_coqui_narrator_names_by_language, EMOTION_OPTIONS as COQUI_EMOTION_OPTIONS, SPEED_OPTIONS as COQUI_SPEED_OPTIONS, PITCH_OPTIONS as COQUI_PITCH_OPTIONS, CoquiVoiceName
from yta_audio.voice.generation.google import narrate as narrate_google, GoogleNarrationVoice, LANGUAGE_OPTIONS as GOOGLE_LANGUAGE_OPTIONS, get_narrator_names_by_language as get_google_narrator_names_by_language, EMOTION_OPTIONS as GOOGLE_EMOTION_OPTIONS, SPEED_OPTIONS as GOOGLE_SPEED_OPTIONS, PITCH_OPTIONS as GOOGLE_PITCH_OPTIONS, GoogleTld
from yta_audio.voice.generation.microsoft import narrate as narrate_microsoft, MicrosoftNarrationVoice, LANGUAGE_OPTIONS as MICROSOFT_LANGUAGE_OPTIONS, get_narrator_names_by_language as get_microsoft_narrator_names_by_language, EMOTION_OPTIONS as MICROSOFT_EMOTION_OPTIONS, SPEED_OPTIONS as MICROSOFT_SPEED_OPTIONS, PITCH_OPTIONS as MICROSOFT_PITCH_OPTIONS, MicrosoftVoiceName
# from yta_audio.voice.generation.open_voice import narrate as narrate_open_voice, OpenVoiceNarrationVoice, LANGUAGE_OPTIONS as OPEN_VOICE_LANGUAGE_OPTIONS, get_narrator_names_by_language as get_open_voice_narrator_names_by_language, EMOTION_OPTIONS as OPEN_VOICE_EMOTION_OPTIONS, SPEED_OPTIONS as OPEN_VOICE_SPEED_OPTIONS, PITCH_OPTIONS as OPEN_VOICE_PITCH_OPTIONS, OpenVoiceVoiceName
from yta_audio.voice.generation.tetyys import narrate_tetyys, TetyysNarrationVoice, LANGUAGE_OPTIONS as TETYYS_LANGUAGE_OPTIONS, get_narrator_names_by_language as get_tetyys_narrator_names_by_language, EMOTION_OPTIONS as TETYYS_EMOTION_OPTIONS, SPEED_OPTIONS as TETYYS_SPEED_OPTIONS, PITCH_OPTIONS as TETYYS_PITCH_OPTIONS, TetyysVoiceName
from yta_audio.voice.generation.tiktok import narrate_tiktok, TiktokNarrationVoice, LANGUAGE_OPTIONS as TIKTOK_LANGUAGE_OPTIONS, get_narrator_names_by_language as get_tiktok_narrator_names_by_language, EMOTION_OPTIONS as TIKTOK_EMOTION_OPTIONS, SPEED_OPTIONS as TIKTOK_SPEED_OPTIONS, PITCH_OPTIONS as TIKTOK_PITCH_OPTIONS, TiktokVoiceName
from yta_audio.voice.generation.tortoise import narrate as narrate_tortoise, TortoiseNarrationVoice, LANGUAGE_OPTIONS as TORTOISE_LANGUAGE_OPTIONS, get_narrator_names_by_language as get_tortoise_narrator_names_by_language, EMOTION_OPTIONS as TORTOISE_EMOTION_OPTIONS, SPEED_OPTIONS as TORTOISE_SPEED_OPTIONS, PITCH_OPTIONS as TORTOISE_PITCH_OPTIONS, TortoiseVoiceName
from yta_audio.voice.generation.ttsmp3 import narrate_tts3, Ttsmp3NarrationVoice, LANGUAGE_OPTIONS as TTSMP3_LANGUAGE_OPTIONS, get_narrator_names_by_language as get_ttsmp3_narrator_names_by_language, EMOTION_OPTIONS as TTSMP3_EMOTION_OPTIONS, SPEED_OPTIONS as TTSMP3_SPEED_OPTIONS, PITCH_OPTIONS as TTSMP3_PITCH_OPTIONS, Ttsmp3VoiceName
from yta_validation.parameter import ParameterValidator
from yta_programming.output import Output
from yta_constants.file import FileType
from abc import ABC, abstractmethod
from typing import Union


class VoiceNarrator(ABC):
    """
    Class to simplify and encapsulate the voice
    narration functionality.
    """

    @staticmethod
    @abstractmethod
    def narrate(
        text: str,
        voice: NarrationVoice = NarrationVoice.default(),
        output_filename: Union[str, None] = None
    ):
        """
        Create a voice narration of the given 'text' and
        stores it locally in the 'output_filename'
        provided (or in a temporary file if not provided).
        """
        pass

    @staticmethod
    @abstractmethod
    def get_available_languages() -> list[NarrationLanguage]:
        """
        Get the list of the languages that are available
        to be used in the voice narration.

        This method must be overwritten.
        """
        pass

    @staticmethod
    @abstractmethod
    def get_available_narrator_names(
        language: NarrationLanguage
    ) -> list[str]:
        """
        Get the list of the narrator names that are
        available for the given 'language' to be used
        in the voice narration.

        This method must be overwritten.
        """
        pass

    @staticmethod
    @abstractmethod
    def get_available_emotions() -> list[VoiceEmotion]:
        """
        Get the list of the emotions that are 
        available to be used when narrating the
        text.

        This method must be overwritten.
        """
        pass

    @staticmethod
    @abstractmethod
    def get_available_speeds() -> list[VoiceSpeed]:
        """
        Get the list of the speeds that are 
        available to be used when narrating the
        text.

        This method must be overwritten.
        """
        pass

    @staticmethod
    @abstractmethod
    def get_available_pitches() -> list[VoicePitch]:
        """
        Get the list of the pitches that are 
        available to be used when narrating the
        text.

        This method must be overwritten.
        """
        pass

class CoquiVoiceNarrator(VoiceNarrator):

    @staticmethod
    def narrate(
        text: str,
        name: CoquiVoiceName = CoquiVoiceName.DEFAULT,
        emotion: VoiceEmotion = VoiceEmotion.DEFAULT,
        speed: VoiceSpeed = VoiceSpeed.DEFAULT,
        pitch: VoicePitch = VoicePitch.DEFAULT,
        language: NarrationLanguage = NarrationLanguage.DEFAULT,
        output_filename: Union[str, None] = None
    ):
        ParameterValidator.validate_mandatory_string('text', text, do_accept_empty = False)
        name = CoquiVoiceName.to_enum(name)
        
        output_filename = Output.get_filename(output_filename, FileType.AUDIO)

        voice = CoquiNarrationVoice(
            name = name.value,
            emotion = emotion,
            speed = speed,
            pitch = pitch,
            language = language
        )
        
        # TODO: Maybe return a FileReturn (?)
        return narrate_coqui(text, voice, output_filename = output_filename)
    
    @staticmethod
    def get_available_languages() -> list[NarrationLanguage]:
        return COQUI_LANGUAGE_OPTIONS
    
    @staticmethod
    def get_available_narrator_names(
        language: NarrationLanguage
    ) -> list[str]:
        language = NarrationLanguage.to_enum(language)

        return get_coqui_narrator_names_by_language(language)
    
    @staticmethod
    def get_available_emotions() -> list[VoiceEmotion]:
        return COQUI_EMOTION_OPTIONS
    
    @staticmethod
    def get_available_speeds() -> list[VoiceSpeed]:
        return COQUI_SPEED_OPTIONS
    
    @staticmethod
    def get_available_pitches() -> list[VoicePitch]:
        return COQUI_PITCH_OPTIONS
    
class GoogleVoiceNarrator(VoiceNarrator):

    @staticmethod
    def narrate(
        text: str,
        name: GoogleTld = GoogleTld.DEFAULT,
        emotion: VoiceEmotion = VoiceEmotion.DEFAULT,
        speed: VoiceSpeed = VoiceSpeed.DEFAULT,
        pitch: VoicePitch = VoicePitch.DEFAULT,
        language: NarrationLanguage = NarrationLanguage.DEFAULT,
        output_filename: Union[str, None] = None
    ):
        ParameterValidator.validate_mandatory_string('text', text, do_accept_empty = False)
        name = GoogleTld.to_enum(name)
        
        output_filename = Output.get_filename(output_filename, FileType.AUDIO)

        voice = GoogleNarrationVoice(
            name = name.value,
            emotion = emotion,
            speed = speed,
            pitch = pitch,
            language = language
        )
        
        # TODO: Maybe return a FileReturn (?)
        return narrate_google(text, voice, output_filename = output_filename)
    
    @staticmethod
    def get_available_languages() -> list[NarrationLanguage]:
        return GOOGLE_LANGUAGE_OPTIONS
    
    @staticmethod
    def get_available_narrator_names(
        language: NarrationLanguage
    ) -> list[str]:
        language = NarrationLanguage.to_enum(language)

        return get_google_narrator_names_by_language(language)
    
    @staticmethod
    def get_available_emotions() -> list[VoiceEmotion]:
        return GOOGLE_EMOTION_OPTIONS
    
    @staticmethod
    def get_available_speeds() -> list[VoiceSpeed]:
        return GOOGLE_SPEED_OPTIONS
    
    @staticmethod
    def get_available_pitches() -> list[VoicePitch]:
        return GOOGLE_PITCH_OPTIONS
    
class MicrosoftVoiceNarrator(VoiceNarrator):

    @staticmethod
    def narrate(
        text: str,
        name: MicrosoftVoiceName = MicrosoftVoiceName.DEFAULT,
        emotion: VoiceEmotion = VoiceEmotion.DEFAULT,
        speed: VoiceSpeed = VoiceSpeed.DEFAULT,
        pitch: VoicePitch = VoicePitch.DEFAULT,
        language: NarrationLanguage = NarrationLanguage.DEFAULT,
        output_filename: Union[str, None] = None
    ):
        ParameterValidator.validate_mandatory_string('text', text, do_accept_empty = False)
        name = MicrosoftVoiceName.to_enum(name)
        
        output_filename = Output.get_filename(output_filename, FileType.AUDIO)

        voice = MicrosoftNarrationVoice(
            name = name.value,
            emotion = emotion,
            speed = speed,
            pitch = pitch,
            language = language
        )
        
        # TODO: Maybe return a FileReturn (?)
        return narrate_microsoft(text, voice, output_filename = output_filename)
    
    @staticmethod
    def get_available_languages() -> list[NarrationLanguage]:
        return MICROSOFT_LANGUAGE_OPTIONS
    
    @staticmethod
    def get_available_narrator_names(
        language: NarrationLanguage
    ) -> list[str]:
        language = NarrationLanguage.to_enum(language)

        return get_microsoft_narrator_names_by_language(language)
    
    @staticmethod
    def get_available_emotions() -> list[VoiceEmotion]:
        return MICROSOFT_EMOTION_OPTIONS
    
    @staticmethod
    def get_available_speeds() -> list[VoiceSpeed]:
        return MICROSOFT_SPEED_OPTIONS
    
    @staticmethod
    def get_available_pitches() -> list[VoicePitch]:
        return MICROSOFT_PITCH_OPTIONS
    
# class OpenVoiceVoiceNarrator(VoiceNarrator):

#     @staticmethod
#     def narrate(
#         text: str,
#         name: OpenVoiceVoiceName = OpenVoiceVoiceName.DEFAULT,
#         emotion: VoiceEmotion = VoiceEmotion.DEFAULT,
#         speed: VoiceSpeed = VoiceSpeed.DEFAULT,
#         pitch: VoicePitch = VoicePitch.DEFAULT,
#         language: NarrationLanguage = NarrationLanguage.DEFAULT,
#         output_filename: Union[str, None] = None
#     ):
#         ParameterValidator.validate_mandatory_string('text', text, do_accept_empty = False)
#         name = OpenVoiceVoiceName.to_enum(name)

#         output_filename = Output.get_filename(output_filename, FileType.AUDIO)

#         voice = OpenVoiceNarrationVoice(
#             name = name.value,
#             emotion = emotion,
#             speed = speed,
#             pitch = pitch,
#             language = language
#         )
        
#         # TODO: Maybe return a FileReturn (?)
#         return narrate_open_voice(text, voice, output_filename = output_filename)
    
#     @staticmethod
#     def get_available_languages() -> list[NarrationLanguage]:
#         return OPEN_VOICE_LANGUAGE_OPTIONS
    
#     @staticmethod
#     def get_available_narrator_names(
#         language: NarrationLanguage
#     ) -> list[str]:
#         language = NarrationLanguage.to_enum(language)

#         return get_open_voice_narrator_names_by_language(language)
    
#     @staticmethod
#     def get_available_emotions() -> list[VoiceEmotion]:
#         return OPEN_VOICE_EMOTION_OPTIONS
    
#     @staticmethod
#     def get_available_speeds() -> list[VoiceSpeed]:
#         return OPEN_VOICE_SPEED_OPTIONS
    
#     @staticmethod
#     def get_available_pitches() -> list[VoicePitch]:
#         return OPEN_VOICE_PITCH_OPTIONS
    
class TetyysVoiceNarrator(VoiceNarrator):

    @staticmethod
    def narrate(
        text: str,
        name: TetyysVoiceName = TetyysVoiceName.DEFAULT,
        emotion: VoiceEmotion = VoiceEmotion.DEFAULT,
        speed: VoiceSpeed = VoiceSpeed.DEFAULT,
        pitch: VoicePitch = VoicePitch.DEFAULT,
        language: NarrationLanguage = NarrationLanguage.DEFAULT,
        output_filename: Union[str, None] = None
    ):
        ParameterValidator.validate_mandatory_string('text', text, do_accept_empty = False)
        name = TetyysVoiceName.to_enum(name)

        output_filename = Output.get_filename(output_filename, FileType.AUDIO)

        voice = TetyysNarrationVoice(
            name = name.value,
            emotion = emotion,
            speed = speed,
            pitch = pitch,
            language = language
        )
        
        # TODO: Maybe return a FileReturn (?)
        return narrate_tetyys(text, voice, output_filename = output_filename)
    
    @staticmethod
    def get_available_languages() -> list[NarrationLanguage]:
        return TETYYS_LANGUAGE_OPTIONS
    
    @staticmethod
    def get_available_narrator_names(
        language: NarrationLanguage
    ) -> list[str]:
        language = NarrationLanguage.to_enum(language)

        return get_tetyys_narrator_names_by_language(language)

    @staticmethod
    def get_available_emotions() -> list[VoiceEmotion]:
        return TETYYS_EMOTION_OPTIONS
    
    @staticmethod
    def get_available_speeds() -> list[VoiceSpeed]:
        return TETYYS_SPEED_OPTIONS
    
    @staticmethod
    def get_available_pitches() -> list[VoicePitch]:
        return TETYYS_PITCH_OPTIONS
    
class TiktokVoiceNarrator(VoiceNarrator):

    @staticmethod
    def narrate(
        text: str,
        name: TiktokVoiceName = TiktokVoiceName.DEFAULT,
        emotion: VoiceEmotion = VoiceEmotion.DEFAULT,
        speed: VoiceSpeed = VoiceSpeed.DEFAULT,
        pitch: VoicePitch = VoicePitch.DEFAULT,
        language: NarrationLanguage = NarrationLanguage.DEFAULT,
        output_filename: Union[str, None] = None
    ):
        ParameterValidator.validate_mandatory_string('text', text, do_accept_empty = False)
        name = TiktokVoiceName.to_enum(name)
        
        output_filename = Output.get_filename(output_filename, FileType.AUDIO)

        voice = TiktokNarrationVoice(
            name = name.value,
            emotion = emotion,
            speed = speed,
            pitch = pitch,
            language = language
        )
        
        # TODO: Maybe return a FileReturn (?)
        return narrate_tiktok(text, voice, output_filename = output_filename)
    
    @staticmethod
    def get_available_languages() -> list[NarrationLanguage]:
        return TIKTOK_LANGUAGE_OPTIONS

    @staticmethod
    def get_available_narrator_names(
        language: NarrationLanguage
    ) -> list[str]:
        language = NarrationLanguage.to_enum(language)

        return get_tiktok_narrator_names_by_language(language)
    
    @staticmethod
    def get_available_emotions() -> list[VoiceEmotion]:
        return TIKTOK_EMOTION_OPTIONS
    
    @staticmethod
    def get_available_speeds() -> list[VoiceSpeed]:
        return TIKTOK_SPEED_OPTIONS
    
    @staticmethod
    def get_available_pitches() -> list[VoicePitch]:
        return TIKTOK_PITCH_OPTIONS
    
class TortoiseVoiceNarrator(VoiceNarrator):

    @staticmethod
    def narrate(
        text: str,
        name: TortoiseVoiceName = TortoiseVoiceName.DEFAULT,
        emotion: VoiceEmotion = VoiceEmotion.DEFAULT,
        speed: VoiceSpeed = VoiceSpeed.DEFAULT,
        pitch: VoicePitch = VoicePitch.DEFAULT,
        language: NarrationLanguage = NarrationLanguage.DEFAULT,
        output_filename: Union[str, None] = None
    ):
        ParameterValidator.validate_mandatory_string('text', text, do_accept_empty = False)
        name = TortoiseVoiceName.to_enum(name)
        
        output_filename = Output.get_filename(output_filename, FileType.AUDIO)

        voice = TortoiseNarrationVoice(
            name = name.value,
            emotion = emotion,
            speed = speed,
            pitch = pitch,
            language = language
        )
        
        # TODO: Maybe return a FileReturn (?)
        return narrate_tortoise(text, voice, output_filename = output_filename)
    
    @staticmethod
    def get_available_languages() -> list[NarrationLanguage]:
        return TORTOISE_LANGUAGE_OPTIONS
    
    @staticmethod
    def get_available_narrator_names(
        language: NarrationLanguage
    ) -> list[str]:
        language = NarrationLanguage.to_enum(language)

        return get_tortoise_narrator_names_by_language(language)
    
    @staticmethod
    def get_available_emotions() -> list[VoiceEmotion]:
        return TORTOISE_EMOTION_OPTIONS
    
    @staticmethod
    def get_available_speeds() -> list[VoiceSpeed]:
        return TORTOISE_SPEED_OPTIONS
    
    @staticmethod
    def get_available_pitches() -> list[VoicePitch]:
        return TORTOISE_PITCH_OPTIONS
    
class Ttsmp3VoiceNarrator(VoiceNarrator):

    @staticmethod
    def narrate(
        text: str,
        name: Ttsmp3VoiceName = Ttsmp3VoiceName.DEFAULT,
        emotion: VoiceEmotion = VoiceEmotion.DEFAULT,
        speed: VoiceSpeed = VoiceSpeed.DEFAULT,
        pitch: VoicePitch = VoicePitch.DEFAULT,
        language: NarrationLanguage = NarrationLanguage.DEFAULT,
        output_filename: Union[str, None] = None
    ):
        ParameterValidator.validate_mandatory_string('text', text, do_accept_empty = False)
        name = Ttsmp3VoiceName.to_enum(name)
        
        output_filename = Output.get_filename(output_filename, FileType.AUDIO)

        voice = Ttsmp3NarrationVoice(
            name = name.value,
            emotion = emotion,
            speed = speed,
            pitch = pitch,
            language = language
        )
        
        # TODO: Maybe return a FileReturn (?)
        return narrate_tts3(text, voice, output_filename = output_filename)
    
    @staticmethod
    def get_available_languages() -> list[NarrationLanguage]:
        return TTSMP3_LANGUAGE_OPTIONS

    @staticmethod
    def get_available_narrator_names(
        language: NarrationLanguage
    ) -> list[str]:
        language = NarrationLanguage.to_enum(language)

        return get_ttsmp3_narrator_names_by_language(language)
    
    @staticmethod
    def get_available_emotions() -> list[VoiceEmotion]:
        return TTSMP3_EMOTION_OPTIONS
    
    @staticmethod
    def get_available_speeds() -> list[VoiceSpeed]:
        return TTSMP3_SPEED_OPTIONS
    
    @staticmethod
    def get_available_pitches() -> list[VoicePitch]:
        return TTSMP3_PITCH_OPTIONS
    
class DefaultVoiceNarrator(VoiceNarrator):
    """
    The voice narrator that would be used by
    default when no specific narrator is requested.
    """

    @staticmethod
    def narrate(
        text: str,
        output_filename: Union[str, None] = None
    ):
        return GoogleVoiceNarrator.narrate(
            text = text,
            output_filename = output_filename
        )
    
    @staticmethod
    def get_available_languages() -> list[NarrationLanguage]:
        return GoogleVoiceNarrator.get_available_languages()

    @staticmethod
    def get_available_narrator_names(
        language: NarrationLanguage
    ) -> list[str]:
        return GoogleVoiceNarrator.get_available_narrator_names(language)
    
    @staticmethod
    def get_available_emotions() -> list[VoiceEmotion]:
        return GoogleVoiceNarrator.get_available_emotions()
    
    @staticmethod
    def get_available_speeds() -> list[VoiceSpeed]:
        return GoogleVoiceNarrator.get_available_speeds()
    
    @staticmethod
    def get_available_pitches() -> list[VoicePitch]:
        return GoogleVoiceNarrator.get_available_pitches()
    