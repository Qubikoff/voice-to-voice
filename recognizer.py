import time
import json
import os
import wave
from wit import Wit
import vosk
import speech_recognition as sr
import subprocess
from difflib import SequenceMatcher

wit_token = "NFHOGPON4IXGC6IH2AAIW5FF7ATMYZBI"
wit_client = Wit(wit_token)

if not os.path.exists("model"):
    subprocess.run(["wget", "https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip"])
    subprocess.run(["unzip", "vosk-model-small-ru-0.22.zip", "-d", "model"])
vosk_model = vosk.Model("model/vosk-model-small-ru-0.22")

recognizer = sr.Recognizer()

def convert_audio_to_wav(filename, output_filename):
    if os.path.exists(output_filename):
        os.remove(output_filename)
    
    command = [
        "ffmpeg", "-i", filename,
        "-ac", "1", "-ar", "16000",
        "-f", "wav", output_filename
    ]
    try:
        subprocess.run(command, check=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print(f"Error during ffmpeg conversion: {e.stderr.decode('utf-8')}")
        raise

def recognize_google(filename):
    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)
    start_time = time.time()
    try:
        text = recognizer.recognize_google(audio, language="ru-RU")
        end_time = time.time()
        return text, end_time - start_time
    except sr.UnknownValueError:
        return "", time.time() - start_time
    except sr.RequestError as e:
        return "", time.time() - start_time

def recognize_wit(filename):
    convert_audio_to_wav(filename, "temp_wit.wav")
    with sr.AudioFile("temp_wit.wav") as source:
        audio = recognizer.record(source)
    audio_content = audio.get_wav_data()
    start_time = time.time()
    try:
        response = wit_client.speech(audio_content, headers={"Content-Type": "audio/wav"})
        end_time = time.time()
        try:
            text = response['text']
        except KeyError:
            text = ""
        return text, end_time - start_time
    except Exception as e:
        print(f"Error with Wit.ai: {e}")
        return "", time.time() - start_time

def recognize_vosk(filename):
    wf = wave.open(filename, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() not in (8000, 16000, 32000, 44100, 48000):
        print("Файл должен быть монофоническим, 16 бит и с частотой 8000, 16000, 32000, 44100 или 48000 Гц")
        return "", 0
    
    rec = vosk.KaldiRecognizer(vosk_model, wf.getframerate())
    start_time = time.time()
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            result = rec.Result()
            result_dict = json.loads(result)
            text = result_dict.get("text", "")
            end_time = time.time()
            return text.lower(), end_time - start_time
    
    final_result = rec.FinalResult()
    final_result_dict = json.loads(final_result)
    final_text = final_result_dict.get("text", "")
    end_time = time.time()
    return final_text.lower(), end_time - start_time

def compare_models(filename):
    google_text, google_time = recognize_google(filename)
    wit_text, wit_time = recognize_wit(filename)
    vosk_text, vosk_time = recognize_vosk(filename)

    google_accuracy = SequenceMatcher(None, reference_text.lower(), google_text.lower()).ratio()
    wit_accuracy = SequenceMatcher(None, reference_text.lower(), wit_text.lower()).ratio()
    vosk_accuracy = SequenceMatcher(None, reference_text.lower(), vosk_text.lower()).ratio()

    best_model = max((google_text, google_time, google_accuracy, "Google"), 
                     (wit_text, wit_time, wit_accuracy, "Wit.ai"), 
                     (vosk_text, vosk_time, vosk_accuracy, "Vosk"), 
                     key=lambda x: x[2])
    
    print(f"Google Speech-to-Text: {google_text} (Time: {google_time:.2f} seconds, Accuracy: {google_accuracy:.2f})")
    print(f"Wit.ai: {wit_text} (Time: {wit_time:.2f} seconds, Accuracy: {wit_accuracy:.2f})")
    print(f"Vosk: {vosk_text} (Time: {vosk_time:.2f} seconds, Accuracy: {vosk_accuracy:.2f})")
    print(f"\nBest Model: {best_model[3]}")
    print(f"Recognized Text: {best_model[0]}")
    print(f"Time: {best_model[1]:.2f} seconds")
    print(f"Accuracy: {best_model[2]:.2f}")
    
    return best_model[0]
