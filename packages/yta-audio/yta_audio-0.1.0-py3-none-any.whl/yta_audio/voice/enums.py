from yta_constants.lang import Language
from yta_constants.enum import YTAEnum as Enum
from typing import Union


class NarrationLanguage(Enum):
    """
    The languages available for voice narrations.

    This list is based on the ISO-639 but not all
    these languages are available for narrations 
    and also each narration engine has its own
    languages available. This list is also manually
    set in other libraries, so please ensure it
    keeps updated.
    """

    DEFAULT = 'default'
    """
    This value has been created for those cases
    in which there is a default language that is
    being used in the situation we are handling.

    Using this value will provide that default
    language. For example, a Youtube video can
    be in Turkish or in English as default,
    depending on the author. Using this 'default'
    value will ensure you obtain that Youtube
    video because that default language will
    always exist.
    """
    ABKHAZIAN = Language.ABKHAZIAN.value
    AFAR = Language.AFAR.value
    AFRIKAANS = Language.AFRIKAANS.value
    AKAN = Language.AKAN.value
    ALBANIAN = Language.ALBANIAN.value
    AMHARIC = Language.AMHARIC.value
    ARABIC = Language.ARABIC.value
    ARAGONESE = Language.ARAGONESE.value
    ARMENIAN = Language.ARMENIAN.value
    ASSAMESE = Language.ASSAMESE.value
    AVARIC = Language.AVARIC.value
    AVESTAN = Language.AVESTAN.value
    AYMARA = Language.AYMARA.value
    AZERBAIJANI = Language.AZERBAIJANI.value
    BAMBARA = Language.BAMBARA.value
    BASHKIR = Language.BASHKIR.value
    BASQUE = Language.BASQUE.value
    BELARUSIAN = Language.BELARUSIAN.value
    BENGALI = Language.BENGALI.value
    BISLAMA = Language.BISLAMA.value
    BOSNIAN = Language.BOSNIAN.value
    BRETON = Language.BRETON.value
    BULGARIAN = Language.BULGARIAN.value
    BURMESE = Language.BURMESE.value
    CATALAN = Language.CATALAN.value
    CHAMORRO = Language.CHAMORRO.value
    CHECHEN = Language.CHECHEN.value
    CHICHEWA = Language.CHICHEWA.value
    CHINESE = Language.CHINESE.value
    CHINESE_TRADITIONAL = Language.CHINESE_TRADITIONAL.value
    # TODO: I think there are more complex values like
    # this above, but they are not in the list
    CHURCH_SLAVONIC = Language.CHURCH_SLAVONIC.value
    CHUVASH = Language.CHUVASH.value
    CORNISH = Language.CORNISH.value
    CORSICAN = Language.CORSICAN.value
    CREE = Language.CREE.value
    CROATIAN = Language.CROATIAN.value
    CZECH = Language.CZECH.value
    DANISH = Language.DANISH.value
    DIVEHI = Language.DIVEHI.value
    DUTCH = Language.DUTCH.value
    DZONGKHA = Language.DZONGKHA.value
    ENGLISH = Language.ENGLISH.value
    ESPERANTO = Language.ESPERANTO.value
    ESTONIAN = Language.ESTONIAN.value
    EWE = Language.EWE.value
    FAROESE = Language.FAROESE.value
    FIJIAN = Language.FIJIAN.value
    FINNISH = Language.FINNISH.value
    FRENCH = Language.FRENCH.value
    WESTERN_FRISIAN = Language.WESTERN_FRISIAN.value
    FULAH = Language.FULAH.value
    GAELIC = Language.GAELIC.value
    GALICIAN = Language.GALICIAN.value
    GANDA = Language.GANDA.value
    GEORGIAN = Language.GEORGIAN.value
    GERMAN = Language.GERMAN.value
    GREEK = Language.GREEK.value
    KALAALLISUT = Language.KALAALLISUT.value
    GUARANI = Language.GUARANI.value
    GUJARATI = Language.GUJARATI.value
    HAITIAN = Language.HAITIAN.value
    HAUSA = Language.HAUSA.value
    HEBREW = Language.HEBREW.value
    HERERO = Language.HERERO.value
    HINDI = Language.HINDI.value
    HIRI_MOTU = Language.HIRI_MOTU.value
    HUNGARIAN = Language.HUNGARIAN.value
    ICELANDIC = Language.ICELANDIC.value
    IDO = Language.IDO.value
    IGBO = Language.IGBO.value
    INDONESIAN = Language.INDONESIAN.value
    INTERLINGUA = Language.INTERLINGUA.value
    INTERLINGUE = Language.INTERLINGUE.value
    INUKTITUT = Language.INUKTITUT.value
    INUPIAQ = Language.INUPIAQ.value
    IRISH = Language.IRISH.value
    ITALIAN = Language.ITALIAN.value
    JAPANESE = Language.JAPANESE.value
    JAVANESE = Language.JAVANESE.value
    KANNADA = Language.KANNADA.value
    KANURI = Language.KANURI.value
    KASHMIRI = Language.KASHMIRI.value
    KAZAKH = Language.KAZAKH.value
    CENTRAL_KHMER = Language.CENTRAL_KHMER.value
    KIKUYU = Language.KIKUYU.value
    KINYARWANDA = Language.KINYARWANDA.value
    KYRGYZ = Language.KYRGYZ.value
    KOMI = Language.KOMI.value
    KONGO = Language.KONGO.value
    KOREAN = Language.KOREAN.value
    KUANYAMA = Language.KUANYAMA.value
    KURDISH = Language.KURDISH.value
    LAO = Language.LAO.value
    LATIN = Language.LATIN.value
    LATVIAN = Language.LATVIAN.value
    LIMBURGAN = Language.LIMBURGAN.value
    LINGALA = Language.LINGALA.value
    LITHUANIAN = Language.LITHUANIAN.value
    LUBA_KATANGA = Language.LUBA_KATANGA.value
    LUXEMBOURGISH = Language.LUXEMBOURGISH.value
    MACEDONIAN = Language.MACEDONIAN.value
    MALAGASY = Language.MALAGASY.value
    MALAY = Language.MALAY.value
    MALAYALAM = Language.MALAYALAM.value
    MALTESE = Language.MALTESE.value
    MANX = Language.MANX.value
    MAORI = Language.MAORI.value
    MARATHI = Language.MARATHI.value
    MARSHALLESE = Language.MARSHALLESE.value
    MONGOLIAN = Language.MONGOLIAN.value
    NAURU = Language.NAURU.value
    NAVAJO = Language.NAVAJO.value
    NORTH_NDEBELE = Language.NORTH_NDEBELE.value
    SOUTH_NDEBELE = Language.SOUTH_NDEBELE.value
    NDONGA = Language.NDONGA.value
    NEPALI = Language.NEPALI.value
    NORWEGIAN = Language.NORWEGIAN.value
    NORWEGIAN_BOKMAL = Language.NORWEGIAN_BOKMAL.value
    NORWEGIAN_NYNORSK = Language.NORWEGIAN_NYNORSK.value
    OCCITAN = Language.OCCITAN.value
    OJIBWA = Language.OJIBWA.value
    ORIYA = Language.ORIYA.value
    OROMO = Language.OROMO.value
    OSSETIAN = Language.OSSETIAN.value
    PALI = Language.PALI.value
    PASHTO = Language.PASHTO.value
    PERSIAN = Language.PERSIAN.value
    POLISH = Language.POLISH.value
    PORTUGUESE = Language.PORTUGUESE.value
    PUNJABI = Language.PUNJABI.value
    QUECHUA = Language.QUECHUA.value
    ROMANIAN = Language.ROMANIAN.value
    ROMANSH = Language.ROMANSH.value
    RUNDI = Language.RUNDI.value
    RUSSIAN = Language.RUSSIAN.value
    NORTHERN_SAMI = Language.NORTHERN_SAMI.value
    SAMOAN = Language.SAMOAN.value
    SANGO = Language.SANGO.value
    SANSKRIT = Language.SANSKRIT.value
    SARDINIAN = Language.SARDINIAN.value
    SERBIAN = Language.SERBIAN.value
    SHONA = Language.SHONA.value
    SINDHI = Language.SINDHI.value
    SINHALA = Language.SINHALA.value
    SLOVAK = Language.SLOVAK.value
    SLOVENIAN = Language.SLOVENIAN.value
    SOMALI = Language.SOMALI.value
    SOUTHERN_SOTHO = Language.SOUTHERN_SOTHO.value
    SPANISH = Language.SPANISH.value
    SUNDANESE = Language.SUNDANESE.value
    SWAHILI = Language.SWAHILI.value
    SWATI = Language.SWATI.value
    SWEDISH = Language.SWEDISH.value
    TAGALOG = Language.TAGALOG.value
    TAHITIAN = Language.TAHITIAN.value
    TAJIK = Language.TAJIK.value
    TAMIL = Language.TAMIL.value
    TATAR = Language.TATAR.value
    TELUGU = Language.TELUGU.value
    THAI = Language.THAI.value
    TIBETAN = Language.TIBETAN.value
    TIGRINYA = Language.TIGRINYA.value
    TONGA = Language.TONGA.value
    TSONGA = Language.TSONGA.value
    TSWANA = Language.TSWANA.value
    TURKISH = Language.TURKISH.value
    TURKMEN = Language.TURKMEN.value
    TWI = Language.TWI.value
    UIGHUR = Language.UIGHUR.value
    UKRAINIAN = Language.UKRAINIAN.value
    URDU = Language.URDU.value
    UZBEK = Language.UZBEK.value
    VENDA = Language.VENDA.value
    VIETNAMESE = Language.VIETNAMESE.value
    VOLAPUK = Language.VOLAPUK.value
    WALLOON = Language.WALLOON.value
    WELSH = Language.WELSH.value
    WOLOF = Language.WOLOF.value
    XHOSA = Language.XHOSA.value
    SICHUAN_YI = Language.SICHUAN_YI.value
    YIDDISH = Language.YIDDISH.value
    YORUBA = Language.YORUBA.value
    ZHUANG = Language.ZHUANG.value
    ZULU = Language.ZULU.value

