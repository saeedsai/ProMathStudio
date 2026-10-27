# Offline real-signal FFT — development candidate

Open **Symbolic solver → Signal spectrum · offline FFT**. Enter 4–256 uniformly sampled real values, with a power-of-two length, separated by commas or whitespace. Example: 0, 1, 0, -1, 0, 1, 0, -1 yields bin 2 with amplitude 1. Eight samples of 3 produce DC amplitude 3. Alternating +1/-1 produces Nyquist amplitude 1.

The forward radix-2 DFT uses a negative exponential; inverse uses positive exponential and 1/N scaling. One-sided amplitude is |X[k]|/N at DC and Nyquist and 2|X[k]|/N for interior bins. Output includes bin, amplitude, phase (radians), raw real and imaginary DFT values. Save to Data Tables or plot amplitude in Graphs. A round-trip inverse residual is checked.

Bins represent cycles per complete sample window, not Hz. If sampling frequency is known, Hz = bin × sample rate / N. No sampling rate, leakage/windowing correction, nonuniform sampling, general complex input UI, or DSP toolbox. Values must be finite and have magnitude at most 1e9. Invalid lengths and more than 5,000 input characters are rejected. Offline, no eval or CDN.

Local isolated Chromium numeric/UI harness passed; exact repository Quality/Pages release verification pending.
