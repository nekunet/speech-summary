import json
import pyaudio
import requests
import wave
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import ApiException
from pyprind import prog_bar


class SpeechSummary(object):
    """発話内容を要約するクラス。

    IBM Watson Speech to TextとA3RTのText Summarization APIを
    組み合わせて発話内容を要約する。

    Args:
        speech_api_key: Speech to TextのAPIKEY。
        summarization_api_key: Text SummarizationのAPIKEY。s
    """

    def __init__(self, speech_api_key, summarization_api_key):
        self._speech_api_key = speech_api_key
        self._summarization_api_key = summarization_api_key

    def record(self, audio_format=pyaudio.paInt16, channels=1,
               rate=44100, chunk=2**11, record_time_seconds=10,
               input_device_index=0, filename="recording.wav"):
        """マイクから音声を録音して、wavファイルに出力する関数。

        Args:
            audio_format: 音声のフォーマット。
            channels: モノラル(1) or ステレオ(2)。
            rate: サンプルレート。
            chunk: データ点数。
            record_time_seconds: レコーディング時間（秒）。
            input_device_index: 録音デバイスのインデックス番号
            filename: 音声ファイルを出力するファイル名。
        
        Returns:
            出力した音声ファイル名。
        """

        # pyaudio初期化
        audio = pyaudio.PyAudio()

        # audioとして保存するためのストリーム
        stream = audio.open(
            format=audio_format,
            channels=channels,
            rate=rate,
            input=True,
            input_device_index=input_device_index,
            frames_per_buffer=chunk
        )

        # レコード開始
        stream.start_stream()
        print("[INFO] レコーディングを開始します")
        frames = []
        for i in prog_bar(range(int(rate / chunk * record_time_seconds))):
            data = stream.read(chunk)
            frames.append(data)

        # レコード停止
        print("[INFO] レコーディングを停止しました")
        stream.stop_stream()
        stream.close()
        audio.terminate()

        # ファイルへの保存
        wf = wave.open(filename, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(audio.get_sample_size(audio_format))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))
        wf.close()
        print("[INFO] {0} に音声ファイルを出力しました".format(filename))

        return filename

