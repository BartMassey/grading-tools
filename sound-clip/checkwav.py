#!/usr/bin/python3
import argparse
import numpy as np
import sys, soundfile

ap = argparse.ArgumentParser()
ap.add_argument(
    "-t", "--test",
    help="Test WAV.",
)
ap.add_argument(
    "-r", "--ref",
    help="Reference WAV.",
)
ap.add_argument(
    "-d", "--difference",
    help="RMS difference to trigger reporting",
    type=float,
    default=0.5,
)
args = ap.parse_args()

def approx(n1, n2, delta):
    return abs(n1 - n2) <= delta

def fail(msg):
    print(msg)
    exit(1)

# Read a tone from a wave file.
def read_wave(filename):
    with soundfile.SoundFile(filename) as f:
        if f.format != 'WAV':
            fail(f"unknown file format {f.format}")
        if f.subtype != 'PCM_16':
            fail(f"wrong file subtype {f.subtype}")
        if f.channels != 1:
            fail(f"{f.channels} channels")
        if f.samplerate != 48000:
            fail(f"sample rate {f.samplerate}")
        if f.frames != 48000:
            print(f"warning: {f.frames} frames")
            if not approx(f.frames, 48000, 10):
                fail(f"sample length {f.frames / 48000} secs")
        data = f.read(dtype=np.int16)
    return data

wav = read_wave(args.test)
nwav = len(wav)
refwav = read_wave(args.ref)
nrefwav = len(refwav)
assert nrefwav == 48000
if nwav < nrefwav:
    refwav = refwav[:nrefwav]
elif nwav > nrefwav:
    wav = wav[:nrefwav]

signal = (wav.astype(np.float64) - refwav.astype(np.float64)) / 32768.0
rms = np.sqrt(np.mean(np.square(signal)))
if rms >= args.difference:
    fail(f"rms error {rms}")
