import sounddevice as sd
import soundfile as sf

fs = 44100
duration = 300
print("starting")
myrec = sd.rec(int(duration*fs), samplerate=fs, channels=1)
sd.wait()
print("done")
print(myrec)
sf.write("madhura_6.wav", myrec, samplerate=fs)