# Offline real-signal FFT — development candidate

Open **Symbolic solver → Signal spectrum · offline FFT**. Enter 4–256 uniformly sampled real values, with a power-of-two length, separated by commas or whitespace. Example: 0, 1, 0, -1, 0, 1, 0, -1 yields bin 2 with amplitude 1. Eight samples of 3 produce DC amplitude 3. Alternating +1/-1 produces Nyquist amplitude 1.

The forward radix-2 DFT uses a negative exponential; inverse uses positive exponential and 1/N scaling. One-sided amplitude is |X[k]|/N at DC and Nyquist and 2|X[k]|/N for interior bins. Output includes bin, amplitude, phase (radians), raw real and imaginary DFT values. Save to Data Tables or plot amplitude in Graphs. A round-trip inverse residual is checked.

Set a positive sample rate (default 8 Hz) to convert bin k to frequency in Hz = k × sample rate / N. FFT also shows the bin width (rate/N) and Nyquist frequency (rate/2). Blank, nonnumeric and boolean rates are invalid. Data Tables export includes frequency_Hz and Graphs plots frequency_Hz against amplitude. No leakage/windowing correction, nonuniform sampling, general complex input UI, or DSP toolbox. Values must be finite and have magnitude at most 1e9. Invalid lengths and more than 5,000 input characters are rejected. Offline, no eval or CDN.

Local isolated Chromium numeric/UI harness passed; exact repository Quality/Pages release verification pending.
