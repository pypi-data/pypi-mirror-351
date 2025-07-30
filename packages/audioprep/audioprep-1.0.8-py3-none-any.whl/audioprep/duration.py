import io
import math
import traceback
import wave

import librosa


def get_audio_duration_bytes(byte_buffer: io.BytesIO):
    """
    获取音频的时长
    :param byte_buffer: 音频字节流
    :return:音频长度
    """
    try:
        if not byte_buffer:
            return 0
        byte_buffer.seek(0)
        with wave.open(byte_buffer, 'rb') as combined_audio:
            frame_rate = combined_audio.getframerate()
            num_frames = combined_audio.getnframes()
            duration = num_frames / float(frame_rate)
            return round(duration, 1)
    except (Exception,):
        traceback.print_exc()
        return 0


def get_audio_duration(file_path):
    try:
        duration = librosa.get_duration(filename=file_path)
        return ceil_to_2decimal(duration)
    except Exception as e:
        print(f"Error: {e}")
        return None


def ceil_to_2decimal(number):
    if not number:
        return None
    return math.ceil(number * 100) / 100


if __name__ == '__main__':
    rs = get_audio_duration('./voices/tvb_shot.wav')
    print(f"音频时长: {rs}秒")
