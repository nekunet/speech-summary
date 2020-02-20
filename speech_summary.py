import json
import pyaudio
import requests
import wave
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import ApiException
from pyprind import prog_bar


class SpeechSummary(object):
    """発話内容を要約するクラス

    IBM Watson Speech to TextとA3RTのText Summarization APIを
    組み合わせて発話内容を要約する。

    Args:
        speech_api_key: Speech to TextのAPIKEY。
        summarization_api_key: Text SummarizationのAPIKEY。s
    """

    def __init__(self, speech_api_key, summarization_api_key):
        self._speech_api_key = speech_api_key
        self._summarization_api_key = summarization_api_key

    

