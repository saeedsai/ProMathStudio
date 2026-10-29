# Electromagnetics & Electromagnetic Engineering Toolbox — Feature Catalog

**Status: PLANNED ONLY.** This is a separate selectable toolbox in the ProMathStudio Engineering Toolbox workspace. Feature names and concise descriptions only. Coverage includes Maxwell fields, electrostatics, magnetostatics, induction, waves, RF/microwave, antennas, EMC/EMI, numerical electromagnetics, photonics, electromechanics and measurement. Reuse canonical shared math, vector calculus, PDE, numerical solvers, material models, signal processing, plotting and optimization rather than duplicating code. Individual implementation status requires a future source-and-test audit.

## Electromagnetic fundamentals and mathematics

| Feature | Description |
|---|---|
| Maxwell equations | Differential and integral field equations |
| Vector calculus operators | Gradient, divergence, curl and Laplacian |
| Coordinate systems | Cartesian, cylindrical and spherical EM coordinates |
| Electromagnetic units | SI field quantities and unit conversion |
| Constitutive relations | Permittivity, permeability and conductivity |
| Boundary conditions | Interface conditions for E, D, B and H |
| Charge and current distributions | Point, line, surface and volume sources |
| Potential formulations | Scalar and vector electromagnetic potentials |
| Green functions | Source-to-field integral kernels |
| Electromagnetic energy | Energy density, Poynting vector and conservation |
| Lorentz force | Forces on charges and current elements |
| Dimensional and scaling analysis | Characteristic EM length, time and frequency |

## Electrostatics and dielectrics

| Feature | Description |
|---|---|
| Coulomb law | Fields from static point charges |
| Electric field solver | Field and potential from source distributions |
| Gauss law | Electric flux and enclosed charge |
| Poisson and Laplace equations | Electrostatic potential boundary problems |
| Capacitance extraction | Capacitance matrices and parasitic capacitance |
| Dielectric polarization | Bound charges and dielectric response |
| Dielectric interfaces | Fields across dielectric boundaries |
| Electrostatic forces | Maxwell stress and energy methods |
| Electrostatic shielding | Conductive enclosures and field suppression |
| Breakdown and insulation | Electric stress and dielectric withstand |
| Electrostatic discharge | ESD event and charge-transfer models |
| High-voltage field grading | Electrode geometry and field concentration |

## Magnetostatics and magnetic circuits

| Feature | Description |
|---|---|
| Biot–Savart law | Magnetic fields from currents |
| Ampere law | Magnetic circulation and currents |
| Magnetic vector potential | Magnetostatic field formulation |
| Magnetic flux and linkage | Flux integrals and coil linkage |
| Inductance extraction | Self and mutual inductance |
| Magnetic circuit networks | Reluctance, MMF and flux |
| Magnetic materials | B–H curves and permeability |
| Magnetic hysteresis | Core loss and hysteretic behavior |
| Saturation analysis | Nonlinear ferromagnetic response |
| Eddy currents | Induced current distribution and losses |
| Magnetic forces and torque | Energy and Maxwell stress calculations |
| Permanent magnets | Remanence and magnet field modeling |
| Transformers and inductors | Core, winding and leakage calculations |

## Time-varying fields and induction

| Feature | Description |
|---|---|
| Faraday induction | EMF from changing magnetic flux |
| Displacement current | Time-varying electric field contribution |
| Skin effect | Frequency-dependent conductor penetration |
| Proximity effect | Current redistribution near conductors |
| Diffusion in conductors | Magnetic diffusion and transients |
| Inductive coupling | Coupling between coils and circuits |
| Capacitive coupling | Electric-field coupling between conductors |
| Electromagnetic transients | Time-domain field response |
| Quasi-static approximation | Validity of electro- and magneto-quasistatics |
| Transient eddy-current analysis | Time-dependent conductor losses |
| Wireless power transfer | Resonant inductive power coupling |
| Induction heating | Eddy-current thermal source modeling |

## Wave propagation and field theory

| Feature | Description |
|---|---|
| Wave equation | Electromagnetic propagation models |
| Plane waves | Polarization, impedance and propagation |
| Spherical and cylindrical waves | Radiation and guided propagation |
| Polarization analysis | Linear, circular and elliptical polarization |
| Reflection and transmission | Fresnel coefficients and interfaces |
| Snell law | Refraction and critical angles |
| Standing waves | Interference and resonance |
| Lossy media propagation | Attenuation and phase constants |
| Dispersion | Frequency-dependent propagation |
| Group and phase velocity | Signal and wave velocities |
| Waveguides | Rectangular, circular and dielectric modes |
| Resonant cavities | Eigenmodes and quality factor |
| Scattering parameters | S-parameter frequency response |
| EM field visualization | Vector fields, energy flow and animation |

## Transmission lines and microwave engineering

| Feature | Description |
|---|---|
| Telegrapher equations | Distributed RLCG line models |
| Characteristic impedance | Line impedance and propagation constant |
| Transmission line matching | Stub, quarter-wave and transformer matching |
| Smith chart | Impedance and admittance matching |
| Reflection coefficient and VSWR | Mismatch and standing-wave metrics |
| Coaxial and microstrip lines | Transmission line geometry calculations |
| Stripline and coplanar waveguides | Planar transmission structures |
| Loss and dispersion | Conductor and dielectric line losses |
| Two-port networks | ABCD, Z, Y and S parameters |
| Microwave filters | Distributed and lumped RF filtering |
| Power dividers and couplers | Directional and passive RF networks |
| Resonators | Microwave cavity and planar resonators |
| Waveguide discontinuities | Junction and bend behavior |
| Microwave network optimization | Frequency-domain matching and tuning |

