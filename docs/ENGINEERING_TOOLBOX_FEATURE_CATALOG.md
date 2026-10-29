**Cryptography & Security (ninth planned discipline):** [145-feature cryptography catalog](CRYPTOGRAPHY_SECURITY_TOOLBOX_FEATURE_LIST.md), including cryptographic mathematics, hashes, keys, encryption, digital signatures, PKI, protocols, post-quantum and validation. Reuse shared services; no production primitives from scratch.

**Signal Engineering & Processing (eighth planned discipline):** [177-feature signal catalog](SIGNAL_ENGINEERING_TOOLBOX_FEATURE_LIST.md) covering signal types, synthesis, acquisition, reading/decoding, coding, filtering, transforms, statistics, detection and visualization. Share algorithms with Control, GNSS, Electronics and other disciplines.

**GNSS & Positioning (seventh planned discipline):** [144-feature GPS, observation and position-estimation catalog](GNSS_POSITIONING_OBSERVATION_TOOLBOX_FEATURE_LIST.md). Covers GNSS measurements, geodesy, precise positioning, sensor fusion, integrity and simulation; shares underlying mathematics with the six existing engineering disciplines.

**Control Theory:** [181-feature comprehensive catalog](CONTROL_THEORY_TOOLBOX_FEATURE_LIST.md) covering classical, modern, digital, robust, nonlinear, predictive, identification and simulation capabilities. It is cross-disciplinary and not counted as 181 additional unique tools.

# Engineering Toolboxes — Future Feature Catalog

**Status: PLANNED / NOT IMPLEMENTED BY THIS CHANGE.** Derived from six user-supplied Markdown feature lists (2026-10-29). This catalog stores **feature names and short descriptions only**, not instructions, implementation plans, code, technology choices or launch sequences. Sections are broad feature families; each original source also contains finer-grained subfeatures that must be preserved during subsequent detailed backlog ingestion. Existing capabilities require independent audit before marking any item implemented. The separate 19-item electrical/electronics backlog and control-theory roadmap remain active references; deduplicate overlapping functionality when implementing, without dropping requested scope.

## Physics

| Feature | Description |
|---|---|
| Scientific calculator and mathematics | Scientific, complex, arbitrary-precision and special-function calculations |
| Symbolic mathematics | Algebra, calculus, transforms, differential equations and symbolic verification |
| Numerical analysis | Roots, integration, interpolation, sparse methods and numerical error |
| Differential equations and boundary problems | ODE, DAE, PDE, finite-element, finite-volume and spectral solvers |
| Linear algebra and tensor calculus | Decompositions, eigenproblems, tensor fields and index notation |
| Calculus and differential geometry | Vector calculus, variational methods, manifolds, geodesics and curvature |
| Classical mechanics | Rigid-body, Lagrangian/Hamiltonian, orbital and nonlinear dynamics |
| Electromagnetism | Electrostatics, Maxwell fields, waves, antennas and numerical EM |
| Waves, acoustics, optics and photonics | Propagation, diffraction, lasers, polarization and photonic systems |
| Thermodynamics and heat transfer | Thermal processes and energy transport |
| Statistical mechanics and stochastic physics | Ensembles, stochastic systems and statistical models |
| Quantum mechanics and quantum information | Wavefunctions, operators, quantum systems and information |
| Relativity | Special/general relativity and spacetime geometry |
| Nuclear and particle physics | Nuclear reactions, particles and related models |
| Condensed matter and solid-state physics | Material and solid-state phenomena |
| Fluid, plasma and continuum physics | Continuum flows, plasmas and multiphysics |
| Astrophysics, astronomy and cosmology | Celestial and cosmological models |
| Atomic, molecular and chemical physics | Atomic/molecular structure and interactions |
| Chaos, nonlinear dynamics and complex systems | Bifurcations, chaos and complex-system behavior |
| Simulation and high-performance computing | General numerical simulation and accelerated computation |
| Experimental physics and statistical data analysis | Measurement processing, fitting and statistics |
| Optimization and inverse problems | Parameter estimation, optimization and inverse models |
| Scientific graphing | 2D/3D, field, tensor and time-dependent visualization |
| Units and physical constants | Dimensional consistency and physical reference data |
| Specialist physics toolboxes | Domain-specific scientific workflows |
| Scientific notebook and reporting | Research workspaces and reproducible reporting |
| AI-assisted physics | Assisted equations, analysis and explanation |

## Mechanical Engineering

