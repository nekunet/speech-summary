import configparser


def do_read_test():
    apikey_txt = configparser.ConfigParser()
    apikey_txt.read('../APIKEY.txt', encoding='utf-8')

    speech_api_key = apikey_txt['SPEECH_TO_TEXT']['API_KEY']
    print(type(speech_api_key))
    print(speech_api_key)

    summarization_api_key = apikey_txt['TEXT_SUMMARIZATION']['API_KEY']
    print(type(summarization_api_key))
    print(summarization_api_key)


if __name__ == "__main__":
    do_read_test()
