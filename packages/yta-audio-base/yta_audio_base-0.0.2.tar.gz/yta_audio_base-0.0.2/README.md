# Youtube Autonomous Audio Module

The Audio module.

Please, check the 'pyproject.toml' file to see the dependencies.

Here you have some tests audio files:
- test_coqui_tts.wav (https://drive.google.com/file/d/11rpFl-uCMaOKDW79-C86Sv1A1SvzjOZX/view?usp=sharing)
- test_google_tts.wav (https://drive.google.com/file/d/1eZxWcmDVhmKmRXDFhTYYuTLtHum4DVnf/view?usp=sharing)
- test_imitate_open_voice_tts.wav (https://drive.google.com/file/d/1Eoyq9uPYULUb1bv4C1-IKPvmtRaWXiMv/view?usp=sharing)
- test_imitate_voice_coqui_tts_recortado.wav (https://drive.google.com/file/d/1P1DU6i-M4zFoLA6Cy-EmHyoCMDJ4535R/view?usp=sharing)
- test_imitate_voice_coqui_tts.wav (https://drive.google.com/file/d/1P1DU6i-M4zFoLA6Cy-EmHyoCMDJ4535R/view?usp=sharing)
- test_microsoft_tts.wav (https://drive.google.com/file/d/1V41taeZjGEh9Oj9mW17k-AhbKKmFZ0Sm/view?usp=sharing)
- test_open_voice_tts.wav (https://drive.google.com/file/d/1atc7AsZKBDxkE3IZ0MAQsCcvXDd6R5kf/view?usp=sharing)

There are some libraries that need special installation as they are not public through _pip install_ command.

==> MeloTTS

This library is not published in pypi, so we need to use the "pip install git+https://github.com/myshell-ai/MeloTTS.git" command to install it from the official repo. Also, use the "python -m unidic download" command to install any missing dictionary.

Here you have the official guide for any trouble (https://github.com/myshell-ai/OpenVoice/blob/main/docs/USAGE.md#quick-use).

==> OpenVoice

TODO: ¿Quizás probar "pip install git+https://github.com/myshell-ai/OpenVoice.git"? Como MeloTSS This library is not published in pypi, so we need to handle it manually. First, we need to clone the official project with the "git clone https://github.com/myshell-ai/OpenVoice.git" command. Once downloaded, you install it by using the "pip install ./OpenVoice" command. Once installed, we need to manually change a line in the "se_extractor.py" file to let the model instantiation line use only the first argument (there are 3, but we cannot work with cuda nor float16). Please, read this official guide if any trouble (https://github.com/Alienpups/OpenVoice/blob/main/docs/USAGE_WINDOWS.md), and for downloading the "checkpoints_v2" we need to work. Place them in the project. If you have any trouble with languages, use the "python -m unidic download" command.

This library is for voice cloning and uses the MeloTTS library described in the previous step.