# Signal Engineering & Processing Toolbox — Comprehensive Feature Catalog

**Status: PLANNED ONLY; this is not a claim of implemented functionality.** Feature names and concise descriptions only. This is a distinct selectable toolbox within the Engineering Toolbox workspace, with shared math/FFT/filter/estimation/visualization services used across electrical, electronics, aerospace, control, GNSS and physics. Includes analog/digital, continuous/discrete, real/complex and multidimensional signals; signal generation, acquisition, reading/decoding, coding, filtering, analysis and processing.

## Signal types and representations

| Feature | Description |
|---|---|
| Continuous-time signals | Analog signals defined over continuous time |
| Discrete-time signals | Sequences indexed by sample |
| Digital and quantized signals | Amplitude-quantized sampled signals |
| Real and complex signals | Real-valued and I/Q complex representations |
| Deterministic and random signals | Predictable and stochastic signal models |
| Periodic and aperiodic signals | Repetitive and non-repetitive waveforms |
| Stationary and nonstationary signals | Time-varying statistical behavior |
| Transient and steady-state signals | Short-lived and sustained components |
| Scalar, vector and multichannel signals | Single and multi-axis measurements |
| 1D, 2D and multidimensional signals | Time series, images and higher-dimensional arrays |
| Event, pulse and spike signals | Sparse events and impulse sequences |
| Audio, vibration and acoustic signals | Sound and structural motion data |
| Electrical and biomedical signals | Voltage/current and ECG/EEG/EMG measurements |
| RF, radar, sonar and navigation signals | Carrier-based and ranging signals |
| Optical, image and video signals | Light, pixel and frame sequences |

## Signal creation and synthesis

| Feature | Description |
|---|---|
| Standard waveform generator | Sine, cosine, square, triangle, sawtooth and pulse |
| Impulse, step and ramp generator | Canonical system test excitations |
| Chirp and frequency sweep | Linear, logarithmic and custom sweeps |
| Multitone and harmonic synthesis | Signals with multiple spectral components |
| Noise generation | White, pink, colored and impulsive noise |
| Random process synthesis | Correlated and distribution-controlled sequences |
| Arbitrary waveform generator | Expression- and sample-defined waveforms |
| Modulated signal generator | AM, FM, PM and digital modulation |
| I/Q baseband generator | Complex envelope and quadrature signals |
| Pulse train and coded waveform | PRBS, Barker and chirped pulses |
| Multichannel signal generation | Synchronized channel synthesis |
| Signal mixture builder | Add noise, drift, offsets and interference |
| Parameter-controlled signal synthesis | Live waveform parameter updates |

## Import, acquisition and decoding

| Feature | Description |
|---|---|
| CSV, TSV and spreadsheet import | Time-stamped and sampled signal tables |
| WAV, FLAC and audio import | Audio waveform decoding |
| Binary sample import | Signed/unsigned integer and floating samples |
| I/Q sample file import | Interleaved complex sample formats |
| MAT, HDF5 and scientific data import | Multidimensional signal datasets |
| EDF/BDF biomedical import | Clinical electrophysiology recordings |
| TDMS and measurement logs | Instrumentation data interchange |
| VCD and logic analyzer import | Digital transitions and timing data |
| NMEA, RINEX and navigation logs | GNSS and positioning signal observations |
| Streaming serial and device capture | Live instrument or sensor inputs |
| Network signal streams | UDP/TCP/WebSocket acquisition where supported |
| Sampling metadata parser | Units, timebase, channels and calibration |
| Channel alignment | Time offset and sample-rate synchronization |
| Timestamp repair | Missing, duplicate and irregular timestamps |
| Trigger and capture controls | Threshold, edge and window triggering |
| Signal format validation | Endianness, scaling, clipping and corruption checks |

## Signal editing and operations

| Feature | Description |
|---|---|
| Trim, split and concatenate | Edit and combine waveform segments |
| Time shifting and scaling | Delay, stretch and compress signals |
| Amplitude scaling and offset | Gain and baseline correction |
| Resampling and interpolation | Convert sampling rates |
| Decimation and upsampling | Multirate signal conversion |
| Convolution and correlation | Linear system and similarity operations |
| Windowing and segmentation | Overlapping and framed analysis |
| Detrending and baseline removal | Remove slow trends and DC offsets |
| Normalization and standardization | Scale to amplitude or statistical range |
| Envelope extraction | Amplitude envelope and analytic signal |
| Peak and event detection | Find transients and thresholds |
| Signal differentiation and integration | Rate and accumulated quantity estimation |
| Signal mixing and arithmetic | Channel sums, products and expressions |
| Complex demodulation | Mix carriers to baseband |
| Signal alignment and synchronization | Cross-correlation and clock drift compensation |
| Missing sample reconstruction | Gap filling and interpolation |

