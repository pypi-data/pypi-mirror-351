# from yta_audio.voice.consts import DEFAULT_VOICE
# from yta_audio.voice.enums import NarrationLanguage, VoiceEmotion, VoiceSpeed, VoicePitch
# from yta_audio.voice.generation.voice import NarrationVoice
# from yta_programming.path import DevPathHandler
# from yta_constants.enum import YTAEnum as Enum
# from yta_programming.output import Output
# from yta_constants.file import FileType
# from openvoice import se_extractor
# from openvoice.api import ToneColorConverter
# from melo.api import TTS
# from pathlib import Path
# from typing import Union

# import os
# import torch


# """
# The options below are specified even if we
# don't use them later when processing the 
# voice narration. This is to keep the same
# structure for any voice narration and to
# simplify the way we offer the options in
# an API that is able to make requests.
# """

# # 1. The voices we accept, as Enums
# class OpenVoiceVoiceName(Enum):
#     """
#     Available voices. The value is what is used
#     for the audio creation.
#     """

#     DEFAULT = DEFAULT_VOICE

# # 2. The languages we accept
# LANGUAGE_OPTIONS = [
#     NarrationLanguage.SPANISH,
#     NarrationLanguage.DEFAULT
# ]

# # 3. The emotions we accept
# EMOTION_OPTIONS = [
#     VoiceEmotion.DEFAULT,
#     VoiceEmotion.NORMAL,
# ]

# # 4. The speeds we accept
# SPEED_OPTIONS = [
#     VoiceSpeed.DEFAULT,
#     VoiceSpeed.NORMAL,
# ]

# # 5. The pitches we accept
# PITCH_OPTIONS = [
#     VoicePitch.DEFAULT,
#     VoicePitch.NORMAL,
# ]

# class OpenVoiceNarrationVoice(NarrationVoice):
#     """
#     Voice instance to be used when narrating with
#     OpenVoice engine.
#     """

#     @property
#     def processed_name(
#         self
#     ) -> str:
#         """
#         Get the usable name value from the one that has
#         been set when instantiating the instance.
#         """
#         # TODO: Learn how to handle speaker ids please
#         # We are not able to handle voice names until we
#         # discover how the speakers ids work
#         return None

#     @property
#     def processed_emotion(
#         self
#     ) -> str:
#         """
#         Get the usable emotion value from the one that
#         has been set when instantiating the instance.
#         """
#         # This narration is not able to handle any 
#         # emotion (at least by now)
#         return None
    
#     @property
#     def processed_speed(
#         self
#     ) -> float:
#         """
#         Get the usable speed value from the one that
#         has been set when instantiating the instance.
#         """
#         # This value is used internally with numpy to
#         # concatenate audios, but results may vary
#         # according to the language, so this values
#         # are very experimental
#         speed = (
#             VoiceSpeed.NORMAL
#             if self.speed == VoiceSpeed.DEFAULT else
#             self.speed
#         )

#         return {
#             VoiceSpeed.SLOW: 0.8,
#             VoiceSpeed.NORMAL: 1.0,
#             VoiceSpeed.FAST: 1.2
#         }[speed]

#     @property
#     def processed_pitch(
#         self
#     ) -> float:
#         """
#         Get the usable pitch value from the one that
#         has been set when instantiating the instance.
#         """
#         # By now we are not handling the pitch with
#         # this voice
#         return None
    
#     @property
#     def processed_language(
#         self
#     ) -> str:
#         """
#         Get the usable language value from the one that
#         has been set when instantiating the instance.
#         """
#         # TODO: I don't know which values are actually
#         # accepted by this voice narrator
#         language = (
#             NarrationLanguage.SPANISH
#             if self.language == NarrationLanguage.DEFAULT else
#             self.language
#         )

#         return {
#             NarrationLanguage.SPANISH: 'ES'
#         }[language]