# Engine > Language > NarratorName > Speed | Emotion
   
class VoiceEmotion(Enum):
    """
    The emotion to be transmited in the voice
    narration.
    """

    DEFAULT = 'default'
    SAD = 'sad'
    NORMAL = 'normal'
    HAPPY = 'happy'
    # TODO: Add more when available

class VoiceSpeed(Enum):
    """
    The speed to be used within the voice narration.
    """

    DEFAULT = 'default'
    SLOW = 'slow'
    NORMAL = 'normal'
    FAST = 'fast'
    # TODO: Add more when available

class VoicePitch(Enum):
    """
    The pitch to be used within the voice narration.
    """

    DEFAULT = 'default'
    LOW = 'low'
    NORMAL = 'normal'
    HIGH = 'high'
    # TODO: Add more when available

class VoiceNarrationEngine(Enum):
    """
    The engines we have available for voice narration
    generation.
    """

    DEFAULT = 'default'
    """
    When this option is provided, the system will
    choose one of the available enum elements.
    """
    COQUI = 'coqui'
    GOOGLE = 'google'
    MICROSOFT = 'microsoft'
    OPEN_VOICE = 'open_voice'
    TETYYS = 'tetyys'
    TIKTOK = 'tiktok'
    TORTOISE = 'tortoise'
    TTSMP3 = 'ttsmp3'

    def _get_engine(
        self
    ) -> 'VoiceNarrationEngine':
        """
        We turn the DEFAULT instance into a specific
        one to simplify the way we handle the options.

        For internal use only.
        """
        return (
            VoiceNarrationEngine.GOOGLE
            if self is VoiceNarrationEngine.DEFAULT else
            self
        )

    def get_voice_narrator_class(
        self
    # ) -> Union['CoquiVoiceNarrator', 'GoogleVoiceNarrator', 'MicrosoftVoiceNarrator', 'OpenVoiceVoiceNarrator', 'TetyysVoiceNarrator', 'TiktokVoiceNarrator', 'TortoiseVoiceNarrator', 'Ttsmp3VoiceNarrator']:
    ) -> Union['CoquiVoiceNarrator', 'GoogleVoiceNarrator', 'MicrosoftVoiceNarrator', 'TetyysVoiceNarrator', 'TiktokVoiceNarrator', 'TortoiseVoiceNarrator', 'Ttsmp3VoiceNarrator']:
        """
        Get the VoiceNarrator class associated with this
        enum instance.
        """
        # from yta_audio.voice.generation.narrator import CoquiVoiceNarrator, GoogleVoiceNarrator, MicrosoftVoiceNarrator, OpenVoiceVoiceNarrator, TetyysVoiceNarrator, TiktokVoiceNarrator, TortoiseVoiceNarrator, Ttsmp3VoiceNarrator
        from yta_audio.voice.generation.narrator import CoquiVoiceNarrator, GoogleVoiceNarrator, MicrosoftVoiceNarrator, TetyysVoiceNarrator, TiktokVoiceNarrator, TortoiseVoiceNarrator, Ttsmp3VoiceNarrator

        engine = self._get_engine()

        return {
            VoiceNarrationEngine.GOOGLE: GoogleVoiceNarrator,
            VoiceNarrationEngine.COQUI: CoquiVoiceNarrator,
            VoiceNarrationEngine.MICROSOFT: MicrosoftVoiceNarrator,
            # VoiceNarrationEngine.OPEN_VOICE: OpenVoiceVoiceNarrator,
            VoiceNarrationEngine.TETYYS: TetyysVoiceNarrator,
            VoiceNarrationEngine.TIKTOK: TiktokVoiceNarrator,
            VoiceNarrationEngine.TORTOISE: TortoiseVoiceNarrator,
            VoiceNarrationEngine.TTSMP3: Ttsmp3VoiceNarrator,
        }[engine]
    
    @property
    def available_languages(
        self
    ) -> list[NarrationLanguage]:
        return self.get_voice_narrator_class().get_available_languages()
    
    def is_language_valid(
        self,
        language: NarrationLanguage
    ) -> bool:
        """
        Check if the given 'language' is accepted by
        this engine.
        """
        return NarrationLanguage.to_enum(language) in self.available_languages
    
    def get_available_narrator_names(
        self,
        language: NarrationLanguage
    ) -> list[str]:
        return self.get_voice_narrator_class().get_available_narrator_names(language)
    
    def is_narrator_name_valid(
        self,
        language: NarrationLanguage,
        narration_name: str
    ) -> bool:
        return narration_name in self.get_available_narrator_names(language)

    @property
    def available_emotions(
        self
    ) -> list[VoiceEmotion]:
        return self.get_voice_narrator_class().get_available_emotions()
    
    def is_emotion_valid(
        self,
        emotion: VoiceEmotion
    ) -> bool:
        return VoiceEmotion.to_enum(emotion) in self.available_emotionsWW

    @property
    def available_speeds(
        self
    ) -> list[VoiceSpeed]:
        return self.get_voice_narrator_class().get_available_speeds()
    
    def is_speed_valid(
        self,
        speed: VoiceSpeed
    ) -> bool:
        return VoiceSpeed.to_enum(speed) in self.available_speeds
    
    @property
    def available_pitches(
        self
    ) -> list[VoicePitch]:
        return self.get_voice_narrator_class().get_available_pitches()
    
    def is_pitch_valid(
        self,
        pitch: VoicePitch
    ) -> bool:
        return VoicePitch.to_enum(pitch) in self.available_pitches