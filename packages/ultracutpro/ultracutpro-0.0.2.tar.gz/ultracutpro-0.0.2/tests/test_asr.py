from ultracutpro.ai.voice.sensevoice import run_sensevoice
from ultracutpro.ai.voice.sensevoice import SenseVoiceInfer
from pprint import pprint

# run_sensevoice()

asr = SenseVoiceInfer()
res = asr.asr("data/output3.mp3")
pprint(res)
