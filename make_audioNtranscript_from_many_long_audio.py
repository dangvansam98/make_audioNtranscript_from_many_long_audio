import wave
import  requests
import  json
from pydub import AudioSegment
import os
from time import sleep
import  csv
import numpy as np
from pydub import AudioSegment
import tensorflow as tf
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
import librosa
from inaSpeechSegmenter import Segmenter, seg2csv
import  wave
import audioop
import scipy
from datetime import datetime

GOOGLE_SPEECH_API_KEY = "AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw"
GOOGLE_SPEECH_API_URL = "http://www.google.com/speech-api/v2/recognize?lang={lang}&key={key}"
#https://speech.googleapis.com/v1p1beta1/speech:recognize
def ggRequest(data, lang = 'vi', rate =16000):
    url = GOOGLE_SPEECH_API_URL.format(lang=lang, key=GOOGLE_SPEECH_API_KEY)
    headers = {"Content-Type": "audio/l16; rate=%d" % rate}
    try:
        resp = requests.post(url, data=data, headers=headers)
        #print(resp.text)
        for line in resp.text.split("\n"):
            #print(line)
            if len(resp.text.split("\n")) == 1:
                return None
            line = json.loads(line)
            if line['result'] == []:
                continue
            else:
                line = line['result'][0]['alternative'][0]['transcript']
                return line.lower()
    except:
        return None

def requestVTC(filename, proxy): 
    url = "https://vtcc.ai/voice/api/asr/v1/rest/decode_file"
    headers = {
        'token': 'anonymous',#'ulTkA-jNoKXB78VqO1Qg5GQ5eIeO91dlpi7n9WdnhvhADz6T0wzFxrw8iBkOCD4R',
        'sample_rate': '16000',
        #'format':'S16LE',
        'num_of_channels':'1',
        #'asr_model': 'model code'
        }
    #qpupDIOO3HY6HATdGde9ve0VzXMZl-SjSrT9RVv-Vz9nF3VsJtguOrpJzGzBad1o, anonymous
    
    s = requests.Session()
    files = {'file': open(filename,'rb')}
    if proxy != None:
        response = requests.post(url,files=files, headers=headers, verify='wwwvtccai.crt', proxy = proxy)
    else:
        response = requests.post(url,files=files, headers=headers, verify='wwwvtccai.crt')
    #print(response.text)
    res_json = response.json()
    #print(res_json)
    try:
        a = res_json[0]['status']
        if a == 0:
            transcript = res_json[0]['result']['hypotheses'][0]['transcript_normed']
            #print('request VTC success')
            print('VTC transcript:',transcript)
            if len(transcript) == 0:
                return None
            else:
                return transcript
    except:
        return None

def requestFPT(filename):
    url = 'https://api.fpt.ai/hmi/asr/general'
    payload = open(filename, 'rb').read()
    headers = {'api-key': 'eqJwxYhIkfgkCS1LB8ON5d7jKfEgj2na'} #examle: 'api-key': '3ISvE45DVemWTvrMTIgMtyfIjHnd8yAz' , qpupDIOO3HY6HATdGde9ve0VzXMZl-SjSrT9RVv-Vz9nF3VsJtguOrpJzGzBad1o
    try:
        response = requests.post(url=url, data=payload, headers=headers)
        print(response)
        res_json = response.json()
        print(res_json)
        a = res_json['status']
        if a == 0:
            transcript = res_json['hypotheses'][0]['utterance']
            #print('request FPT success')
            print('FPT transcript:',transcript)
            if len(transcript) == 0:
                return None
            else:
                return transcript
        else:
            return None
    except:
        return None
        
from time import sleep
def requestAndWriteFile_VTC_FPT(audio_dir_path, transcript_out_dir):
    audio_dir = audio_dir_path + '/'
    if not os.path.exists(audio_dir):
        print('Audio dir: "{}" not found! Plase check input dir'.format(audio_dir_path))
        exit()
    transcript_dir = transcript_out_dir + '/'
    if not os.path.exists(transcript_dir):
        os.mkdir(transcript_dir)
    print('Input audio files dir: {}'.format(audio_dir))
    print('Output transcript files dir: {}'.format(transcript_dir))
    #proxies = {'118.174.232.237:48665', '202.29.237.213:3128', '101.109.243.99:8080'}#get_proxies()
    for f in os.listdir(audio_dir):
        name_label_file = transcript_dir + f.split('/')[-1].replace('wav','txt')
        audio_path = audio_dir + f
        if os.path.isfile(name_label_file):
            print('Transript for: {} is exist in: {}. Skipped'.format(audio_path,name_label_file))
            continue
        else:
            #sleep(3)
            #res = requestFPT(audio_path)
            # if res == None:
            #     sleep(3)
            res = requestVTC(audio_path, None)
            sleep(1)
            if res == None:
                continue
            else:
                label_file = open(name_label_file, 'w', encoding='utf-8')
                label_file.write(res)
                print('Transript success, file:{}'.format(name_label_file))
                sleep(2)

def stereo_to_mono(audio_file_name):
    sound = AudioSegment.from_wav(audio_file_name)
    sound = sound.set_channels(1)
    sound.export(audio_file_name, format="wav")

