from recognizer import compare_models
from utils import respond_to_text, text_to_speech
import os
import pyaudio
import wave

def record_audio(filename):
    chunk = 1024
    format = pyaudio.paInt16
    channels = 1
    rate = 16000
    record_seconds = 5

    p = pyaudio.PyAudio()

    stream = p.open(format=format,
                    channels=channels,
                    rate=rate,
                    input=True,
                    frames_per_buffer=chunk)

    print("Recording...")

    frames = []

    for i in range(0, int(rate / chunk * record_seconds)):
        data = stream.read(chunk)
        frames.append(data)

    print("Recording finished")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(format))
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()

if __name__ == "__main__":
    filename = "input.wav"
    record_audio(filename)
    recognized_text = compare_models(filename)
    response_text = respond_to_text(recognized_text)
    text_to_speech(response_text)
    print(f"Распознанный текст: {recognized_text}")
    print(f"Ответ: {response_text}")
    os.remove(filename)
