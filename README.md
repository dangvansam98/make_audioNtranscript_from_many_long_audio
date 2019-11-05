# make_audioNtranscript_from_many_long_audio
Cắt (nhiều) file audio thành từng câu và tạo transcript cho từng file  - Make audio chunk and transcript from (many) long duration audio files python\

data dir: test\
language transcript: vietnamse, https://cloud.google.com/speech-to-text/docs/languages\
mode: all (split+save+transcript+merge)\
run: python make_audioNtranscript_from_many_long_audio.py --input test --lang vi --mode all\
output splited audio files (folder): test_cuted\
outpu transcript files (folder): test_cuted_trans\
transcript of all files (text file): test_cuted_tran.txt