## Antennas and radiation

| Feature | Description |
|---|---|
| Dipole and monopole antennas | Basic wire antenna radiation |
| Loop and patch antennas | Small loop and microstrip radiators |
| Antenna arrays | Array factors and element positioning |
| Phased arrays | Electronic beam steering |
| Radiation patterns | 2D and 3D angular patterns |
| Antenna gain and directivity | Radiation intensity metrics |
| Antenna impedance and matching | Feed impedance and bandwidth |
| Polarization mismatch | Polarization coupling and loss |
| Near-field and far-field | Region boundaries and transformations |
| Link budget | Free-space loss and received power |
| Radar cross section | Scattering strength and angular response |
| Beamforming | Weights, steering vectors and sidelobes |
| Mutual coupling | Element-to-element antenna interactions |
| Antenna measurement processing | Pattern, gain and S-parameter data |

## EMC, EMI and signal integrity

| Feature | Description |
|---|---|
| Conducted emissions | Noise propagating through wiring |
| Radiated emissions | Unwanted field radiation |
| Conducted immunity | Susceptibility to injected disturbances |
| Radiated immunity | Susceptibility to incident fields |
| Shielding effectiveness | Electric and magnetic shielding |
| Grounding and bonding | Return paths and impedance |
| Crosstalk | Near-end and far-end coupling |
| PCB signal integrity | Trace reflections and impedance |
| Power integrity | PDN impedance and supply noise |
| Cable and connector coupling | Harness and connector emissions |
| ESD and EFT | Transient interference scenarios |
| Surge and lightning coupling | High-energy transient coupling |
| EMC filters | Common-mode and differential-mode filtering |
| Pre-compliance analysis | Measurement limits and frequency scans |
| Spectrum and interference analysis | Spectral occupancy and interference |

## Computational electromagnetics

| Feature | Description |
|---|---|
| Finite-difference time-domain | FDTD field propagation solver |
| Finite-element electromagnetics | FEM electrostatic and full-wave solvers |
| Method of moments | MoM integral-equation analysis |
| Finite integration technique | Discrete Maxwell field formulation |
| Boundary-element methods | BEM field and scattering solutions |
| Transmission line matrix method | TLM electromagnetic solver |
| Eigenmode analysis | Resonant frequency and field modes |
| Meshing and geometry | Field-domain discretization |
| Material assignment | Spatially varying constitutive properties |
| Boundary and port conditions | PEC, PMC, radiation and wave ports |
| Absorbing boundaries and PML | Open-domain numerical boundaries |
| Adaptive refinement | Error-driven mesh refinement |
| Solver convergence | Residuals, stability and error estimates |
| Frequency sweeps | Multi-frequency EM response |
| Time-domain simulation | Transient EM field computation |
| Multiphysics coupling | EM-thermal and EM-mechanical interaction |
| Postprocessing and field probes | Sample, integrate and export field data |

## Materials, optics and photonics

| Feature | Description |
|---|---|
| Complex permittivity | Frequency-dependent dielectric response |
| Complex permeability | Lossy magnetic media response |
| Conductivity and resistivity | Temperature-dependent conductor properties |
| Anisotropic materials | Tensor electromagnetic properties |
| Metamaterials | Effective electromagnetic parameters |
| Ferrites and gyrotropic media | Bias-dependent nonreciprocal response |
| Superconductors | Simplified superconducting field models |
| Optical waveguides | Guided optical modes |
| Fiber optics | Fiber propagation and attenuation |
| Photonic crystals | Periodic optical structures |
| Plasmonics | Surface plasmon propagation |
| Optical interference and diffraction | Coherent optical field behavior |
| Electro-optic effects | Field-dependent refractive index |

## Electromechanical, energy and sensing applications

| Feature | Description |
|---|---|
| Electric machine fields | Motor and generator flux distributions |
| Magnetic actuators | Solenoid and relay forces |
| Inductive sensors | Inductance and coupling measurements |
| Capacitive sensors | Electric field sensing |
| Hall and magnetoresistive sensors | Magnetic field transduction |
| EM flow meters | Electromagnetic flow sensing |
| Nondestructive testing | Eddy-current inspection signals |
| Wireless charging | Coil alignment and efficiency |
| Electromagnetic braking | Eddy-current torque and loss |
| Electromagnetic levitation | Magnetic force and stability |
| Transformer field design | Leakage flux and winding forces |
| Thermal losses | Joule, dielectric and magnetic heating |

## Measurement, visualization and workflow

| Feature | Description |
|---|---|
| Field probes and measurements | Electric and magnetic field acquisition |
| VNA data import | Touchstone S1P/S2P/SnP processing |
| Spectrum analyzer data import | Frequency-domain measurement datasets |
| Antenna pattern import | Radiation measurement formats |
| EM field maps | Scalar, vector and streamline visualization |
| 3D field animations | Time-varying E, H and power flow |
| Parameter sweeps | Geometry, material and frequency variation |
| Optimization and sensitivity | Field-based design optimization |
| Uncertainty analysis | Tolerances and measurement error |
| Standards metadata | EMC and exposure standard references |
| Safety and exposure metrics | SAR, power density and field limits |
| Model validation | Analytic reference and measured comparison |
| Reports and reproducibility | Documented assumptions and results |
| CAD geometry interoperability | Import and export supported geometry |
| Python interoperability | Shared numerical data and model exchange |

**Catalog size:** 163 feature entries across 12 categories. These overlap existing electrical, electronics, physics, aerospace and signal engineering catalogs; do not add them as independent unique feature counts. Field and safety results must specify units, coordinate frames, frequency/time assumptions, material properties, boundary conditions, solver accuracy and relevant standard editions where applicable.