| Feature | Description |
|---|---|
| Statics and rigid-body mechanics | Force resultants, equilibrium, supports, centroids and trusses |
| Strength of materials | Stress, strain, beam deflection, buckling and failure criteria |
| Fatigue, fracture and durability | Fatigue life, crack growth and reliability |
| Machine design and rotating parts | Shafts, bearings, balancing, brakes and rotordynamics |
| Gears and power transmission | Gear trains, belts, chains and contact stress |
| Fasteners, joints, springs and fits | Bolts, welds, springs and tolerance analysis |
| Kinematics and mechanisms | Linkages, cams, trajectories and robot kinematics |
| Dynamics and multibody mechanics | Newton–Euler, impact, constrained motion and coupled systems |
| Vibration, modal analysis and NVH | Natural frequencies, modes and vibration response |
| Thermodynamics | Cycles, states and thermophysical analysis |
| Heat transfer | Conduction, convection, radiation and thermal design |
| Fluid mechanics and piping | Pipe losses, hydraulic networks and flow |
| Turbomachinery | Pumps, compressors, fans and turbines |
| HVAC and refrigeration | Cooling, ventilation and building mechanical systems |
| Materials selection and testing | Material properties and mechanical characterization |
| Manufacturing and process engineering | Process design and production calculations |
| Control, automation and mechatronics | Mechanical feedback and electromechanical systems |
| Finite-element structural analysis | Structural meshing, loading and FEA results |
| CFD and thermal simulation | Computational flow and heat transfer |
| System simulation and digital twins | Dynamic models and system-level simulation |
| Optimization, uncertainty and reliability | Design optimization and robustness |
| Specialty mechanical applications | Specialized mechanical engineering design |
| Test engineering and metrology | Measurement, calibration and diagnostics |
| Standards and design verification | Engineering checks and reproducible technical reports |

## Electrical Engineering

| Feature | Description |
|---|---|
| Core mathematics | Complex, symbolic, numerical and transform tools |
| Scientific visualization | Bode, Nyquist, phasors, Smith charts and signals |
| Basic electrical calculators | Ohm, RLC, power, transformer and cable sizing |
| Circuit and network analysis | Schematic capture, MNA, SPICE and transients |
| Analog electronics | Amplifiers, filters, oscillators and semiconductor bias |
| Digital electronics and logic | Logic minimization, timing and digital simulation |
| Signal processing | FFT, spectral analysis, digital filters and identification |
| Control systems | Transfer functions, feedback, root locus and controllers |
| Electromagnetics and field theory | Electric/magnetic fields and field solvers |
| Power systems and grids | Load flow, faults, protection and networks |
| Electrical machines and drives | Motors, generators and variable-speed drives |
| Power electronics | Converters, switching and converter controls |
| RF, microwave and antennas | Transmission lines, matching and radiation |
| Telecommunications | Modulation, coding and communications systems |
| Renewable energy and batteries | PV, wind, storage and energy systems |
| PCB, cabling and hardware | Interconnects, signal integrity and physical design |
| Instrumentation and metrology | Sensors, measurement and uncertainty |
| Reliability, safety and optimization | Design margins, risk and optimization |

## Electronics Engineering

| Feature | Description |
|---|---|
| Core numerical mathematics | Electronic math, precision and unit conversion |
| DC circuits | Ohm, Kirchhoff, nodal, mesh and network equivalents |
| AC and network theory | Phasors, RLC, two-port networks and transients |
| Schematic and circuit simulation | SPICE, sweeps, noise and convergence |
| Passive components | RLC parasitics, selection and derating |
| Analog electronics | Transistor bias, amplifiers, op-amps and oscillators |
| Semiconductor physics | PN junctions, MOSFETs, materials and device models |
| Digital logic and computer arithmetic | Logic, FSM, fixed point and timing |
| Digital signal processing | FFT, spectra, FIR/IIR, sampling and code export |
| Analog filters | Filter topology, synthesis and frequency response |
| ADC, DAC and mixed signal | Converter characteristics and mixed-signal interfaces |
| RF and wireless electronics | RF networks, microwave and wireless front ends |
| Power electronics and management | Power conversion, regulation and protection |
| Control systems for electronics | Feedback and embedded controller analysis |
| Embedded electronics | Interface timing, microcontroller and peripheral signals |
| PCB, signal integrity and EMC | Board-level interconnect and electromagnetic compatibility |
| Electromagnetics and sensors | Fields and sensing devices |
| Optoelectronics and photonics | LEDs, photodiodes and optical components |
| Communications engineering | Modulation, coding and links |
| IC and VLSI mathematics | Integrated circuit design and timing |
| Thermal, reliability and tolerances | Thermal design and statistical margins |
| Measurement and lab analysis | Instrument data and experiments |
| Optimization and design automation | Automated parameter selection and sweeps |
| Interactive visualization | Plots, waveforms and circuit diagrams |
| Integrated workspaces | Linked electronics analysis workbenches |

