# Control Theory Toolbox — Comprehensive Feature Catalog

**Status: PLANNED FEATURE INVENTORY; NOT AN IMPLEMENTATION CLAIM.** Feature names and short descriptions only. Existing Bode, Nyquist, Routh–Hurwitz, sampled root locus and feedback have partial implementations in ProMathStudio; all other individual statuses require an evidence-based audit. This catalog is cross-linked from the engineering workspace plan. Shared math, plotting, signal processing and optimization capabilities must use canonical reusable services, not duplicated discipline-specific implementations.

## Modeling and representation

| Feature | Description |
|---|---|
| Transfer functions | Continuous/discrete SISO and MIMO rational models |
| State-space systems | A, B, C, D and descriptor E representations |
| Zero-pole-gain models | Pole-zero and gain representations |
| Model conversion | State-space, transfer function and zero-pole-gain conversion |
| Block diagrams | Series, parallel, feedback and nested loop reduction |
| Signal-flow graphs | Mason gain formula and loop paths |
| Continuous and discrete time | Time-domain model semantics and conversions |
| Sampled-data and hybrid systems | Mixed continuous/discrete dynamics and event models |
| Time delays | Input, output, transport and computational delays |
| Nonlinear models | Nonlinear state equations and equilibrium points |
| Linearization | Jacobians and operating-point linear models |
| Operating point and trim | Steady-state equilibrium solution |
| Linear parameter-varying models | Scheduled and parameter-dependent dynamics |
| Model interconnection | Subsystem wiring, I/O naming and composition |
| Model simplification | Pole-zero cancellation, minimal realization and model reduction |
| Physical modeling | Mechanical, electrical, fluid and thermal plant primitives |

## Time-domain analysis

| Feature | Description |
|---|---|
| Step response | Time response to step excitation |
| Impulse response | Time response to impulse excitation |
| Ramp and arbitrary input response | Forced responses to user-defined signals |
| Initial condition response | Free response from initial states |
| Rise, settling and peak times | Standard transient metrics |
| Overshoot and undershoot | Transient extrema and percentage metrics |
| Steady-state error | Error constants and reference tracking |
| Time-domain convolution | Impulse-response convolution |
| State trajectories | State-space time histories |
| Phase portraits | Nonlinear and linear phase-plane plots |
| Response comparison | Open/closed-loop and multiple-design overlays |
| Disturbance rejection | Output response to disturbances |
| Noise response | Measurement-noise propagation |
| Actuator and sensor limits | Saturation, deadband, hysteresis and rate limits |
| Nonlinear simulation | Numerical time integration and events |

## Frequency-domain analysis

| Feature | Description |
|---|---|
| Bode diagrams | Magnitude and phase versus frequency |
| Nyquist diagrams | Complex loop frequency response and encirclement |
| Nichols charts | Gain-phase frequency plots |
| Black diagrams | Complex gain/phase locus representation |
| Frequency response estimation | Empirical FRF from sampled signals |
| Pole-zero maps | Continuous and discrete pole/zero diagrams |
| Root locus | Closed-loop poles versus gain |
| Root locus branch tracking | Branch matching and breakaway visualization |
| Gain and phase margins | Crossover frequencies and stability margins |
| Delay and disk margins | Time-delay tolerance and multivariable robustness |
| Bandwidth and resonant peak | Closed-loop frequency performance |
| Sensitivity and complementary sensitivity | S and T frequency functions |
| Loop shaping | Desired open-loop response design |
| Singular value plots | MIMO frequency response singular values |
| MIMO interaction | Relative gain array and decoupling analysis |
| Frequency weighting | Weighted performance and uncertainty curves |
| Frequency-domain comparison | Overlays, cursors and annotations |

## Stability and system properties

