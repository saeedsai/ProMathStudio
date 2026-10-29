# GNSS, GPS, Observation and Position Estimation Toolbox — Feature Catalog

**Planning only — no functionality implemented by this commit.** Feature names and concise descriptions, grouped by subject. Covers satellite navigation, raw observation processing, precise positioning, inertial navigation, multi-sensor fusion, integrity and mapping. Shared geodesy, matrix solvers, Kalman filters, control, signal processing, plotting and uncertainty engines must be reused across the Engineering Toolbox. This catalog is not a verified inventory of existing implementation.

## GNSS fundamentals and signal models

| Feature | Description |
|---|---|
| GPS, Galileo, GLONASS, BeiDou and QZSS | Constellation, signal and orbit reference models |
| SBAS and regional navigation systems | Augmentation constellations and corrections |
| GNSS time systems | GPS, UTC, Galileo, BeiDou and GLONASS time conversion |
| Satellite ephemerides | Broadcast and precise orbit interpolation |
| Satellite clock models | Clock bias, drift and relativistic corrections |
| Pseudorange measurement | Code-based satellite range modeling |
| Carrier-phase measurement | Phase cycles, ambiguities and wavelength |
| Doppler measurement | Range-rate and frequency-shift observations |
| Signal travel time | Transmission/reception time and Earth rotation correction |
| Satellite geometry | Azimuth, elevation and visibility |
| DOP metrics | GDOP, PDOP, HDOP, VDOP and TDOP |
| Satellite selection | Geometry- and quality-based selection |
| Link budget and C/N0 | Received power and carrier-to-noise metrics |
| Multipath models | Reflected signal error and mitigation |
| Ionospheric delay | Single/dual-frequency delay corrections |
| Tropospheric delay | Dry/wet delay and mapping functions |
| Earth tide and loading corrections | Geophysical displacement corrections |
| Antenna phase center | Antenna offsets and variation models |

## Coordinate frames, geodesy and maps

| Feature | Description |
|---|---|
| WGS84 and reference ellipsoids | Ellipsoid geometry and Earth constants |
| ECEF and geodetic conversion | Cartesian to latitude, longitude, height |
| ENU, NED and local frames | Local tangent plane transformations |
| ECI and ECEF conversion | Earth rotation and inertial reference frames |
| ITRF and datum transformations | Reference frame epochs and transformations |
| UTM and UPS projections | Grid coordinates and inverse projections |
| Geoid and orthometric height | Ellipsoidal-to-mean-sea-level height conversion |
| Geodesic distance and bearing | Ellipsoidal inverse/direct geodesics |
| Map projection library | Mercator, Lambert and other projections |
| Coordinate uncertainty transforms | Covariance propagation between frames |
| Velocity and acceleration frames | Motion vector and covariance conversion |
| Lever-arm and boresight calibration | Sensor installation offsets and orientation |

## Observation processing and file formats

| Feature | Description |
|---|---|
| RINEX observation import | GNSS code, carrier and Doppler observation files |
| RINEX navigation import | Broadcast ephemeris and clock files |
| SP3 precise orbits | Precise orbit and clock interpolation |
| CLK precise clock files | Precise clock data |
| RTCM observation streams | Real-time correction and measurement messages |
| NMEA parsing | Receiver position, velocity and quality messages |
| UBX and vendor binary logs | Receiver-specific measurements and status |
| IMU logs | Accelerometer and gyro time series |
| Timestamp synchronization | Cross-sensor time offsets and drift |
| Observation quality control | Range, carrier, Doppler and geometry validation |
| Cycle-slip detection and repair | Carrier-phase discontinuity detection |
| Outlier and gross-error rejection | Robust observation screening |
| Measurement weighting | Elevation, C/N0 and noise-based weighting |
| Observation residuals | Pre-fit and post-fit residual diagnostics |
| Observation visualization | Skyplots, timelines and satellite availability |
| Missing data handling | Gaps, duplicates and irregular sampling |

## Position, velocity and timing estimation

| Feature | Description |
|---|---|
| Single-point positioning | Least-squares GNSS pseudorange position |
| Weighted least squares | Noise-weighted position and clock estimation |
| Iterative nonlinear estimation | Gauss–Newton and Levenberg–Marquardt |
| Robust positioning | Huber and other robust loss functions |
| Velocity from Doppler | Receiver velocity and clock drift |
| Position-velocity-time solution | Joint PVT estimation |
| Sequential estimation | Recursive positioning across epochs |
| Extended Kalman filter | Nonlinear navigation state estimation |
| Unscented Kalman filter | Sigma-point navigation filtering |
| Information and square-root filters | Numerically stable recursive estimation |
| Particle filter | Non-Gaussian navigation state estimation |
| Factor-graph optimization | Batch/smoothing multi-sensor estimation |
| Rauch–Tung–Striebel smoother | Backward state smoothing |
| Ambiguity estimation | Carrier-phase integer ambiguity states |
| Integer ambiguity resolution | LAMBDA-style integer least squares |
| RAIM | Receiver autonomous integrity monitoring |
| ARAIM | Advanced integrity monitoring |
| Protection levels | Horizontal and vertical integrity bounds |
| Error ellipses and confidence regions | Position covariance visualization |
| Clock bias and drift estimation | Receiver timing states |
| Time transfer and synchronization | Precise clock comparison and timing |

## Differential and precise positioning

