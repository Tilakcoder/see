import torch
import torchaudio
import sounddevice as sd
from transformers import AutoProcessor, WhisperForConditionalGeneration

class SpeechtoText:
    def __init__(self):
        self.processor = AutoProcessor.from_pretrained("openai/whisper-tiny.en")
        self.model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-tiny.en")
        print("voice is ready")

    # Load the audio from a local file using torchaudio
    def audioFfile(self, audio_file_path = "audio/output.wav"):
        waveform, sample_rate = torchaudio.load(audio_file_path)
        inputs = self.processor(waveform.squeeze().numpy(), sampling_rate=sample_rate, return_tensors="pt")
        return inputs

    def getRecord(self, duration=2, sample_rate=16000, trig=False):
        audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
        sd.wait()
        waveform = torch.tensor(audio_data).float()
        waveform = waveform.T
        waveform = waveform / 32767.0
        threshold = 0.05
        if torch.any(torch.abs(waveform) > threshold) and trig:
            return True
        elif trig:
            return False
        
        return waveform

    def audio_from_mic(self, duration=2, sample_rate=16000):
        print("recording")
        waveform = self.getRecord(duration, sample_rate)
        print("recording complete")
        inputs = self.processor(waveform.squeeze().numpy(), sampling_rate=sample_rate, return_tensors="pt")
        return inputs

    def text(self, inputs):
        input_features = inputs.input_features
        generated_ids = self.model.generate(inputs=input_features)
        transcription = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return transcription

# voice = SpeechtoText()

# while True:
#     if voice.getRecord(0.25, trig=True):
#         print(voice.text(voice.audio_from_mic()))


