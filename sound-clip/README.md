# checkwav: test wav file for conformance with a reference
Bart Massey 2021

This program compares the WAV file parameters and actual
samples of a test WAV with those of a reference WAV
and reports differences.

The test of the samples uses RMS difference as a
heuristic. Use `-d <diff>` to change the heuristic value.
`-d 0` triggers if the samples are not identical.  `-d 1`
ignores differences in samples. The default is 0.05.