| Feature | Description |
|---|---|
| DGPS | Differential code corrections |
| RTK baseline positioning | Real-time kinematic carrier-phase positioning |
| Network RTK | VRS, FKP and network corrections |
| PPK | Post-processed kinematic positioning |
| PPP | Precise point positioning |
| PPP-RTK | Precise point positioning with regional corrections |
| Static survey adjustment | Long-duration station position estimation |
| Baseline vector estimation | Relative receiver geometry |
| Reference station processing | Base station coordinates and corrections |
| CORS network integration | Continuously operating reference stations |
| Ambiguity fixing validation | Ratio and integrity tests |
| Convergence monitoring | Time-to-fix and position quality |
| Multi-frequency combinations | Ionosphere-free and wide-lane combinations |
| Multi-constellation fusion | Combined constellation observation estimation |

## INS and multisensor fusion

| Feature | Description |
|---|---|
| IMU calibration | Accelerometer/gyroscope biases, scale and misalignment |
| Strapdown inertial navigation | Quaternion and mechanization equations |
| Attitude estimation | Roll, pitch, yaw and quaternion filtering |
| GNSS/INS loosely coupled fusion | Fusion of receiver PVT with IMU |
| GNSS/INS tightly coupled fusion | Raw satellite observations with IMU |
| Ultra-tightly coupled GNSS/INS | Signal tracking and inertial aiding |
| Wheel odometry fusion | Vehicle wheel speed and encoder updates |
| Barometer fusion | Pressure-altitude observation updates |
| Magnetometer fusion | Heading measurements and magnetic calibration |
| Visual odometry fusion | Camera motion estimates |
| LiDAR odometry fusion | Point-cloud motion estimates |
| UWB positioning fusion | Ranging-based indoor localization |
| Wi-Fi and BLE positioning | Radio fingerprint and ranging localization |
| Radar odometry | Radar-based motion estimation |
| Zero-velocity updates | Stationary inertial drift correction |
| Nonholonomic constraints | Vehicle lateral/vertical velocity constraints |
| Sensor fault detection | Innovation gating and consistency checks |
| Extrinsic calibration | Inter-sensor rotation and translation |
| Time-offset calibration | Sensor latency and synchronization estimation |

## Navigation, tracking and mapping

| Feature | Description |
|---|---|
| Trajectory estimation | Continuous position and velocity histories |
| Map matching | Road/rail/path constrained positioning |
| Dead reckoning | Position propagation during GNSS outage |
| Route and waypoint navigation | Distance, heading and arrival estimates |
| Cross-track and along-track error | Route-relative navigation metrics |
| Track smoothing | Denoised position and heading histories |
| Geofencing | Spatial entry and exit checks |
| Heading and course estimation | Motion heading and course over ground |
| Ground speed and vertical speed | Velocity-derived navigation metrics |
| GNSS coverage planning | Satellite availability and geometry forecast |
| Indoor positioning | Building-frame and anchor-based localization |
| SLAM integration | Simultaneous localization and mapping interfaces |
| Landmark-based localization | Map feature observations and pose estimation |
| Multi-agent localization | Cooperative ranging and position estimation |

## Integrity, errors and reliability

| Feature | Description |
|---|---|
| Error budget | Satellite, atmospheric, receiver and geometry errors |
| Covariance consistency | NEES/NIS and residual consistency |
| Availability and continuity | Position service uptime and outage metrics |
| Integrity risk | Probability of hazardous misleading information |
| Spoofing indicators | Inconsistent signals, clock and geometry checks |
| Jamming indicators | Signal quality and spectrum anomaly metrics |
| Multipath diagnostics | Correlator and residual-based diagnostics |
| Cycle-slip monitoring | Phase discontinuity quality tracking |
| Receiver fault isolation | Exclusion of faulty satellites and sensors |
| Confidence and uncertainty | Covariance, CEP, RMS and percentile accuracy |
| Fault injection | Simulated sensor/constellation failures |
| Urban canyon degradation | NLOS and limited sky-visibility modeling |
| Safety-critical navigation metrics | Alert limits, time to alert and protection levels |

## Simulation, visualization and engineering workflow

| Feature | Description |
|---|---|
| Satellite orbit visualization | Ground tracks and orbital geometry |
| Skyplot | Azimuth/elevation satellite display |
| World map and local trajectory plots | Geographic and local-frame paths |
| 3D navigation state visualization | Position, attitude and uncertainty volumes |
| Observation timeline | Code, carrier, Doppler and quality time series |
| Filter diagnostics | Innovation, covariance and bias plots |
| Scenario simulator | Satellite visibility, noise and receiver motion |
| GNSS outage simulation | Signal loss and recovery experiments |
| Monte Carlo navigation analysis | Accuracy and integrity distributions |
| Parameter sweeps | Noise, constellation and estimator comparisons |
| Batch log processing | Multiple measurement datasets |
| Live stream monitoring | Receiver data and corrections dashboard |
| Results export | CSV, JSON, KML, GPX and GeoJSON |
| Navigation report generation | Reproducible estimates and quality reports |
| Reference test datasets | Known coordinate and trajectory benchmarks |
| Reusable sensor models | Shared sensor and noise model registry |
| Navigation toolbox examples | Survey, automotive, drone, aviation and robotics workflows |

**Catalog total:** 144 feature entries in 9 categories. Counts overlap existing mathematics, aerospace, electrical, physics and control theory catalogs; do not sum them as distinct new implementations. Position outputs must display coordinate reference frame, epoch, units, assumptions, uncertainty and integrity limitations.
