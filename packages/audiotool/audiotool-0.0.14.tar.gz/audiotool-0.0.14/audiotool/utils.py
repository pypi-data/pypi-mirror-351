import os
import numpy as np
from pydub import AudioSegment


def pad_audio(audio, target_duration=550):
    """
    如果音频长度小于目标持续时间，则在音频末尾添加静音以达到目标长度。

    :param audio: pydub.AudioSegment 对象
    :param target_duration: 目标持续时间（毫秒）
    :return: 填充后的 pydub.AudioSegment 对象
    """
    target_length = target_duration  # 目标长度，单位为毫秒

    if len(audio) < target_length:
        padding_length = target_length - len(audio)
        silence = AudioSegment.silent(
            duration=padding_length, frame_rate=audio.frame_rate
        )
        padded_audio = audio + silence
    else:
        padded_audio = audio

    return padded_audio


def normalize_audio_to_target(
    input_file, target_sample_rate=16000, pad_to_ms=None, save_to_tmp=False
):
    _, file_extension = os.path.splitext(input_file)

    # Load the audio file
    if file_extension.lower() == ".mp3":
        audio = AudioSegment.from_mp3(input_file)
    elif file_extension.lower() == ".wav":
        audio = AudioSegment.from_wav(input_file)
    else:
        raise ValueError("Unsupported file format. Please use MP3 or WAV.")

    # Convert to mono if it's not already
    if audio.channels > 1:
        audio = audio.set_channels(1)

    # Set the sample rate if it's different from the target
    if audio.frame_rate != target_sample_rate:
        audio = audio.set_frame_rate(target_sample_rate)

    # padding audio when it is too short
    if pad_to_ms is not None:
        audio = pad_audio(audio, target_duration=pad_to_ms)
    # Normalize the audio
    if save_to_tmp:
        output_file = os.path.join(
            "/tmp", os.path.basename(input_file)[:-4] + "_normalized.wav"
        )
    else:
        output_file = os.path.splitext(input_file)[0] + "_normalized.wav"
    audio.export(output_file, format="wav", parameters=["-acodec", "pcm_s16le"])
    return output_file


def save_np_float32_to_wav_file(audio_data, sr, output_file):
    audio_data = audio_data.astype(np.float32)

    max_abs_value = np.max(np.abs(audio_data))
    if max_abs_value > 1.0:
        audio_data = audio_data / max_abs_value

    audio_data_int = (audio_data * 32767).astype(np.int16)

    # 创建 AudioSegment 对象
    audio_segment = AudioSegment(
        audio_data_int.tobytes(),
        frame_rate=sr,
        sample_width=2,  # 16 位 = 2 字节
        channels=1 if audio_data.ndim == 1 else audio_data.shape[0],
    )

    audio_segment.export(output_file, format="wav")