## Transforms and spectral analysis

| Feature | Description |
|---|---|
| Fourier series | Periodic signal harmonic decomposition |
| DFT, FFT and IFFT | Discrete frequency transforms |
| STFT and spectrogram | Windowed time-frequency representation |
| Wavelet transform | Multiresolution time-frequency analysis |
| Continuous wavelet transform | Scalograms and scale-frequency analysis |
| Discrete cosine and sine transforms | Energy compaction transforms |
| Hilbert transform | Analytic signal and instantaneous phase |
| Laplace transform | Continuous-system transform representation |
| Z-transform | Discrete-system transform representation |
| Cepstrum analysis | Echo, pitch and spectral envelope analysis |
| Power spectral density | Welch and periodogram estimates |
| Cross-spectrum and coherence | Relationships between channels |
| Transfer function estimation | Frequency response from input/output data |
| Phase and group delay | Frequency-dependent timing |
| Harmonic and THD analysis | Harmonic distortion and spectral content |
| Spectral leakage and resolution | Window and bin-width diagnostics |
| Time-frequency reassignment | Improved localized spectral representation |
| Bispectrum and higher-order spectra | Non-Gaussian and nonlinear spectral measures |

## Filter design and processing

| Feature | Description |
|---|---|
| FIR filter design | Windowed, equiripple and least-squares filters |
| IIR filter design | Butterworth, Chebyshev, elliptic and Bessel filters |
| Low-pass and high-pass filters | Pass or suppress frequency regions |
| Band-pass and band-stop filters | Isolate or reject frequency bands |
| Notch and comb filters | Reject narrowband or periodic interference |
| All-pass and phase equalization | Modify phase while retaining magnitude |
| Adaptive LMS, NLMS and RLS filters | Online coefficient adaptation |
| Kalman filtering | State-space noise reduction and estimation |
| Median and order-statistic filters | Robust impulsive-noise removal |
| Savitzky–Golay smoothing | Polynomial smoothing and derivatives |
| Wavelet denoising | Threshold-based multiscale denoising |
| Wiener filtering | Minimum mean-square error denoising |
| Matched filtering | Known-pattern detection in noise |
| Multirate and polyphase filters | Efficient rate conversion |
| Filter stability and pole-zero analysis | Numerical and theoretical stability |
| Filter coefficient quantization | Fixed-point sensitivity and overflow |
| Real-time filtering | Streaming stateful signal processing |
| Filter comparison and response plots | Magnitude, phase, impulse and step responses |
| Zero-phase filtering | Forward-backward noncausal processing |

## Statistical and stochastic signal analysis

| Feature | Description |
|---|---|
| Mean, variance and RMS | Basic signal statistics |
| SNR, SINAD and ENOB | Noise and converter performance |
| Crest factor and dynamic range | Peak-to-average and range metrics |
| Autocorrelation and cross-correlation | Temporal similarity and lag |
| Autocovariance and stationarity | Time-dependence of statistical structure |
| Probability density estimation | Histograms and kernel estimates |
| Noise model fitting | Gaussian, Poisson and colored-noise models |
| Outlier and anomaly detection | Unusual signal samples and events |
| Uncertainty propagation | Measurement error in signal outputs |
| Confidence intervals and hypothesis tests | Statistical significance of signal features |
| AR, MA and ARMA modeling | Stochastic time-series processes |
| Spectral estimation methods | Parametric and nonparametric PSD |
| Principal and independent component analysis | Multichannel decomposition |
| Blind source separation | Recover mixed independent sources |
| Change-point detection | Abrupt shifts in signal statistics |

## Digital communications and coding