def mp3_to_wav(audio_file_name):
    if audio_file_name.split('.')[1] == 'mp3':    
        sound = AudioSegment.from_mp3(audio_file_name)
        audio_file_name = audio_file_name.split('.')[0] + '.wav'
        sound.export(audio_file_name, format="wav")

def frame_rate_channel(audio_file_name):
    with wave.open(audio_file_name, "rb") as wave_file:
        frame_rate = wave_file.getframerate()
        channels = wave_file.getnchannels()
        return frame_rate,channels

def makeTransFile(in_file, out_file = ''):
    #data_dir = 'cut_by_sam/GDCD12'
    tran_file = open(in_file.split('/')[-1] + '_transcript.txt','w', encoding='utf-8')
    file_name = in_file
    #if f.endswith('.mp3'):
    #    mp3_to_wav(file_name)
    frame_rate, channels = frame_rate_channel(file_name)
    #print(frame_rate,channels)
    if channels > 1:
        stereo_to_mono(file_name)
    b_data = open(file_name,'rb')
    #print(b_data)
    text = ggRequest(b_data, rate = frame_rate)
    print(text)
    tran_file.write(file_name + ' ' + text + '\n')
    #break


def removeMusicAndCut(file_name, out_dir):
  print('\nREMOVE MUSIC AND CUT')
  seg = Segmenter()
  segmentation = seg(file_name)
  sample_rate, raw_audio = scipy.io.wavfile.read(file_name)
  speech = []
  print(segmentation)
  count = 1
  if not os.path.exists(out_dir):
    os.mkdir(out_dir)
  for s in segmentation:
    if s[0] != 'Music' and s[0] != 'NOACTIVITY':
      print(str(count),'dur of sen:',s[2]-s[1])
      speech_data = raw_audio[int(s[1]*sample_rate):int(s[2]*sample_rate + int(sample_rate/3))]
      speech_data = np.array(speech_data)

      print(len(speech_data), len(speech_data)/sample_rate)
      if len(speech_data)/sample_rate < 1.0 or len(speech_data)/sample_rate > 10:
        continue
      else:
        scipy.io.wavfile.write(out_dir + '/' + file_name.split('/')[-1].replace('.wav','') + '_' + str(count) + '.wav', sample_rate, speech_data)
        count += 1

def removeMusicAndCutManyFile(d, o = None):
    #d = 'dacnhantam'
    for f in os.listdir(d):
        print(f)
        if o == None:
            removeMusicAndCut(d+'/'+f,d+ '_cuted') #output dir is: <d>_cuted
        else:
            removeMusicAndCut(d+'/'+f,o) #output dir is: <o>

def requestAndWriteFile_GG(audio_dir_path, transcript_out_dir):
    audio_dir = audio_dir_path + '/'
    if not os.path.exists(audio_dir):
        print('Audio dir: "{}" not found! Plase check input dir'.format(audio_dir_path))
        exit()
    transcript_dir = transcript_out_dir + '/'
    if not os.path.exists(transcript_dir):
        os.mkdir(transcript_dir)
    print('Input audio files dir: {}'.format(audio_dir))
    print('Output transcript files dir: {}'.format(transcript_dir))
    for i,f in enumerate(os.listdir(audio_dir)):
        name_label_file = transcript_dir + f.split('/')[-1].replace('wav','txt')
        audio_path = audio_dir + f
        print('{}/{}:'.format(i,len(os.listdir(audio_dir)),f))
        if os.path.isfile(name_label_file):
            print('Transript for: {} is exist in: {}. Skipped'.format(audio_path,name_label_file))
            continue
        else:
            b_data = open(audio_path,'rb')
            res = ggRequest(b_data)
            if res == None:
                continue
            else:
                label_file = open(name_label_file, 'w', encoding='utf-8')
                label_file.write(res)
                print(audio_path,res)
                print('Transript success, file:{}'.format(name_label_file))
                
def mergeTransFileToOne(trans_dir):
    #trans_dir = 'thai_son_data_cuted_transcript/'
    print('MERGE {}'.format(trans_dir))
    text_file = open(trans_dir + '.txt','w',encoding = 'utf-8')
    for f in os.listdir(trans_dir):
        with open(trans_dir + '/' + f,'r',encoding='utf-8') as t:
            text = t.readline().lower()
        wav = f.replace('.txt','')
        text_file.write(wav + ' ' + text + '\n')

def runALL(datadir):
    removeMusicAndCutManyFile(datadir, datadir + '_cuted')
    requestAndWriteFile_GG(datadir + '_cuted', datadir + '_cuted' + 'trans')
    #requestAndWriteFile_VTC_FPT(datadir + '_cuted', datadir + '_cuted' + 'trans')
    mergeTransFileToOne(datadir + '_cuted' + 'trans')

if __name__ == "__main__":
    datadir = 'wavfiles'

    #removeMusicAndCutManyFile(datadir, datadir + '_cuted')

    #requestAndWriteFile_GG(datadir + '_cuted', datadir + '_cuted' + 'trans')

    #mergeTransFileToOne('aihoa_dacnhantam1_trans')
    #mergeTransFileToOne('bo_luat_hinh_su_nam_2015_sua_doi_bo_sung_2017_01_trans')
    #mergeTransFileToOne('GDCD12_trans')
    
    #cut long .wav file to many chunk (sentence) save to output folder and make transcript 
    runALL(datadir)