## Fluid Mechanics

| Feature | Description |
|---|---|
| Engineering mathematics | Fluid-specific numerical and symbolic methods |
| Units and dimensions | Pressure, flow, viscosity and dimensionless groups |
| Fluid properties and thermodynamics | Property correlations, mixtures and phase states |
| Fundamental fluid mechanics | Continuity, momentum, energy and Navier–Stokes |
| Hydrostatics | Pressure, buoyancy and hydrostatic loads |
| Internal pipe and duct flow | Friction, Moody charts, losses and sizing |
| Hydraulic networks | Pumps, valves, networks and flow balances |
| External flow and aerodynamics | Boundary layers, drag, lift and wake |
| Compressible flow | Isentropic, shock, nozzle and gas flow |
| Turbomachinery | Pump, compressor and turbine performance |
| Heat and mass transfer | Convection, exchangers and transport |
| Open-channel hydraulics | Manning, hydraulic jumps and channels |
| Multiphase and non-Newtonian flow | Two-phase pressure loss, rheology and slurries |
| Transient fluid systems | Water hammer, surge and dynamic pipes |
| Turbulence | Turbulence models and turbulent-flow analysis |
| CFD fundamentals | Discretization, meshing and numerical flow solvers |
| Advanced CFD and multiphysics | Coupled flow, heat and multiphase simulations |
| Numerical methods | Solvers, convergence and error controls |
| Visualization | Streamlines, contours and field animation |
| Design optimization | Fluid-system sizing and optimization |
| Experimental fluid mechanics | Flow measurements and uncertainty |
| Dedicated engineering calculators | Domain-specific quick calculations |
| Automation, integration and reporting | Reusable engineering workflows |

## Aerospace Engineering

| Feature | Description |
|---|---|
| Core symbolic mathematics | Equation, calculus and transform solvers |
| Linear algebra | Matrices, tensors and decompositions |
| Numerical scientific computing | ODE, PDE, interpolation and optimization |
| Scientific visualization | 2D/3D, trajectories and aerodynamic plots |
| Statistics and data analysis | Uncertainty, Monte Carlo and experimental data |
| Atmosphere and environment | ISA, gravity, wind and turbulence |
| Aerodynamics | Airfoils, lifting line, VLM, shocks and CFD |
| Flight mechanics and performance | 3/6-DOF, trim, climb, cruise, takeoff and landing |
| Flight stability and control | Aircraft modes, stability derivatives and autopilots |
| Control theory | Transfer functions, root locus, Bode and design |
| Propulsion and thermodynamics | Engines, propulsion cycles and performance |
| Structures and materials | Aircraft stress, fatigue and aero-structures |
| Orbital mechanics and astrodynamics | Orbits, transfers and perturbations |
| Spacecraft attitude dynamics | Spacecraft rotations, actuators and attitude control |
| Rotorcraft, UAV and VTOL | Rotor and unmanned aircraft models |
| Hypersonics and reentry | High-Mach and thermal reentry analysis |
| Avionics, sensors and navigation | Sensor, estimation and navigation models |
| Guidance and trajectory optimization | Guidance laws and optimal trajectories |
| Preliminary aircraft/spacecraft design | Mass, sizing and configuration tradeoffs |
| Optimization and design exploration | Multi-objective design studies |
| Simulation and system modeling | Dynamic aerospace simulation |
| Signal processing and identification | Spectra, estimation and model identification |
| Uncertainty, reliability and safety | Reliability, failure and sensitivity analysis |
| Aeroelasticity | Coupled structural and aerodynamic response |
| Engineering units and reference data | Aerospace constants and standards |
| Equation editor and notebook | Connected aerospace calculations |
| Engineering data workspace | Data import, analysis and visualization |
| Programming and interoperability | Scientific APIs and data interchange |
| Reporting and traceability | Engineering reports and reproducibility |
| AI engineering assistant | Assisted engineering analysis |
| Quick aerospace calculators | Fast flight/atmosphere/orbit calculations |

## Source files

- `Physics_Software_Complete_Feature_List.md`
- `Mechanical_Engineering_Tools_Complete_Feature_List.md`
- `Electronics_Engineering_Tool_Full_Feature_List.md`
- `Aerospace_Engineering_Full_Feature_List.md`
- `Fluid_Mechanics_Engineering_Features.md`
- `Electrical_Engineering_Toolbox_Feature_List.md`

**Deferred:** This is a planning-only feature-family catalog; the original uploaded documents contain additional individual feature entries and are not fully replicated here. Do not interpret the summary as the exhaustive individual-feature matrix or as evidence of implemented functionality.
