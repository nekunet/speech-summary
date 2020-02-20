import configparser

import speech_summary


def main():
    apikey_txt = configparser.ConfigParser()
    apikey_txt.read('APIKEY.txt', encoding='utf-8')

    speech_api_key = apikey_txt['SPEECH_TO_TEXT']['API_KEY']
    summarization_api_key = apikey_txt['TEXT_SUMMARIZATION']['API_KEY']

    ss = speech_summary.SpeechSummary(speech_api_key, summarization_api_key)

    ss.record(record_time_seconds=10)
    speech_text = ss.speech_to_text()


if __name__ == "__main__":
    main()
