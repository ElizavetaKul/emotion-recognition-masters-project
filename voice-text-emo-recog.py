# -*- coding: utf-8 -*-
"""
 
Voice and text emotion recognition for 3-sec audio pieces using Aniemore and Whisper libraries

Original file is located at
    https://colab.research.google.com/drive/1gahgYj0A6XtsGL7e-38lL0ZFK7Ob3JMt
"""

# @title Если файлы находятся на гугл диске, подключимся к нему
from google.colab import drive
drive.mount('/content/drive')

# @title Выполним необходимые загрузки
!pip install pydub
!pip install git+https://github.com/openai/whisper.git

import pydub
from pydub import AudioSegment
import glob
import os
import math
import pandas as pd
import whisper
from pathlib import Path
import torch

# @title Изменим канал streo на mono. Разделим аудио на отрывки по n секунд (определим в sec_per_split)
for n in range(1, 11):
    sound = AudioSegment.from_wav(f'/content/drive/MyDrive/эмоции/full_audios/audio_{n}.wav')
    sound = sound.set_channels(1)

    total_dur = math.ceil(sound.duration_seconds)

    sec_per_split = 3
    c = 1
    for i in range(0, total_dur, sec_per_split):
      beg = i * 1000
      end = (i + sec_per_split) * 1000

      sliced = sound[beg:end]
      sliced.export(f'/content/audio_{n}_{c}.wav', format='wav')
      c += 1


# @title Загрузим модель Whisper
whisper_model = whisper.load_model("large")


# @title Загрузим модели Aniemore
%pip install -Uq aniemore rich wget

# @title Text emotion recognition
from rich import print  
from aniemore.recognizers.text import TextRecognizer
from aniemore.models import HuggingFaceModel

text_model = HuggingFaceModel.Text.Bert_Tiny2
device = 'cuda' if torch.cuda.is_available() else 'cpu'

tr = TextRecognizer(model=text_model, device=device)

script = {}
text_emo = {}

for file in glob.glob('/content/audio_*.wav'): 
  path = '/content/'
  filename = os.path.basename(file)

  text = whisper_model.transcribe(path+filename)
  script[f'{filename}'] = str(text['text'])

  emo_from_text = tr.recognize(str(text['text']), return_single_label=True)
  text_emo[f'{filename}'] = emo_from_text

audio_text = pd.DataFrame(list(script .items()), columns=['num', 'text'])   
text_emo_df = pd.DataFrame(list(text_emo .items()), columns=['num', 'emo_text'])

# @title Voice emotion recognition

from aniemore.recognizers.voice import VoiceRecognizer

voice_model = HuggingFaceModel.Voice.WavLM
device = 'cuda' if torch.cuda.is_available() else 'cpu'
vr = VoiceRecognizer(model=voice_model, device=device)

voice_emo = {}

for file in glob.glob('/content/audio_*.wav'):
    filename = f'/content/{os.path.basename(file)}'

    result = vr.recognize(filename, return_single_label=True)
    voice_emo[f'{os.path.basename(file)}'] = result


voice_emo_df = pd.DataFrame(list(voice_emo .items()), columns=['num', 'emo_voice'])

# @title Сохраним результаты в csv файл

merged = pd.merge(
    audio_text, text_emo_df,
    left_on='num',
    right_on='num'
)

merged_results = pd.merge(
    merged, voice_emo_df,
    left_on='num',
    right_on='num'
)

merged_results.to_csv('emotion_recognition_results.csv')