| Feature | Description |
|---|---|
| Routh–Hurwitz | Polynomial stability test and first-column analysis |
| Jury criterion | Discrete-time polynomial stability test |
| Schur–Cohn criterion | Discrete stability conditions |
| Nyquist stability criterion | Encirclement and unstable-pole counting |
| Bode stability criterion | Frequency margin interpretation |
| Lyapunov stability | Lyapunov functions and matrix equations |
| Hurwitz and Schur eigenvalue checks | Continuous and discrete pole regions |
| Controllability | Controllability matrix and rank |
| Observability | Observability matrix and rank |
| Minimal realization | Remove unreachable or unobservable states |
| Stabilizability and detectability | Weaker control/observation properties |
| Modal analysis | Eigenvalues, eigenvectors, damping and natural frequency |
| Dominant pole approximation | Reduced-order transient estimation |
| Root sensitivity | Pole motion with parameter changes |
| Robust stability | Stability across parameter uncertainty |
| Absolute stability | Sector conditions and circle/Popov criteria |

## Classical controller design

| Feature | Description |
|---|---|
| P controller | Proportional feedback design |
| PI controller | Proportional-integral feedback design |
| PD controller | Proportional-derivative feedback design |
| PID controller | PID and derivative filtering |
| Two-degree-of-freedom PID | Reference weighting and separate disturbance shaping |
| Anti-windup | Integrator clamping and back calculation |
| Bumpless transfer | Smooth controller mode changes |
| PID tuning | Ziegler–Nichols, Cohen–Coon and model-based tuning |
| Lead compensator | Phase lead network design |
| Lag compensator | Phase lag network design |
| Lead-lag compensator | Combined phase compensation |
| Notch and resonant controllers | Frequency-selective disturbance suppression |
| Feedforward control | Reference and measured-disturbance compensation |
| Cascade control | Nested inner/outer loops |
| Ratio and split-range control | Process control configurations |
| Gain scheduling | Parameter-dependent controller gains |
| Decoupling control | Cross-coupling compensation |
| Smith predictor | Delay compensation |
| Internal model control | IMC design and tuning |
| Pole placement | Closed-loop pole assignment |
| Reference prefilter | Setpoint shaping |
| Controller comparison | Performance and effort trade-off charts |

## Modern state-space control

| Feature | Description |
|---|---|
| State feedback | Full-state feedback control |
| Reference tracking | Precompensators and integral augmentation |
| LQR | Linear quadratic regulator design |
| LQI | Integral-augmented quadratic regulator |
| LQG | Linear quadratic Gaussian design |
| Kalman filter | State estimation with process/measurement noise |
| Extended Kalman filter | Nonlinear state estimation via linearization |
| Unscented Kalman filter | Sigma-point nonlinear estimation |
| Luenberger observer | Deterministic state observer |
| Reduced-order observer | Observer with partial-state reconstruction |
| Unknown-input observer | State estimation under unknown disturbances |
| Servo control | Command tracking with disturbance rejection |
| H2 control | Optimal stochastic performance |
| H-infinity control | Worst-case robust performance synthesis |
| Mixed sensitivity design | Weighted robust feedback synthesis |
| Mu analysis and synthesis | Structured uncertainty robustness |
| Loop transfer recovery | Observer/controller robustness recovery |
| Eigenstructure assignment | Pole and eigenvector shaping |
| MIMO pole placement | Multivariable state feedback |
| Descriptor systems | Generalized state-space analysis |

## Digital control

| Feature | Description |
|---|---|
| Sampling and zero-order hold | Discrete equivalents and sampling artifacts |
| Discretization | ZOH, Tustin, matched pole-zero and Euler methods |
| Z transform | Forward/inverse Z and rational algebra |
| Difference equations | Discrete recurrence modeling |
| Discrete PID | Position and velocity forms |
| Digital filters | Controller filtering and implementation |
| Quantization and fixed point | Finite word-length and overflow |
| Computational delay | Timing and latency effects |
| Sample-rate selection | Aliasing and closed-loop bandwidth |
| Multi-rate control | Different sensor and actuator rates |
| Event-triggered control | Event-driven controller updates |
| Discrete stability | Unit-circle and Jury analysis |
| Digital controller code export | Generated reference code for implementation |

## Optimization, predictive and advanced control

