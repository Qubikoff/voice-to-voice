from gtts import gTTS
from IPython.display import Audio, display

def clean_text(text):
    return text.strip().lower()

def respond_to_text(text):
    cleaned_text = clean_text(text)
    if "привет я разработчик" in cleaned_text:
        response = "сегодня выходной"
    elif "я сегодня не приду домой" in cleaned_text:
        response = "ну и катись отсюда"
    else:
        response = "непонятная команда"
    return response

def text_to_speech(text):
    tts = gTTS(text=text, lang='ru')
    tts.save("response.mp3")
    display(Audio("response.mp3", autoplay=True))
