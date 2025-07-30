"""
Module to easily parse the audio.
"""
from yta_audio.converter import AudioConverter
from yta_audio_base.types import AudioType, validate_parameter_with_type


class AudioParser:
    """
    Class to simplify the way we parse audios.
    """

    @staticmethod
    def as_audioclip(
        audio: AudioType
    ):
        validate_parameter_with_type(AudioType, 'audio', audio, True)
        
        audio, _ = AudioConverter.to_audioclip(audio)

        return audio
    
    @staticmethod
    def as_audiosegment(
        audio: AudioType
    ):
        validate_parameter_with_type(AudioType, 'audio', audio, True)

        audio, _ = AudioConverter.to_audiosegment(audio)

        return audio
    
    # TODO: '.as_numpy()' ? It is difficult due to rate
    # or strange mapping... (?)