| Feature | Description |
|---|---|
| Model predictive control | Constrained receding-horizon control |
| Linear MPC | Quadratic-program predictive design |
| Nonlinear MPC | Nonlinear predictive optimization |
| Explicit MPC | Precomputed piecewise controller policies |
| Constrained control | State, input and output limits |
| Optimal control | Finite/infinite horizon optimization |
| Pontryagin principle | Hamiltonian optimality conditions |
| Dynamic programming | Bellman recursion and policies |
| Trajectory optimization | Direct shooting and collocation |
| Adaptive control | Online parameter-dependent controllers |
| MRAC | Model-reference adaptive control |
| Self-tuning regulators | Online identification and controller update |
| Sliding mode control | Switching surfaces and chattering analysis |
| Backstepping | Recursive nonlinear controller construction |
| Feedback linearization | Input-output and state linearization |
| Passivity-based control | Energy and passivity design |
| Fuzzy control | Rule-based fuzzy controllers |
| Neural and learning control | Data-driven control policy models |
| Reinforcement learning control | Learned policy with constraints |
| Iterative learning control | Repeated-task error learning |
| Fractional-order control | Non-integer-order dynamics and PID |

## Identification and estimation

| Feature | Description |
|---|---|
| System identification | Plant models from measured input/output data |
| ARX, ARMAX and OE models | Parametric discrete identification |
| Box–Jenkins models | Separate process and noise dynamics |
| Subspace identification | State-space realization from data |
| Frequency-domain identification | Fit frequency response models |
| Parameter estimation | Least-squares and nonlinear estimation |
| Recursive least squares | Online parameter estimation |
| Experiment design | Excitation and identification quality |
| Model validation | Residuals, cross-validation and fit |
| Sensor fusion | Combine multiple measurement sources |
| Disturbance observers | Estimate and reject unknown disturbances |
| Fault detection and isolation | Residual-based anomaly and fault diagnostics |

## Robustness, uncertainty and safety

| Feature | Description |
|---|---|
| Uncertain parameters | Interval, statistical and structured variations |
| Monte Carlo closed-loop analysis | Performance distributions across uncertainty |
| Sensitivity analysis | Parameter and model sensitivity |
| Worst-case analysis | Worst-case margins and responses |
| Structured singular value | Mu robust-performance analysis |
| Gain/phase uncertainty | Loop uncertainty models |
| Actuator faults and saturation | Failure modes and safe fallback |
| Sensor faults and noise | Faulty measurement behavior |
| Safety constraints | State and output envelope checks |
| Stability certificates | Evidence and assumptions for stability claims |
| Controller validation | Nominal, boundary and adversarial test cases |

## Simulation, workflows and interoperability

| Feature | Description |
|---|---|
| Interactive control block editor | Visual plant/controller interconnection |
| Simulation solver settings | Step sizes, tolerances and events |
| Parameter sweeps | Batch response comparison |
| Control design workspace | Models, controllers, signals and plots together |
| Tuning dashboard | Interactive gains, poles and margins |
| Engineering units | Unit-aware model parameters and outputs |
| Reusable plant library | Mechanical, electrical, thermal, fluid and aerospace examples |
| Data import/export | CSV, JSON and model data interchange |
| MATLAB/Octave interchange | Model and dataset import/export where supported |
| Python and SciPy interoperability | Compatible models and numerical results |
| FMU/FMI interoperability | Co-simulation and functional mockup units |
| Code generation | C/C++/Python controller reference export |
| Hardware-in-the-loop interfaces | Real-time hardware simulation hooks |
| Software-in-the-loop validation | Controller software against simulated plants |
| Real-time monitoring | Live telemetry and control dashboards |
| Plots and reporting | Reproducible control-system reports |
| Examples and tutorials | Canonical control engineering examples |
| Numerical diagnostics | Residuals, conditioning, tolerances and warnings |

**Catalog size:** 181 feature entries across 11 groups. Entries overlap the prior 166-gap audit and six engineering disciplines; do not add counts as unique features. Detailed implementation status is pending.
