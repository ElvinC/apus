# modified_ax25_tx.py
import wave
import numpy as np

# -------------- user settings --------------
samplerate = 9600          # sample rate (keep 9600 if you prefer)
samples_per_bit = int(samplerate / 1200)  # should be exact integer (e.g. 8 when sr=9600)
mark_freq = 1200.0         # mark = 1200 Hz (commonly "1")
space_freq = 2200.0        # space = 2200 Hz (commonly "0")
sine_table_size = 1024
amplitude = 0.8            # fraction of full scale
preamble_flags = 128       # number of 0x7E flags to send before the frame
postamble_flags = 32
outfile = "aprs_out.wav"
# optional invert if your decoder expects opposite polarity
invert_tones = False
# -------------- AX.25 payload --------------
dest = "M6CYT"   # callsign only (no trailing SSID here)
dest_ssid = 1
src = "M6CYT"
src_ssid = 1
message = "/214517h4903.50N/17023.65W"

# -------------- helpers --------------
def ax25_callsign_bytes(call, ssid):
    # call: up to 6 chars or 7? In AX.25 each callsign field is 7 bytes left-padded with spaces,
    # each character left-shifted one bit. Last byte is SSID with LSB=0 except last address
    # Format: 6 or 7 char? Spec expects 6-character callsign + SSID byte (but many use 7-length including space)
    call = call.upper().ljust(6)[:6]  # ensure length 6
    out = []
    for ch in call:
        out.append(ord(ch) << 1)
    # SSID byte: bit format:  bit7=1, bit6=SSID, others: per AX.25. We'll set typical SSID encoding:
    ssid_byte = (ssid & 0x0f) << 1
    ssid_byte |= 0x60  # set bits 7..5 as typical (0b011). Many implementations use 0x60 here.
    # Leave LSB 0 (not the end-of-address flag) — caller will set last-address bit
    out.append(ssid_byte & 0xFE)
    return out

def build_frame_bytes(dest_call, dest_ssid, src_call, src_ssid, info_bytes):
    content = []
    # destination (7 bytes)
    content += ax25_callsign_bytes(dest_call, dest_ssid)
    # source (7 bytes) — mark the last address byte's low bit as 1 to indicate end of address field
    src_field = ax25_callsign_bytes(src_call, src_ssid)
    # set last address octet LSB to 1 to indicate last address in the header:
    src_field[-1] |= 0x01
    content += src_field
    # Control and PID
    content.append(0x03)  # UI frame
    content.append(0xF0)  # no layer 3 protocol
    # Info
    content += [b for b in info_bytes]
    # Now compute CRC (FCS) — CRC-16-CCITT (x^16 + x^12 + x^5 + 1), X.25 variant: reflected
    # We'll follow the bitwise LSB-first approach used in many examples (poly 0x8408).
    crc = 0xFFFF
    for val in content:
        v = val
        for _ in range(8):
            bit = (v ^ crc) & 0x01
            crc >>= 1
            if bit:
                crc ^= 0x8408
            v >>= 1
    crc ^= 0xFFFF
    # Append LSB first then MSB
    content.append(crc & 0xFF)
    content.append((crc >> 8) & 0xFF)
    return bytes(content)

def bytes_to_nrz_bits(frame_bytes):
    # produce NRZ bits LSB-first per byte
    bits = []
    for b in frame_bytes:
        for bit in range(8):
            bits.append((b >> bit) & 1)
    return bits

def bit_stuff_nrz(nrz_bits):
    stuffed = []
    ones = 0
    for bit in nrz_bits:
        stuffed.append(bit)
        if bit == 1:
            ones += 1
            if ones == 5:
                # insert a 0 after five 1s
                stuffed.append(0)
                ones = 0
        else:
            ones = 0
    return stuffed

def nrz_to_nrzi(nrz_bits, initial_level=1):
    # NRZI: '0' -> transition, '1' -> no transition
    level = initial_level
    nrzi_levels = []
    for bit in nrz_bits:
        if bit == 0:
            level ^= 1
        # append current level (tone state) for this bit
        nrzi_levels.append(level)
    return nrzi_levels

# -------------- build AX.25 frame --------------
info = message.encode('ascii')
frame = build_frame_bytes(dest, dest_ssid, src, src_ssid, info)
print(frame)
# convert to NRZ bits
nrz = bytes_to_nrz_bits(frame)
# add flags pre/post in NRZ form (flag 0x7E is transmitted LSB-first) -> we'll add in NRZ bits later
# do bit stuffing
nrz_stuffed = bit_stuff_nrz(nrz)
# NRZ -> NRZI
nrzi = nrz_to_nrzi(nrz_stuffed, initial_level=1)

# prepend and append many flags (0x7E) in NRZ, stuffed then encoded to NRZI
flag_byte = 0x7E
flag_bits = [(flag_byte >> i) & 1 for i in range(8)]
# produce preamble NRZ bits (repeated)
preamble_nrz = flag_bits * preamble_flags
postamble_nrz = flag_bits * postamble_flags

# full NRZ stream (preamble + payload + postamble)
full_nrz = preamble_nrz + nrz_stuffed + postamble_nrz
# re-run NRZI encoding for the whole stream (cleaner)
full_nrzi = nrz_to_nrzi(full_nrz, initial_level=1)

# -------------- generate audio using DDS + sine LUT --------------
# prepare sine table
sine = np.sin(2.0 * np.pi * np.arange(sine_table_size) / sine_table_size)

# compute DDS increments
# phase accumulator is 16-bit as in your original code (wrap @65536)
def freq_to_delta(freq, sr):
    return int(round(freq / sr * 65536)) & 0xFFFF

delta_mark = freq_to_delta(mark_freq, samplerate)
delta_space = freq_to_delta(space_freq, samplerate)
# build samples
track = []
phase_acc = 0

for nrzi_level in full_nrzi:
    # map NRZI level to tone: 1 -> mark, 0 -> space (swap if invert_tones)
    if invert_tones:
        tone_delta = delta_space if nrzi_level == 1 else delta_mark
    else:
        tone_delta = delta_mark if nrzi_level == 1 else delta_space
    for _ in range(samples_per_bit):
        phase_acc = (phase_acc + tone_delta) & 0xFFFF
        # map 16-bit phase_acc to sine index
        idx = (phase_acc * sine_table_size) >> 16   # top bits -> index
        sample = sine[idx]
        track.append(sample)

# scale to int16
audio = np.array(track) * (amplitude * (2**15 - 1))
audio = audio.astype('<i2')  # little-endian 16-bit

# write WAV
with wave.open(outfile, 'wb') as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(samplerate)
    wf.writeframes(audio.tobytes())

print("Wrote", outfile, "samples:", len(audio))