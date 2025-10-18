import pyaudio
import wave
import sys
import numpy as np
import random, struct
from scipy import signal



filename = "noise2.wav"

samplerate = 9600

track = [] # empty

freq_lut = np.sin(np.arange(0,8) / 8 * np.pi * 2) * 0.2
print(freq_lut)

accumulator = 0
delta_1200 = 0x2000
delta_2200 = 0x3aab


aprs_formatted = []

dest_address = "NOCALL1"
source_address = "NOCALL7"
message = ":YOU      :Y"

content_formatted = []

for c in dest_address:
    content_formatted.append(ord(c) << 1)

for c in source_address[:-1]:
    content_formatted.append(ord(c) << 1)

content_formatted.append((ord(source_address[-1]) << 1) | 0x01) # Set LSB

content_formatted.append(0x03)
content_formatted.append(0xF0)
for c in message:
    content_formatted.append(ord(c))

# Calculate CRC
crc = 0xFFFF
for i in range(len(content_formatted)):
    value = content_formatted[i]

    for bit in range(8):
        crc ^= (value & 0x01)
        
        if ( crc & 0x01 ):
            crc = ( crc >> 1 ) ^ 0x8408
        else:
            crc = ( crc >> 1 )

        value = value >> 1

crc = crc ^ 0xffff

content_formatted.append((crc) & 0xFF)
content_formatted.append((crc >> 8) & 0xFF)
print(crc)
print(",".join([f"{x:x}" for x in content_formatted]))

this_tone = delta_1200
tncTxBit = 1 # The bit being transmitted 
print(bytes(content_formatted))
ones_counter = 0

bitstream = []

# Transmit the frame

def add_bit():
    global accumulator

    bitstream.append(tncTxBit)
    for sample in range(8):

        accumulator = ((accumulator + this_tone) % 0x010000) & 0xFFFF
        #idx = (accumulator >> 13) & 0b100 # Only high/low
        #track.append(-0.5 if idx else 0.5)
        #track.append(freq_lut[idx])
        idx = (accumulator >> 15) & 0b00000001
        track.append(-0.5 if idx else 0.5)
        #track.append(idx)



for i in range(30):
    flag = 0x7E
    for bit in range(8):

        if (flag >> bit) & 0x01:
            ones_counter += 1
        else:
            tncTxBit = tncTxBit ^ 1 # Flip
            ones_counter = 0

        this_tone = delta_1200 if tncTxBit == 1 else delta_2200
        
        add_bit()

# Start by transmitting frame
for byte in range(len(content_formatted)):
    for bit in range(8):

        if (content_formatted[byte] >> bit) & 0x01:
            ones_counter += 1
        else:
            tncTxBit = tncTxBit ^ 1 # Flip
            ones_counter = 0

        this_tone = delta_1200 if tncTxBit == 1 else delta_2200

        add_bit()

        # Bit stuffing, flip and transmit
        if ones_counter == 5:
            tncTxBit = tncTxBit ^ 1 # Flip
            ones_counter = 0

            this_tone = delta_1200 if tncTxBit == 1 else delta_2200

            add_bit()

# Transmit the frame
flag = 0x7E
for i in range(30):
    for bit in range(8):

        if (flag >> bit) & 0x01:
            ones_counter += 1
        else:
            tncTxBit = tncTxBit ^ 1 # Flip
            ones_counter = 0

        this_tone = delta_1200 if tncTxBit == 1 else delta_2200
        
        add_bit()

#print("".join([str(b) for b in track]))
#print("".join([str(x) for x in bitstream]))

# Put the channels together
audio = np.array([np.array(track)]).T

audio = (audio * (2 ** 15 - 1)).astype("<h") # Little endial conversion

with wave.open('noise2.wav', "w") as f:
    # 2 Channels.
    f.setnchannels(1)
    # 2 bytes per sample.
    f.setsampwidth(2)
    f.setframerate(samplerate)
    f.writeframes(audio.tobytes())


# open the file for reading.
wf = wave.open(filename, 'rb')

# create an audio object
p = pyaudio.PyAudio()

# open stream based on the wave object which has been input.
stream = p.open(format =
                p.get_format_from_width(wf.getsampwidth()),
                channels = wf.getnchannels(),
                rate = wf.getframerate(),
                output = True)

# Set chunk size of 1024 samples per data frame
chunk = 1024  

# Open the sound file 
wf = wave.open(filename, 'rb')

# Create an interface to PortAudio
p = pyaudio.PyAudio()

# Open a .Stream object to write the WAV file to
# 'output = True' indicates that the sound will be played rather than recorded
stream = p.open(format = p.get_format_from_width(wf.getsampwidth()),
                channels = wf.getnchannels(),
                rate = wf.getframerate(),
                output = True)

# Read data in chunks
data = wf.readframes(chunk)

# Play the sound by writing the audio data to the stream
while data:
    stream.write(data)
    data = wf.readframes(chunk)

# Close and terminate the stream
stream.close()
p.terminate()