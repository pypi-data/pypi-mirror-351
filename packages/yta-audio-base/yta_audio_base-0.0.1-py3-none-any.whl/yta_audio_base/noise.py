from yta_audio_base.parser import AudioParser
from yta_audio_base.types import AudioType, validate_parameter_with_type
from yta_audio_base.converter import AudioConverter
from yta_temp import Temp
from yta_file.handler import FileHandler
from yta_programming.output import Output
from yta_validation.parameter import ParameterValidator
from yta_constants.file import FileType
from df.enhance import enhance, init_df, load_audio, save_audio
from typing import Union


class AudioNoise:
    """
    Class to simplify and encapsulate the code related with audio noise.
    """

    # TODO: Set 'audio' types
    def remove(
        audio: AudioType,
        output_filename: Union[str, None] = None
    ):
        """
        Remove the noise from the provided audio and, if 'output_filename'
        is provided, the audio without noise is written localy with that
        filename.
        """
        # Using deepfilternet https://github.com/Rikorose/DeepFilterNet
        # TODO: This fails when .mp3 is used, so we need to transform into wav.
        # TODO: Output file must be also wav
        # TODO: What about audioclip instead of audiofile? Is it possible? (?)
        # Based on this (https://medium.com/@devesh_kumar/how-to-remove-noise-from-audio-in-less-than-10-seconds-8a1b31a5143a)
        # https://github.com/Rikorose/DeepFilterNet
        # TODO: This is failing now saying 'File contains data in an unknon format'...
        # I don't know if maybe some library, sh*t...
        # Load default model
        
        # If it is not an audio filename I need to create it to be able to
        # work with (TODO: Check how to turn into same format as when readed)
        # TODO: Refactor these below to accept any audio, not only filename
        validate_parameter_with_type(AudioType, 'audio', audio, True)
        ParameterValidator.validate_string('output_filename', output_filename, do_accept_empty_string = False)

        tmp_audio_filename = Temp.get_filename('audio_temp.wav')

        audio = AudioParser.as_audiosegment(audio)
        _, tmp_audio_filename = AudioConverter.to_wav(audio, tmp_audio_filename) 

        # TODO: This was done before because the parameter was only
        # a filename and now I'm accepting other audio types
        # if audio_filename.endswith('.mp3'):
        #     # TODO: Maybe it is .wav but not that format...
        #     mp3_to_wav(audio_filename, TMP_WAV_FILENAME)
        #     audio_filename = TMP_WAV_FILENAME

        model, df_state, _ = init_df()
        audio, _ = load_audio(tmp_audio_filename, sr = df_state.sr())
        # Remove the noise
        enhanced = enhance(model, df_state, audio)

        output_filename = Output.get_filename(output_filename, FileType.AUDIO)

        save_audio(output_filename, enhanced, df_state.sr())

        try:
            FileHandler.delete_file(tmp_audio_filename)
        except:
            pass

        # TODO: What do we return, maybe a FileReturn (?)
        return output_filename

    # TODO: Create a 'generate' noise method