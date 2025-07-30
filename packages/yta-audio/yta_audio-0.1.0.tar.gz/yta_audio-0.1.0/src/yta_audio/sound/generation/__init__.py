from yta_audio_base.silences import AudioSilence
from yta_audio.resources.drive_urls import TYPING_KEYBOARD_3_SECONDS_GOOGLE_DRIVE_DOWNLOAD_URL
from yta_google_drive_downloader.resource import Resource
from yta_temp import Temp
from yta_programming.output import Output
from yta_programming.decorators.requires_dependency import requires_dependency
from yta_constants.file import FileType
from typing import Union


class SoundGenerator:

    @requires_dependency('moviepy', 'yta_audio', 'moviepy')
    @staticmethod
    def create_typing_audio(
        output_filename: Union[str, None] = None
    ):
        """
        Creates a typing audioclip of 3.5 seconds that, if 
        'output_filename' is provided, is stored locally
        with that name.
        """
        from moviepy import AudioFileClip, concatenate_audioclips

        audio_filename = Resource(TYPING_KEYBOARD_3_SECONDS_GOOGLE_DRIVE_DOWNLOAD_URL, Temp.get_custom_wip_filename('sound_typing_keyboard_3s.mp3')).file
        audioclip = AudioFileClip(audio_filename)
        silence_audioclip = AudioSilence.create(0.5)

        audioclip = concatenate_audioclips([audioclip, silence_audioclip])

        if output_filename is not None:
            output_filename = Output.get_filename(output_filename, FileType.AUDIO)
            audioclip.write_audiofile(output_filename)

        # TODO: Maybe use FileReturn instead (?)
        return audioclip
