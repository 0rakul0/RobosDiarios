#!/usr/bin/env python3

import speech_recognition as sr

audio_path = "C:\\Users\\e7609043\\Desktop\\teste.wav"

r = sr.Recognizer()
with sr.WavFile(audio_path) as source:
     r.adjust_for_ambient_noise(source, duration=1)
     audio = r.record(source)
try:
     resposta = r.recognize_google(audio, show_all=True, language='pt-BR')
     if resposta != []:
          print('\nResposta:', '"',resposta['alternative'][0]['transcript'],'"', 'com', '{0:.2f}'.format(resposta['alternative'][0]['confidence']*100),'% de certeza')
     else:
          print('\nÉ rapaz, não foi dessa vez')
except:
     print('deu merda mesmo rapaz')