#     def validate_and_process(
#         self,
#         name: str,
#         emotion: VoiceEmotion,
#         speed: VoiceSpeed,
#         pitch: VoicePitch,
#         language: NarrationLanguage
#     ):
#         OpenVoiceVoiceName.to_enum(name)
#         if VoiceEmotion.to_enum(emotion) not in EMOTION_OPTIONS:
#             raise Exception(f'The provided {emotion} is not valid for this narration voice.')
#         if VoiceSpeed.to_enum(speed) not in SPEED_OPTIONS:
#             raise Exception(f'The provided {speed} is not valid for this narration voice.')
#         if VoicePitch.to_enum(pitch) not in PITCH_OPTIONS:
#             raise Exception(f'The provided {pitch} is not valid for this narration voice.')
#         if NarrationLanguage.to_enum(language) not in LANGUAGE_OPTIONS:
#             raise Exception(f'The provided {language} is not valid for this narration voice.')
        
#     @staticmethod
#     def default():
#         return OpenVoiceNarrationVoice(
#             name = OpenVoiceVoiceName.DEFAULT.value,
#             emotion = VoiceEmotion.DEFAULT,
#             speed = VoiceSpeed.DEFAULT,
#             pitch = VoicePitch.DEFAULT,
#             language = NarrationLanguage.DEFAULT
#         )

# # The voices but for a specific language, to be able to
# # choose one when this is requested from the outside
# def get_narrator_names_by_language(
#     language: NarrationLanguage
# ) -> list[str]:
#     language = NarrationLanguage.to_enum(language)
#     language = (
#         NarrationLanguage.SPANISH
#         if language is NarrationLanguage.DEFAULT else
#         language
#     )

#     return {
#         NarrationLanguage.SPANISH: [
#             DEFAULT_VOICE,
#         ]
#     }[language]

# # All the remaining functionality we need to make it
# # work properly
# def narrate(
#     text: str,
#     voice: OpenVoiceNarrationVoice = OpenVoiceNarrationVoice.default(),
#     output_filename: Union[str, None] = None
# ):
#     """
#     Narrates the provided 'text' at the provided 'speed' with the MeloTTS
#     library. The file will be saved as 'output_filename'.

#     # TODO: @definitive_cantidate
#     """
#     output_filename = Output.get_filename(output_filename, FileType.AUDIO)
    
#     model = TTS(language = voice.processed_language)
#     # TODO: Find a list with the speaker IDs to
#     # know how they work and how to customize it
#     speaker_ids = model.hps.data.spk2id
#     # TODO: What is 'quiet' for? And some other 
#     # parameters? Is any interesting (?)
#     model.tts_to_file(
#         text = text,
#         speaker_id = speaker_ids['ES'],
#         output_path = output_filename,
#         speed = voice.processed_speed
#     )

#     return output_filename

# PROJECT_ABSOLUTE_PATH = DevPathHandler.get_project_abspath()

# def clone_voice(input_filename):
#     CHECKPOINTS_PATH = (Path(__file__).parent.parent.__str__() + '/resources/openvoice/checkpoints_v2/').replace('\\', '/')
    
#     ckpt_converter = CHECKPOINTS_PATH + 'converter'
#     device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
#     tone_color_converter = ToneColorConverter(f'{ckpt_converter}/config.json', device = device)
#     tone_color_converter.load_ckpt(f'{ckpt_converter}/checkpoint.pth')
#     source_se = torch.load(f'{CHECKPOINTS_PATH}/base_speakers/ses/es.pth', map_location = device)
#     # This will generate a 'se.pth' file and some wavs that are the cloned voice
#     target_se, audio_name = se_extractor.get_se(input_filename, tone_color_converter, vad = False)


# def imitate_voice(text, input_filename = None, output_filename = None):
#     """
#     This method imitates the 'input_filename' provided voice and
#     generates a new narration of the provided 'text' and stores it
#     as 'output_filename'.

#     The provided 'input_filename' must be a valid audio file that
#     contains a clear narration to be imitated.

#     # TODO: @definitive_cantidate
#     """
#     if not input_filename:
#         return None
    
#     if not output_filename:
#         return None
    
#     CHECKPOINTS_PATH = (Path(__file__).parent.parent.__str__() + '/resources/openvoice/checkpoints_v2/').replace('\\', '/')
    
#     ckpt_converter = CHECKPOINTS_PATH + 'converter'
#     device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
#     tone_color_converter = ToneColorConverter(f'{ckpt_converter}/config.json', device = device)
#     tone_color_converter.load_ckpt(f'{ckpt_converter}/checkpoint.pth')

