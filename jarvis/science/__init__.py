"""
J.A.R.V.I.S. Scientific and Engineering Intelligence Suite
Owns Capabilities 61 - 75:
  61. Mathematical Reasoning (Symbolic & numerical math)
  62. Physics Analysis (Classical mechanics, kinematics, thermodynamics)
  63. Electronics Analysis (Ohm's law, RLC circuits, schematic analysis)
  64. Robotics Intelligence (Kinematics, trajectory, PID controls)
  65. CAD Assistance (DXF / STL / SVG wireframe geometric generators)
  66. Simulation Management (Monte Carlo & numerical differential simulators)
  67. Scientific Data Analysis (NumPy/Pandas/statistical metrics)
  68. Statistical Modeling (Regression, distribution fitting, hypothesis testing)
  69. Image Processing (Filters, edge detection, contrast, convolutions)
  70. Signal Processing (FFT, spectral analysis, frequency filters)
  71. 3D Scene Understanding (Mesh geometry, vertices, transforms)
  72. Computer Vision (Feature extraction, contour detection)
  73. Sensor Integration (Simulated & serial sensor telemetry streams)
  74. Engineering Calculations (Unit conversion, stress/strain, beam deflection)
  75. Technical Research (Engineering specs & standard tables)
"""

from jarvis.science.math_engine import (
    ExpressionEvaluator,
    safe_eval_math,
    numerical_derivative,
    second_derivative,
    gradient,
    integrate_trapezoidal,
    integrate_simpson,
    root_bisection,
    root_newton_raphson,
    polynomial_roots,
    solve_linear_system,
    matrix_determinant,
    matrix_inverse,
)

from jarvis.science.physics import (
    KinematicsSolver,
    DynamicsSolver,
    GravitationAndOrbit,
    ThermodynamicsEngine,
)

from jarvis.science.electronics import (
    OhmsLaw,
    PassiveNetworks,
    RLCAnalysis,
    OpAmpCircuits,
    DCNetlistSolver,
)

from jarvis.science.robotics import (
    PlanarArmKinematics,
    TrajectoryPlanner,
    PIDController,
)

from jarvis.science.cad import (
    DXFGenerator,
    STLGenerator,
    SVGTechnicalDrawer,
)

from jarvis.science.simulators import (
    MonteCarloEngine,
    ODESimulator,
)

from jarvis.science.data_analysis import (
    ScientificDataAnalyzer,
)

from jarvis.science.statistical_modeling import (
    RegressionEngine,
    DistributionFitter,
    HypothesisTesting,
)

from jarvis.science.image_processing import (
    ImageProcessingEngine,
)

from jarvis.science.signal_processing import (
    SignalProcessingEngine,
)

from jarvis.science.scene3d import (
    Mesh3D,
    Transform3D,
    RayTracer3D,
)

from jarvis.science.computer_vision import (
    HarrisCornerDetector,
    ContourAnalyzer,
)

from jarvis.science.sensors import (
    NMEAParser,
    IMUSensorFusion,
    KalmanFilter1D,
    TelemetryMonitor,
)

from jarvis.science.engineering import (
    UnitConverter,
    MechanicsOfMaterials,
    BeamDeflectionSolver,
)

from jarvis.science.technical_research import (
    TechnicalResearchEngine,
    MATERIALS_DATABASE,
    ISO_METRIC_THREADS,
    AWG_TABLE,
)

__all__ = [
    # Cap 61
    "ExpressionEvaluator", "safe_eval_math", "numerical_derivative", "second_derivative",
    "gradient", "integrate_trapezoidal", "integrate_simpson", "root_bisection",
    "root_newton_raphson", "polynomial_roots", "solve_linear_system", "matrix_determinant", "matrix_inverse",
    # Cap 62
    "KinematicsSolver", "DynamicsSolver", "GravitationAndOrbit", "ThermodynamicsEngine",
    # Cap 63
    "OhmsLaw", "PassiveNetworks", "RLCAnalysis", "OpAmpCircuits", "DCNetlistSolver",
    # Cap 64
    "PlanarArmKinematics", "TrajectoryPlanner", "PIDController",
    # Cap 65
    "DXFGenerator", "STLGenerator", "SVGTechnicalDrawer",
    # Cap 66
    "MonteCarloEngine", "ODESimulator",
    # Cap 67
    "ScientificDataAnalyzer",
    # Cap 68
    "RegressionEngine", "DistributionFitter", "HypothesisTesting",
    # Cap 69
    "ImageProcessingEngine",
    # Cap 70
    "SignalProcessingEngine",
    # Cap 71
    "Mesh3D", "Transform3D", "RayTracer3D",
    # Cap 72
    "HarrisCornerDetector", "ContourAnalyzer",
    # Cap 73
    "NMEAParser", "IMUSensorFusion", "KalmanFilter1D", "TelemetryMonitor",
    # Cap 74
    "UnitConverter", "MechanicsOfMaterials", "BeamDeflectionSolver",
    # Cap 75
    "TechnicalResearchEngine", "MATERIALS_DATABASE", "ISO_METRIC_THREADS", "AWG_TABLE",
]
