発話内容の要約プログラム
====

IBM Watson Speech to Text (音声認識)のAPIとA3RTのText Summarization APIを組み合わせた、
発話内容を要約するPythonスクリプトです。

## Description
[Speech to Text](https://www.ibm.com/watson/jp-ja/developercloud/speech-to-text.html)と[Text Summarization API](https://a3rt.recruit-tech.co.jp/product/TextSummarizationAPI/)を利用して、発話内容を要約します。  

プログラムを実行すると音声録音が始まり、スクリプト中で設定した時間が経過するとその間に話された内容がSpeech to Textにより音声認識され、その結果をText Summarization APIに渡すことによって内容が要約されます。  

デフォルトでは、一連のフローで下記のファイルが出力されます。  
- recording.wav: 録音した音声
- speech.txt: 音声認識した結果
- summary.txt: 要約結果

また、オプションでそれぞれのAPIから返されるjson形式のデータをファイルに出力することもできます。
- speech.json: Speech to Textのレスポンス
- summary.json: Text Summarization APIのレスポンス

各ファイル名についてもオプションで設定可能です。

## Demo
<img src="demo/demo.gif" alt="demo" style="width: 75%">

## Requirement
* ibm-cloud-sdk-core 1.5.1
* ibm-watson 4.3.0
* PyAudio 0.2.11
* PyPrind 2.11.2
* requests 2.22.0

## Usage

```example.py
import speech_summary

ss = speech_summary.SpeechSummary(WATSON_API_KEY,
                                  A3RT_API_KEY)

ss.record(record_time_seconds=15)
speech_text = ss.speech_to_text()
result = ss.text_summarization(speech_text)
```

## Author

[nekunet](https://github.com/nekunet)
