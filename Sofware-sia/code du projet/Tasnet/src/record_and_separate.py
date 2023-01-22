# -*- coding: utf-8 -*-
"""
Created on Wed Jan 18 11:22:54 2023

@author: alexa
"""
import pyaudio
from separate import *
import os
import librosa
import json
import wave

parser = argparse.ArgumentParser('Separate speech using TasNet')
parser.add_argument('--model_path', type=str,default="C:/Users/alexa/OneDrive/Bureau/save_model_1/final.path.rar",
                    help='Path to model file created by training')
parser.add_argument('--mix_dir', type=str, default="C:/Users/alexa/OneDrive/Documents/Code en tout genre/Python Scripts/Tasnet/src",
                    help='Directory including recorded wav files')
parser.add_argument('--mix_json', type=str, default="C:/Users/alexa/OneDrive/Documents/Code en tout genre/Python Scripts/Tasnet/src",
                    help='Json file including mixture wav files')
parser.add_argument('--out_dir', type=str, default="C:/Users/alexa/OneDrive/Documents/Code en tout genre/Python Scripts/Tasnet/src/sortie_res",
                    help='Directory putting separated wav files')
parser.add_argument('--use_cuda', type=int, default=1,
                    help='Whether use GPU to separate speech')
parser.add_argument('--sample_rate', default=11025, type=int,
                    help='Sample rate')
parser.add_argument('--batch_size', default=1, type=int,
                    help='Batch size')

def preprocess_one_dir(in_dir, out_dir, out_filename, sample_rate=11025):
    file_infos = []
    in_dir = os.path.abspath(in_dir)
    wav_list = os.listdir(in_dir)
    for wav_file in wav_list:
        if not wav_file.endswith('.wav'):
            continue
        wav_path = os.path.join(in_dir, wav_file)
        samples, _ = librosa.load(wav_path, sr=sample_rate)
        file_infos.append((wav_path, len(samples)))
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    with open(os.path.join(out_dir, out_filename + '.json'), 'w') as f:
        json.dump(file_infos, f, indent=4)









def readInputAudio():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 11025
    RECORD_SECONDS = 10
    WAVE_OUTPUT_FILENAME = "output.wav"

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("* recording")

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("* done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()


class AudioFile:
    chunk = 1024

    def __init__(self, file):
        """ Init audio stream """
        self.wf = wave.open(file, 'rb')
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=self.p.get_format_from_width(self.wf.getsampwidth()),
            channels=self.wf.getnchannels(),
            rate=self.wf.getframerate(),
            output=True
        )

    def play(self):
        """ Play entire file """
        print("* Play entire file")
        data = self.wf.readframes(self.chunk)
        while data != b'':
            self.stream.write(data)
            data = self.wf.readframes(self.chunk)

    def close(self):
        """ Graceful shutdown """
        self.stream.close()
        self.p.terminate()
if __name__ == '__main__':
    args = parser.parse_args()
    print(args)
    readInputAudio()
    in_dir="C:/Users/alexa/OneDrive/Documents/Code en tout genre/Python Scripts/Tasnet/src"
    preprocess_one_dir(in_dir, in_dir, "output") 
    separate(args)
    