| Feature | Description |
|---|---|
| Sampling and quantization | ADC/DAC representation and error |
| Pulse-code modulation | PCM coding and reconstruction |
| Companding | A-law and mu-law nonlinear quantization |
| Line coding | NRZ, RZ, Manchester and multilevel codes |
| Source coding and compression | Lossless and lossy signal representations |
| Channel coding | Error detection and correction |
| CRC and checksums | Transmission error detection |
| Hamming, BCH and Reed–Solomon codes | Block error-correcting codes |
| Convolutional and turbo codes | Trellis-based error correction |
| LDPC and polar codes | Modern capacity-approaching coding |
| Interleaving and deinterleaving | Burst error spreading and reversal |
| BPSK, QPSK and QAM modulation | Digital symbol modulation |
| FSK, ASK and PSK modulation | Carrier keying families |
| OFDM and multicarrier modulation | Orthogonal subcarrier transmission |
| Pulse shaping and matched reception | Raised cosine and root-raised cosine filters |
| Carrier recovery and PLL | Frequency/phase synchronization |
| Timing recovery | Symbol clock estimation |
| Equalization | Channel distortion compensation |
| Channel models | AWGN, fading and multipath |
| BER, SER and EVM measurement | Communication quality metrics |
| Constellation and eye diagrams | Digital link visualization |
| Packet framing and decoding | Bitstream to frame parsing |

## Signal detection, estimation and tracking

| Feature | Description |
|---|---|
| Threshold and hypothesis detection | Signal-presence decisions |
| Matched-filter detection | Known waveform detection |
| CFAR detection | Adaptive radar-style detection thresholds |
| Cross-correlation delay estimation | Time-of-arrival difference estimation |
| Frequency and phase estimation | Sinusoid parameter estimation |
| Amplitude and envelope estimation | Signal strength tracking |
| DOA and beamforming | Direction of arrival and array processing |
| MUSIC and ESPRIT | High-resolution spectral/angle estimation |
| State estimation | Kalman, extended and unscented filtering |
| Particle filtering | Non-Gaussian signal tracking |
| Target tracking | Position and velocity estimation from observations |
| System identification | Input-output dynamic model fitting |
| Sensor fusion | Multisensor measurement combination |
| Event classification | Label detected patterns |
| Fault and change detection | Detect signal or sensor degradation |

## Specialized signal domains

| Feature | Description |
|---|---|
| Audio and speech processing | Pitch, formants, enhancement and features |
| Vibration and condition monitoring | Order tracking, envelope and bearing faults |
| Biomedical signal analysis | ECG, EEG, EMG and physiological features |
| Radar signal processing | Range-Doppler, pulse compression and tracking |
| Sonar and underwater acoustics | Beamforming, echo and ranging |
| GNSS signal processing | Correlation, acquisition and tracking loops |
| RF and SDR processing | Complex I/Q, downconversion and channelization |
| Optical signal processing | Photodetector and optical waveform analysis |
| Image and video processing | Spatial and temporal filtering |
| Seismic and geophysical signals | Wave arrivals and spectral analysis |
| Power quality signals | Harmonics, transients and phasors |
| Industrial IoT signals | Sensor streams and equipment telemetry |

## Visualization, automation and deployment

| Feature | Description |
|---|---|
| Oscilloscope and waveform viewer | Time-domain zoom, cursor and triggers |
| Spectrum analyzer | FFT and PSD displays |
| Spectrogram and scalogram viewer | Time-frequency heatmaps |
| Constellation and eye diagrams | Communications signal inspection |
| Filter design dashboard | Coefficients, responses and tuning |
| Multichannel synchronized plots | Linked time axes and cursors |
| Annotation and region selection | Mark events and signal segments |
| Signal processing pipeline editor | Connect reusable operations into workflows |
| Batch processing | Run pipelines over many recordings |
| Live streaming dashboard | Monitor incoming sensor data |
| Export processed signals | CSV, WAV, binary and scientific formats |
| Filter coefficient and code export | Generate C/C++/Python reference coefficients |
| Reproducible signal projects | Save pipeline parameters and metadata |
| Performance and latency profiling | Processing throughput and timing |
| Numerical validation | Reference signals, error bounds and tests |
| Signal examples and tutorials | Documented reference workflows |

**Catalog:** 177 named feature entries in 11 categories. These overlap existing engineering and mathematical catalogs; do not sum as unique new software features. Detailed per-feature implementation status requires an audit. Signal metadata must preserve units, sample rate, timestamps, channel definitions, complex representation and calibration; display assumptions and data quality.
