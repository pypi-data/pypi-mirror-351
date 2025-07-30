from yta_audio_base.converter.utils import audiosegment_to_audioclip, numpy_to_audiosegment, audioclip_to_audiosegment, numpy_to_audioclip
from yta_constants.enum import YTAEnum as Enum
from yta_validation import PythonValidator
from yta_validation.parameter import ParameterValidator
from yta_file.handler import FileHandler
from yta_programming.output import Output
from yta_programming.decorators.requires_dependency import requires_dependency
from yta_constants.file import FileType
from pydub import AudioSegment
from typing import Union

import numpy as np


class AudioExtension(Enum):
    """
    Enum class to encapsulate the accepted audio extensions for our
    system.
    """

    # TODO: Maybe interconnect with 'ffmpeg_handler.py' Enums
    MP3 = 'mp3'
    WAV = 'wav'
    M4A = 'm4a'
    WMA = 'wma'
    CD = 'cd'
    OGG = 'ogg'
    AIF = 'aif'
    # TODO: Check which extensions are valid for the AudioSegment
    # and the 'export' method to be able to classify AudioExtension
    # enums in AudioSegmentAudioExtension or similar because we
    # should also have AudioExtension for the FfmpegHandler...

class AudioConverter:
    """
    Class to simplify and encapsulate the functionality
    related to audio conversion.
    """

    @requires_dependency('moviepy', 'yta_audio_base', 'moviepy')
    @staticmethod
    def to(
        audio: Union[str, np.ndarray, AudioSegment, 'AudioClip'],
        extension: AudioExtension,
        output_filename: Union[str, None] = None
    ):
        """
        This method converts the provided 'audio' to an audio with
        the provided 'extension' by storing it locally as the 
        provided 'output_filename' (or as a temporary file if not
        provided), and returns the new audio and the filename.

        This method returns two values: audio, filename
        """
        from moviepy import AudioClip

        ParameterValidator.validate_mandatory_instance_of('audio', audio, [str, np.ndarray, AudioSegment, AudioClip])

        audio = AudioConverter.to_audiosegment(audio)
        extension = AudioExtension.to_enum(audio)

        # TODO: Here we use AudioExtension but not FileExtension
        output_filename = Output.get_filename(output_filename, extension.value)
        
        # if not output_filename:
        #     # TODO: Replace this when not exporting needed
        #     output_filename = Temp.get_filename(f'tmp_converted_sound.{extension.value}')
        # else:
        #     output_filename = ensure_file_extension(output_filename, extension.value)

        audio.export(output_filename, format = extension.value)
        audio = AudioConverter.to_audiosegment(output_filename)

        # TODO: Maybe return a FileReturn instead of this (?)
        return audio, output_filename

    @requires_dependency('moviepy', 'yta_audio_base', 'moviepy')
    @staticmethod
    def to_wav(
        audio: Union[str, np.ndarray, AudioSegment, AudioClip],
        output_filename: str
    ):
        """
        This method converts the provided 'audio' to a wav audio
        by storing it locally as the provided 'output_filename'
        (or as a temporary file if not provided), and returns the
        new audio and the filename.

        This method returns two values: audio, filename
        """
        from moviepy import AudioClip

        ParameterValidator.validate_mandatory_instance_of('audio', audio, [str, np.ndarray, AudioSegment, AudioClip])

        return AudioConverter.to(audio, AudioExtension.WAV, output_filename)
    
    @requires_dependency('moviepy', 'yta_audio_base', 'moviepy')
    @staticmethod
    def to_mp3(
        audio: Union[str, np.ndarray, AudioSegment, AudioClip],
        output_filename: str
    ):
        """
        This method converts the provided 'audio' to a mp3 audio
        by storing it locally as the provided 'output_filename'
        (or as a temporary file if not provided), and returns the
        new audio and the filename.

        This method returns two values: audio, filename
        """
        from moviepy import AudioClip

        ParameterValidator.validate_mandatory_instance_of('audio', audio, [str, np.ndarray, AudioSegment, AudioClip])

        return AudioConverter.to(audio, AudioExtension.MP3, output_filename)
    
    @requires_dependency('moviepy', 'yta_audio_base', 'moviepy')
    @staticmethod
    def to_audioclip(
        audio: Union[str, np.ndarray, AudioSegment, AudioClip],
        output_filename: Union[str, None] = None
    ):
        from moviepy import AudioClip

        ParameterValidator.validate_mandatory_instance_of('audio', audio, [str, np.ndarray, AudioSegment, AudioClip])

        if (
            PythonValidator.is_string(audio) and
            not FileHandler.is_audio_file(audio)
        ):
            raise Exception('Provided "audio" filename is not a valid audio file.')
        
        audio = (
            AudioFileClip(audio)
            if PythonValidator.is_string(audio) else
            numpy_to_audioclip(audio)
            if PythonValidator.is_numpy_array(audio) else
            # TODO: Check this works
            # TODO: Create the util
            audiosegment_to_audioclip(audio)
            if PythonValidator.is_instance(audio, AudioSegment) else
            None # TODO: Raise Exception (?)
        )

        if output_filename is not None:
            output_filename = Output.get_filename(output_filename, FileType.VIDEO)
            audio.write_audiofile(output_filename)

        # TODO: Maybe use a FileReturn instead (?)
        return audio, output_filename
    
    @requires_dependency('moviepy', 'yta_audio_base', 'moviepy')
    @staticmethod
    def to_audiosegment(
        audio: Union[str, np.ndarray, AudioSegment, AudioClip],
        output_filename: Union[str, None] = None
    ):
        """
        Forces the provided 'audio' to be a pydub AudioSegment
        and returns it if valid 'audio' provided or raises an
        Exception if not.
        """
        from moviepy import AudioClip

        ParameterValidator.validate_mandatory_instance_of('audio', audio, [str, np.ndarray, AudioSegment, AudioClip])

        if (
            PythonValidator.is_string(audio) and
            not FileHandler.is_audio_file(audio)
        ):
            raise Exception('Provided "audio" filename is not a valid audio file.')
            
        audio = (
            AudioSegment.from_file(audio)
            if PythonValidator.is_string(audio) else
            # TODO: Check this
            # TODO: What about sample_rate (?)
            numpy_to_audiosegment(audio)
            if PythonValidator.is_numpy_array(audio) else
            audioclip_to_audiosegment(audio)
            if PythonValidator.is_instance(audio, AudioClip) else
            None # TODO: Raise Exception (?)
        )

        if output_filename is not None:
            # TODO: Validate 'output_filename'
            # TODO: Use the extension, please
            audio.export(output_filename, format = 'wav')

        return audio, output_filename
    
    