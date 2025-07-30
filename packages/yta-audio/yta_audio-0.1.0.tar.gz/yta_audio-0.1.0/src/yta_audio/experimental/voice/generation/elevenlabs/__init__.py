
"""
This module has been commented because the code is
very old and the 'elevenlabs' dependency is not a
real dependency yet as this module is experimental,
but the code was working when it was tested a long
time ago.
"""
# from yta_programming.env import Environment
# from yta_programming.output import Output
# from yta_constants.file import FileType
# from elevenlabs import generate, save, set_api_key
# from typing import Union


# API_KEY = Environment.get_current_project_env('ELEVENLABS_API_KEY')

# # TODO: Implement a method to get an existing voice attending to a 'type' (terror, inspirational, etc.)

# def generate_elevenlabs_narration(
#     text: str,
#     voice: str,
#     output_filename: Union[str, None] = None
# ):
#     """
#     Receives a 'text' and generates a single audio file with that 'text' narrated with
#     the provided 'voice', stored locally as 'output_filename'.

#     This method will split 'text' if too much longer to be able to narrate without issues
#     due to external platform working process. But will lastly generate a single audio file.
#     """
#     texts = [text]
#     # TODO: Set this limit according to voice type
#     if len(text) > 999999:
#         texts = []
#         # TODO: Handle splitting text into subgroups to narrate and then join
#         print('No subgrouping text yet')
#         texts = [text]

#     output_filename = Output.get_filename(output_filename, FileType.AUDIO)

#     if len(texts) == 1:
#         # Only one single file needed
#         download_elevenlabs_audio(texts[0], voice, output_filename)
#     else:
#         raise Exception('More than one text not implemented yet.')
#         for text in texts:
#             # TODO: Generate single file
#             print('Not implemented yet')

#         # TODO: Join all generated files in only one (maybe we need some silence in between?)
            
#     return output_filename

# def download_elevenlabs_audio(text = 'Esto es API', voice = 'Freya', output_file = 'generated_elevenlabs.wav'):
#     """
#     Generates a narration in elevenlabs and downloads it as output_file audio file.
#     """
#     set_api_key(API_KEY)
#     # TODO: Check if voice is valid
#     # TODO: Check which model fits that voice.
#     model = 'eleven_multilingual_v2'

#     if not output_file.endswith('.wav'):
#         output_file = output_file + '.wav'

#     # TODO: Try to be able to call it with stability parameter
#     audio = generate(
#         text = text,
#         voice = voice,
#         model = model
#     )

#     save(audio, output_file)