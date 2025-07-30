"""
Utils for audio conversion.

TODO: This utils should not have the ParameterValidator
for checkings, they must be done in the static class
that simplifies their use.
"""
from yta_temp import Temp
from yta_validation.parameter import ParameterValidator
from yta_programming.decorators.requires_dependency import requires_dependency
from pydub import AudioSegment

import numpy as np


@requires_dependency('moviepy', 'yta_audio_base', 'moviepy')
def audiosegment_to_audioclip(
    audio: AudioSegment
):
    """
    Export the 'audio' AudiOSegment to a file and
    read it as a moviepy audio file.

    TODO: Please, make it through memory and not writting files.
    """
    from moviepy import AudioFileClip

    ParameterValidator.validate_mandatory_instance_of('audio', audio, AudioSegment)
    
    # TODO: I have not been able to create an AudioFileClip dinamically
    # from memory information. I don't want to write but...
    tmp_filename = Temp.get_filename('tmp_audio.wav')
    audio.export(tmp_filename, format = 'wav')

    return AudioFileClip(tmp_filename)

@requires_dependency('moviepy', 'yta_audio_base', 'moviepy')
def audioclip_to_audiosegment(
    audio: 'AudioClip'
):
    """
    This method returns the provided moviepy audio converted into a
    pydub AudioSegment.

    TODO: This method currently writes a temporary file to make the 
    conversion. This needs to be improved to avoid writting files.
    """
    from moviepy import AudioClip

    ParameterValidator.validate_mandatory_instance_of('audio', audio, 'AudioClip')

    # TODO: Please, improve this to be not writting files
    tmp_filename = Temp.get_filename('tmp_audio.wav')
    audio.write_audiofile(tmp_filename)
    audio = AudioSegment.from_file(tmp_filename, format = 'wav')

    return audio

# TODO: This has not been tested properly
def numpy_to_audiosegment(
    audio: np.ndarray, sample_rate
):
    """
    Convers the provided 'audio' numpy array,
    that contains the audio data and must be in
    float32 or int16, to a pydub AudioSegment.

    TODO: Untested method
    """
    ParameterValidator.validate_mandatory_numpy_array('audio', audio)
    
    # Normalize audio_array if it's not already in int16 format
    if audio.dtype not in [np.int16, np.float32]:
        raise Exception('The "audio" parameter provided is not np.int16 nor np.float32.')
    
    audio = (
        # Assuming the audio_array is in float32 with values between -1 and 1
        (audio * 32767).astype(np.int16)
        if audio != np.int16 else
        audio
    )

    if audio.ndim not in [1, 2]:
        raise Exception("Audio array must be 1D (mono) or 2D (stereo).")
    
    channels = (
        1
        if audio.ndim == 1 else
        audio.shape[1]
    )
    
    return AudioSegment(
        data = audio.tobytes(),
        sample_width = 2,  # 16 bits = 2 bytes
        frame_rate = sample_rate,
        channels = channels
    )

def audiosegment_to_numpy(
    audio: AudioSegment
):
    """
    This method turns the provided 'audio' AudioSegment into a numpy
    array by converting it first to an AudioFileClip and then to a
    numpy.

    TODO: Please, maybe it is a better (more direct) way

    TODO: This method has not been tested properly
    """
    ParameterValidator.validate_mandatory_instance_of('audio', audio, AudioSegment)
    
    # TODO: Maybe this is not the best way, I need
    # to test and improve this
    return np.array(audio.get_array_of_samples())

@requires_dependency('moviepy', 'yta_audio_base', 'moviepy')
def numpy_to_audioclip(
    audio: np.ndarray
):
    """
    This method turns the provided 'audio' np.ndarray
    into a moviepy AudioClip.

    TODO: This method has not been tested properly
    """
    from moviepy import AudioClip

    ParameterValidator.validate_mandatory_numpy_array('audio', audio)
    
    # TODO: This is untested, make it work
    return AudioClip(audio)

@requires_dependency('moviepy', 'yta_audio_base', 'moviepy')
def audioclip_to_numpy(
    audio: 'AudioClip'
):
    """
    Convers the provided 'audio' moviepy AudioFileClip to a numpy
    array that will be np.float32.
    """
    from moviepy import AudioClip

    ParameterValidator.validate_mandatory_instance_of('audio', audio, 'AudioClip')
    
    # TODO: Check this: https://github.com/Zulko/moviepy/issues/2027#issuecomment-1937357458

    chunk_size = 5 * 1024 * 1024
    audio_chunks = []
    for chunk in audio.iter_chunks(chunksize = chunk_size):
        # Convertir cada fragmento a un array numpy y añadirlo a la lista
        audio_array = np.frombuffer(chunk, dtype=np.int16)
        
        # Normalizar si el audio es estéreo (tendría dos columnas)
        if (
            len(audio_array) > 0 and
            len(audio_array) % 2 == 0
        ):
            audio_array = audio_array.reshape(-1, 2)
        
        audio_chunks.append(audio_array)
    
    # Concatenar todos los fragmentos en un solo array
    full_audio_array = np.concatenate(audio_chunks, axis = 0)
    
    # Convertir a float32 y normalizar
    full_audio_array = full_audio_array.astype(np.float32)

    return (
        full_audio_array / np.max(np.abs(full_audio_array))
        if np.max(np.abs(full_audio_array)) > 1.0 else
        full_audio_array
    )


__all__ = [
    'audiosegment_to_audioclip',
    'audioclip_to_audiosegment',
    'numpy_to_audiosegment',
    'audiosegment_to_numpy',
    'numpy_to_audioclip',
    'audioclip_to_numpy'
]