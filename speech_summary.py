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
            出力した音声ファイル名
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

    def speech_to_text(self, audio_filename="recording.wav",
                       speech_json_filename="speech.json",
                       json_output=False,
                       speech_txt_filename="speech.txt"):
        """音声ファイルから、テキストデータにする関数。

        WatsonのSpeech to TextのAPIを利用して、音声ファイルから文字に起こす。

        Args:
            audio_filename: 対象の音声ファイル。
            speech_json_file: Speech to Textから返されるjson形式の出力ファイル。
            json_output: APIから返されるjson形式のデータをファイルに出力するか。
            speech_txt_filename: 音声データを文字に起こしたtxt形式の出力ファイル。

        Returns:
            音声を文字に起こしたテキストデータ。
        """

        # returnする結果
        speech_text = ""

        # Watsonのspeech to text APIの初期化
        authenticator = IAMAuthenticator(self._speech_api_key)

        # 認証
        speech_to_text = SpeechToTextV1(
            authenticator=authenticator
        )

        # endpointはTokyo DCに設定
        endpoint = "https://gateway-tok.watsonplatform.net/speech-to-text/api"
        speech_to_text.set_service_url(endpoint)

        try:
            print("[INFO] WatsonにAPIリクエストを送信中")

            with open(audio_filename, "rb") as audio_file:
                # APIに渡す設定
                cont_type = "audio/wav"
                lang = "ja-JP_BroadbandModel"

                # リクエストの送信
                result = speech_to_text.recognize(audio=audio_file,
                                                  content_type=cont_type,
                                                  model=lang)

            print("[INFO] Watsonからレスポンスを受信しました")

            # 結果をjson形式にdumps
            # ensure_ascii=Falseで日本語の文字化けに対応
            result_json = json.dumps(result.get_result(), indent=2,
                                     ensure_ascii=False)

            # jsonファイルの保存
            if json_output:
                with open(speech_json_filename, "w") as f:
                    f.write(result_json)
                print("[INFO] Watsonからのレスポンスを {0} に保存しました"
                      .format(speech_json_filename))

            # transcriptの結果をリストに格納していく
            speech_list = []
            json_dict = json.loads(result_json)
            for i in range(len(json_dict["results"])):
                # 単語間の空白を消す
                tmp = json_dict["results"][i]
                tmp = tmp["alternatives"][0]["transcript"].replace(" ", "")
                speech_list.append(tmp)

            # txtファイルの保存
            with open(speech_txt_filename, "w") as f:
                for st in speech_list:
                    f.write(st+"。\n")
            print("[INFO] 音声認識の結果を {0} に保存しました".format(speech_txt_filename))

            # 文末に丸をつけてjoin
            for st in speech_list:
                speech_text += st + "。"

        # エラーハンドリング
        except ApiException as ex:
            print("Method failed with status code "
                  + str(ex.code) + ": "
                  + ex.message)
            exit()

        return speech_text

    def text_summarization(self, sentences, linenumber="1",
                           summary_json_filename="summary.json",
                           json_output=False,
                           summary_txt_filename="summary.txt"):
        """テキストデータの文章を要約する関数。

        A3RTのText Summarization APIを使って、文章を要約する。

        Args:
            sentences: テキストデータ。
            summary_json_file: Text Summarization APIから返されるjson形式の出力ファイル。
            json_output: APIから返されるjson形式のデータをファイル出力するか。
            summary_txt_filename: 要約した文章のtxt形式の出力ファイル。

        Returns:
            要約したテキストデータ。
        """

        # returnする結果
        summary_text = ""

        # エンドポイント
        endpoint = "https://api.a3rt.recruit-tech.co.jp/text_summarization/v1"

        print("[INFO] A3RTにAPIリクエストを送信中")

        # リクエストパラメータ
        # linenumberは抽出文章数。1以上の整数で、入力した文章数より少ない数（API制約事項）
        payload = {"apikey": self._summarization_api_key,
                   "sentences": sentences,
                   "linenumber": linenumber}

        # リクエストをpost
        r = requests.post(endpoint, payload)
        result = r.json()

        print("[INFO] A3RTからレスポンスを受信しました")

        # jsonファイルの保存
        if json_output:
            with open(summary_json_filename, "w") as f:
                f.write(json.dumps(result, indent=2, ensure_ascii=False))
            print("[INFO] A3RTからのレスポンスを {0} に保存しました"
                  .format(summary_json_filename))

        if result["status"] == 0:
            for i in range(len(result["summary"])):
                summary_text += result["summary"][i] + "。\n"

        # エラーハンドリング
        else:
            print("Method failed with status code "
                  + str(result["status"]) + ": "
                  + result["message"])
            exit()

        # txtファイルの保存
        with open(summary_txt_filename, "w") as f:
            f.write(summary_text)
        print("[INFO] 要約した結果を {0} に保存しました".format(summary_txt_filename))

        return summary_text
