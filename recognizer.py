import time
import json
import os
import wave
import requests
import zipfile
from wit import Wit
import vosk
import speech_recognition as sr
from difflib import SequenceMatcher

wit_token = "NFHOGPON4IXGC6IH2AAIW5FF7ATMYZBI"
wit_client = Wit(wit_token)

# Инициализация Vosk модели
model_url = "https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip"
model_path = "vosk-model-small-ru-0.22.zip"
model_dir = "model/vosk-model-small-ru-0.22"

if not os.path.exists(model_dir):
    # Загрузка модели
    response = requests.get(model_url, stream=True)
    with open(
