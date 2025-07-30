"""
This module has been comented because the 'pedalboard'
library is not being installed properly with poetry,
but the code was working before so I want to keep it.
"""
# from yta_audio.converter import AudioConverter
# from yta_file.filename.handler import FilenameHandler
# from yta_file.handler import FileHandler
# from yta_temp import Temp
# from yta_programming.output import Output
# from yta_constants.file import FileType
# from math import trunc
# # TODO: This 'pedalboard' library is failing when being
# # installed so maybe optional (?)
# from pedalboard import Pedalboard, Reverb
# from typing import Union

# import numpy as np
# import soundfile as sf


# def slow_and_reverb_audio_file(
#     audio_filename: str,
#     output_filename: Union[str, None] = None,
#     room_size: float = 0.75,
#     damping: float = 0.5,
#     wet_level: float = 0.08,
#     dry_level: float = 0.2,
#     delay: float = 2,
#     slow_factor: float = 0.08
# ):
#     """
#     Apply 'slow and reverb' effect in the provided
#     'audio_filename' and stores it locally as the
#     given 'output_filename', that is returned by
#     this method.
#     """
#     # Extracted from here: https://github.com/samarthshrivas/LoFi-Converter-GUI
#     # But there is no only one: https://github.com/topics/slowedandreverbed
#     if not audio_filename:
#         return None
    
#     # TODO: This is not parsing the content actually
#     if not FileHandler.is_file(audio_filename):
#         return None

#     if FilenameHandler.get_extension(audio_filename) != 'wav':
#         # TODO: Handle other formats, by now I think it is .mp3 only
#         tmp_filename = Temp.get_filename('transformed_audio.wav')
#         AudioConverter.to_wav(audio_filename, tmp_filename)
#         audio_filename = tmp_filename

#     audio, sample_rate = sf.read(audio_filename)
#     sample_rate -= trunc(sample_rate * slow_factor)

#     # Adding reverb effect
#     reverved_board = Pedalboard([
#         Reverb(
#             # TODO: I need to learn more about these parameters
#             room_size = room_size,
#             damping = damping,
#             wet_level = wet_level,
#             dry_level = dry_level
#         )
#     ])

#     # Adding other surrounding effects
#     audio_with_effects = reverved_board(audio, sample_rate)
#     channel_1 = audio_with_effects[:, 0]
#     channel_2 = audio_with_effects[:, 1]
#     shift_length = delay * 1000
#     shifted_channel_1 = np.concatenate((np.zeros(shift_length), channel_1[:-shift_length]))
#     combined_signal = np.hstack((shifted_channel_1.reshape(-1, 1), channel_2.reshape(-1, 1)))

#     # TODO: Maybe force .wav (?)
#     output_filename = Output.get_filename(output_filename, FileType.AUDIO)

#     # Write the slowed and reverved output file
#     sf.write(output_filename, combined_signal, sample_rate)

#     # TODO: Maybe use FileReturn instead (?)
#     return output_filename