from google.cloud import speech_v1 as speech
import os
import io
import librosa

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'YOUR_FILE_OAuth_client'


def get_config(samplerate, language):
    return speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
        sample_rate_hertz=samplerate,
        language_code=get_lang_code(language)
    )


# language codes: https://cloud.google.com/speech-to-text/docs/languages
def get_lang_code(language):
    if language == "Ukrainian":
        return "uk-UA"
    elif language == "English":
        return "en-US"


# if audio longer than 1 minute (asynchronous speech recognition)
def speech_to_text_long(config, audio):
    client = speech.SpeechClient()
    response = client.long_running_recognize(config=config, audio=audio).result()
    return get_sentences(response)


def speech_to_text(config, audio):
    client = speech.SpeechClient()
    response = client.recognize(config=config, audio=audio)
    return get_sentences(response)


def get_sentences(response):
    transcript = ""
    for result in response.results:
        best_alternative = result.alternatives[0]
        transcript = best_alternative.transcript
        confidence = best_alternative.confidence
    if transcript != "":
        if confidence >= 0.4:
            return transcript
        else:
            return "Sorry, I'm not sure :("
    else:
        return "Sorry, I didn't understand you :("


# for OGG_OPUS Sample rate must be one of 8000 Hz, 12000 Hz,
# 16000 Hz, 24000 Hz or 48000 Hz
def get_samplerate(file):
    fn_ogg = file
    return librosa.get_samplerate(fn_ogg)


def to_text(file, lang="English"):
    file_name = os.path.join(os.path.dirname(__file__), file)
    with io.open(file_name, "rb") as audio_file:
        content = audio_file.read()
        audio = speech.RecognitionAudio(content=content)
    duration = librosa.get_duration(filename=file_name)
    try:
        if 60 < duration <= 300:
            res = speech_to_text_long(get_config(get_samplerate(file_name), lang), audio)
        elif duration < 60:
            res = speech_to_text(get_config(get_samplerate(file_name), lang), audio)
        else:
            res = "I can't convert this message."
    finally:
        os.remove(file)
    return res
