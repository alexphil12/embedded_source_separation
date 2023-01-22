# -*- coding: utf-8 -*-
"""
Created on Fri Jan 13 10:54:57 2023

@author: alexa
"""

#!/usr/bin/env python
# Created on 2018/12/09
# Author: Kaituo XU

import argparse
import json
import os

import librosa


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


def preprocess(args):
    for sett in ["valid","test","train"]:    
        for speaker in ['mix', 's1', 's2']:
            preprocess_one_dir(os.path.join(args.in_dir,sett,speaker),
                               os.path.join(args.out_dir, sett),
                               speaker,
                               sample_rate=args.sample_rate)
            
if __name__ == "__main__":
    parser = argparse.ArgumentParser("WSJ0 data preprocessing")
    parser.add_argument('--in-dir', type=str, default="C:/Users/alexa/OneDrive/Bureau/Source-audio-SIA",
                        help='Directory path of wsj0')
    parser.add_argument('--out-dir', type=str, default="C:/Users/alexa/OneDrive/Bureau/Source-audio-JSON",
                        help='Directory path to put output files')
    parser.add_argument('--sample_rate', type=int, default=11025,
                        help='Sample rate of audio file')
    args = parser.parse_args()
    print(args)
    preprocess(args)