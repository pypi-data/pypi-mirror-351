"""
TODO: Refactor this because it is only accepting
audio filenames and not binary or other type of
audios.
"""
from yta_file.handler import FileHandler
from yta_programming.decorators.requires_dependency import requires_dependency
from yta_temp import Temp
from yta_programming.output import Output
from yta_constants.file import FileType
from pydub import AudioSegment
from pydub.effects import speedup
from typing import Union


@requires_dependency('moviepy', 'yta_audio_base', 'moviepy')
# TODO: Check and refactor this below
def crop_audio_file(
    audio_filename: str,
    duration: float,
    output_filename: Union[str, None] = None
):
    """
    Crops the 'audio_filename' provided to the requested 'duration'.

    This method returns the new audio 'output_filename' if valid, or
    False if it was not possible to crop it.
    """
    from moviepy import AudioFileClip

    if not audio_filename:
        return None
    
    audio_clip = AudioFileClip(audio_filename)

    if audio_clip.duration < duration:
        # TODO: Exception, None, review this
        print('audio is shorter than requested duration')
        return False
    
    audio_clip = audio_clip.with_duration(duration)
    
    if output_filename is not None:
        audio_clip.write_audiofile(Output.get_filename(output_filename, FileType.AUDIO))

    return audio_clip

@requires_dependency('moviepy', 'yta_audio_base', 'moviepy')
def speedup_audio_file(
    audio_filename: str,
    new_duration: int,
    output_filename: Union[str, None] = None
):
    """
    Receives an audio 'audio_filename' and makes it have the provided
    'new_duration' if shorter than the real one. It will speed up the
    audio to fit that new duration and will store the new audio file
    as 'output_filename'.
    """
    from moviepy import AudioFileClip

    if not audio_filename:
        return None
    
    # TODO: The FileValidator is now different and in
    # FileHandler and I cannot validate according to
    # the file content type (by now)
    if not FileHandler.is_file(audio_filename):
        return None
    # TODO: This code below was before
    # if not FileValidator.file_is_audio_file(audio_filename):
    #     return None
    
    audio = AudioFileClip(audio_filename)
    if audio.duration <= new_duration:
        return None
    
    # We calculate audio the speed_up factor 
    speed_factor = audio.duration / new_duration

    # We use a tmp file because input filename could be same as output 
    # TODO: Careful with extension
    tmp_audio_filename = Temp.get_filename('tmp_audio_shortened.wav')
    # TODO: What about format?
    sound = AudioSegment.from_file(audio_filename, format = 'mp3')
    final = speedup(sound, playback_speed = speed_factor)
    final.export(tmp_audio_filename, format = 'mp3')
    # TODO: This is giving 'PermissionError [WindError 5]' when input 
    # and output are the same

    output_filename = Output.get_filename(output_filename, FileType.AUDIO)

    FileHandler.rename_file(
        tmp_audio_filename,
        output_filename,
        True
    )

    return output_filename