#     source_se = torch.load(f'{CHECKPOINTS_PATH}/base_speakers/ses/es.pth', map_location = device)
#     target_se, audio_name = se_extractor.get_se(input_filename, tone_color_converter, vad = False)

#     # This below is for testing
#     # audio_segs is the number of audio segments created
#     # se_save_path is the path in which se.pth file has been saved
#     # TODO: Need to know the path in which everything is saved to detect audio
#     # segments number and also to be able to load the 'se.pth' file
#     path = PROJECT_ABSOLUTE_PATH + 'processed/narracion_irene_albacete_recortado_v2_OMR2KXcN3jYVFUsb'
#     tone_color_converter.extract_se(30, se_save_path = path), 'narracion_irene_albacete_recortado_v2_OMR2KXcN3jYVFUsb'
#     # TODO: Check what is 'target_se' to check if it is a string and we can
#     # point the 'se.pth' file, because I don't already understand how it works
#     # This above is for testing

#     # We generate a narration to obtain it but with the 'input_filename' voice
#     source_filename = 'tmp.wav'
#     narrate(text, output_filename = source_filename)

#     encode_message = "@MyShell"
#     tone_color_converter.convert(
#         audio_src_path = source_filename, 
#         src_se = source_se, 
#         tgt_se = target_se, 
#         output_path = output_filename,
#         message = encode_message)
    
#     # TODO: Remove tmp file 'source_filename'
#     try:
#         os.remove('tmp.wav')
#     except:
#         pass

#     return output_filename



# def __test():
#     # TODO: This must be deleted, I keep it to ensure nothing will fail in the future
#     # TODO: Took from here (https://github.com/myshell-ai/OpenVoice/blob/main/demo_part3.ipynb)
#     PATH = 'C:/Users/dania/Desktop/PROYECTOS/yta-ai-utils/yta_ai_utils/'

#     ckpt_converter = PATH + 'resources/openvoice/checkpoints_v2/converter'
#     device = "cuda:0" if torch.cuda.is_available() else "cpu"
#     output_dir = 'output/openvoice'

#     tone_color_converter = ToneColorConverter(f'{ckpt_converter}/config.json', device = device)
#     tone_color_converter.load_ckpt(f'{ckpt_converter}/checkpoint.pth')

#     os.makedirs(output_dir, exist_ok = True)

#     reference_speaker = PATH + 'resources/test.m4a' # This is the voice you want to clone
#     target_se, audio_name = se_extractor.get_se(reference_speaker, tone_color_converter, vad = False)

#     texts = {
#         'EN_NEWEST': "Did you ever hear a folk tale about a giant turtle?",  # The newest English base speaker model
#         'EN': "Did you ever hear a folk tale about a giant turtle?",
#         'ES': "El resplandor del sol acaricia las olas, pintando el cielo con una paleta deslumbrante.",
#         'FR': "La lueur dorée du soleil caresse les vagues, peignant le ciel d'une palette éblouissante.",
#         'ZH': "在这次vacation中，我们计划去Paris欣赏埃菲尔铁塔和卢浮宫的美景。",
#         'JP': "彼は毎朝ジョギングをして体を健康に保っています。",
#         'KR': "안녕하세요! 오늘은 날씨가 정말 좋네요.",
#     }

#     src_path = f'{output_dir}/tmp.wav'

#     # Basic (no cloning) below
#     speed = 1.0

#     for language, text in texts.items():
#         model = TTS(language=language, device=device)
#         speaker_ids = model.hps.data.spk2id
        
#         for speaker_key in speaker_ids.keys():
#             speaker_id = speaker_ids[speaker_key]
#             speaker_key = speaker_key.lower().replace('_', '-')
            
#             source_se = torch.load(f'{PATH}checkpoints_v2/base_speakers/ses/{speaker_key}.pth', map_location=device)
#             model.tts_to_file(text, speaker_id, src_path, speed = speed)
#             save_path = f'{output_dir}/output_v2_{speaker_key}.wav'

#             # Run the tone color converter
#             encode_message = "@MyShell"
#             tone_color_converter.convert(
#                 audio_src_path=src_path, 
#                 src_se=source_se, 
#                 tgt_se=target_se, 
#                 output_path=save_path,
#                 message=encode_message)