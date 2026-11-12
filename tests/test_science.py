"""
Comprehensive Unit Test Suite for J.A.R.V.I.S. Scientific and Engineering Intelligence Suite
Validates Capabilities 61 - 75:
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

import math
import os
import sys
import unittest
import numpy as np

# Ensure workspace root is in sys.path
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from jarvis.science import (
    # Cap 61
    ExpressionEvaluator, safe_eval_math, numerical_derivative, second_derivative,
    gradient, integrate_trapezoidal, integrate_simpson, root_bisection,
    root_newton_raphson, polynomial_roots, solve_linear_system, matrix_determinant, matrix_inverse,
    # Cap 62
    KinematicsSolver, DynamicsSolver, GravitationAndOrbit, ThermodynamicsEngine,
    # Cap 63
    OhmsLaw, PassiveNetworks, RLCAnalysis, OpAmpCircuits, DCNetlistSolver,
    # Cap 64
    PlanarArmKinematics, TrajectoryPlanner, PIDController,
    # Cap 65
    DXFGenerator, STLGenerator, SVGTechnicalDrawer,
    # Cap 66
    MonteCarloEngine, ODESimulator,
    # Cap 67
    ScientificDataAnalyzer,
    # Cap 68
    RegressionEngine, DistributionFitter, HypothesisTesting,
    # Cap 69
    ImageProcessingEngine,
    # Cap 70
    SignalProcessingEngine,
    # Cap 71
    Mesh3D, Transform3D, RayTracer3D,
    # Cap 72
    HarrisCornerDetector, ContourAnalyzer,
    # Cap 73
    NMEAParser, IMUSensorFusion, KalmanFilter1D, TelemetryMonitor,
    # Cap 74
    UnitConverter, MechanicsOfMaterials, BeamDeflectionSolver,
    # Cap 75
    TechnicalResearchEngine, MATERIALS_DATABASE, ISO_METRIC_THREADS, AWG_TABLE,
)


class TestCapability61MathReasoning(unittest.TestCase):
    """Capability 61: Mathematical Reasoning tests."""

    def test_expression_evaluator(self):
        evaluator = ExpressionEvaluator({"a": 5.0, "b": 3.0})
        result = evaluator.evaluate("2 * a + sin(pi / 2) - b^2")
        # 2*5 + 1 - 9 = 2
        self.assertAlmostEqual(result, 2.0, places=5)

    def test_safe_eval_math_helper(self):
        val = safe_eval_math("sqrt(16) + log10(100) * 3")
        self.assertAlmostEqual(val, 10.0, places=5)

    def test_numerical_differentiation(self):
        # f(x) = x^3 - 2*x + 1, f'(2) = 3*(4) - 2 = 10
        func = lambda x: x ** 3 - 2.0 * x + 1.0
        df = numerical_derivative(func, 2.0)
        self.assertAlmostEqual(df, 10.0, places=4)
        # f''(2) = 6*(2) = 12
        d2f = second_derivative(func, 2.0)
        self.assertAlmostEqual(d2f, 12.0, places=3)

    def test_numerical_integration(self):
        # int_0^pi sin(x) dx = 2.0
        area_simp = integrate_simpson(math.sin, 0.0, math.pi, n=500)
        self.assertAlmostEqual(area_simp, 2.0, places=5)
        # int_0^1 x^2 dx = 1/3
        area_trap = integrate_trapezoidal(lambda x: x ** 2, 0.0, 1.0, n=1000)
        self.assertAlmostEqual(area_trap, 1.0 / 3.0, places=4)

    def test_root_finding(self):
        func = lambda x: x ** 2 - 4.0
        res_bi = root_bisection(func, 1.0, 3.0)
        self.assertTrue(res_bi["converged"])
        self.assertAlmostEqual(res_bi["root"], 2.0, places=4)

        res_nr = root_newton_raphson(func, 3.0)
        self.assertTrue(res_nr["converged"])
        self.assertAlmostEqual(res_nr["root"], 2.0, places=5)

    def test_polynomial_roots(self):
        # (x - 2)(x - 3) = x^2 - 5x + 6 = 0
        roots = polynomial_roots([1.0, -5.0, 6.0])
        real_roots = sorted([r.real for r in roots])
        self.assertAlmostEqual(real_roots[0], 2.0, places=4)
        self.assertAlmostEqual(real_roots[1], 3.0, places=4)

    def test_linear_algebra_solver(self):
        # 2x + y = 5, x + 3y = 5 -> x=2, y=1
        A = [[2.0, 1.0], [1.0, 3.0]]
        b = [5.0, 5.0]
        x_sol = solve_linear_system(A, b)
        self.assertAlmostEqual(x_sol[0], 2.0, places=5)
        self.assertAlmostEqual(x_sol[1], 1.0, places=5)

        det = matrix_determinant(A)
        self.assertAlmostEqual(det, 5.0, places=5)

        inv = matrix_inverse(A)
        # A * inv should equal identity
        prod = np.array(A) @ np.array(inv)
        np.testing.assert_allclose(prod, np.eye(2), atol=1e-5)


class TestCapability62PhysicsAnalysis(unittest.TestCase):
    """Capability 62: Physics Analysis tests."""

    def test_1d_kinematics(self):
        # Drop from rest: u=0, a=9.80665, t=2 -> v=19.6133, s=19.6133
        res = KinematicsSolver.solve_1d(u=0.0, a=9.80665, t=2.0)
        self.assertAlmostEqual(res["v"], 19.6133, places=3)
        self.assertAlmostEqual(res["s"], 19.6133, places=3)

    def test_projectile_motion(self):
        # 45 deg, v0=20 m/s
        proj = KinematicsSolver.projectile_motion(v0=20.0, angle_deg=45.0, y0=0.0)
        self.assertGreater(proj["range"], 39.0)
        self.assertGreater(proj["max_height"], 9.5)
        self.assertGreater(len(proj["trajectory"]), 10)

    def test_inclined_plane_dynamics(self):
        # mass 10kg, 30 deg slope, friction
        dyn = DynamicsSolver.inclined_plane(mass_kg=10.0, angle_deg=30.0, mu_k=0.1, mu_s=0.2)
        self.assertEqual(dyn["status"], "sliding")
        self.assertGreater(dyn["acceleration_m_s2"], 0.0)

    def test_1d_elastic_collision(self):
        # Equal masses m1=m2=2kg, u1=5, u2=0 -> velocities swap v1=0, v2=5
        col = DynamicsSolver.collision_1d(m1=2.0, u1=5.0, m2=2.0, u2=0.0, elastic=True)
        self.assertAlmostEqual(col["v1"], 0.0, places=5)
        self.assertAlmostEqual(col["v2"], 5.0, places=5)
        self.assertAlmostEqual(col["ke_loss_J"], 0.0, places=5)

    def test_orbital_mechanics(self):
        # Earth orbit at 400km LEO (r = 6371km + 400km = 6.771e6 m)
        m_earth = 5.972e24
        r_orbit = 6.771e6
        orb = GravitationAndOrbit.orbital_mechanics(m_earth, r_orbit)
        # LEO speed ~7.67 km/s
        self.assertGreater(orb["orbital_velocity_m_s"], 7500.0)
        self.assertLess(orb["orbital_velocity_m_s"], 7800.0)

    def test_thermodynamics(self):
        # Ideal gas PV = nRT: solve for P given V=0.024 m^3, n=1 mol, T=298.15 K
        gas = ThermodynamicsEngine.ideal_gas_law(V=0.024, n=1.0, T=298.15)
        self.assertAlmostEqual(gas["P"], 103289.4, places=0)

        # Carnot efficiency: Thot=600K, Tcold=300K -> eta = 50%
        carnot = ThermodynamicsEngine.carnot_efficiency(temp_cold_k=300.0, temp_hot_k=600.0)
        self.assertAlmostEqual(carnot["efficiency_percent"], 50.0, places=5)


class TestCapability63ElectronicsAnalysis(unittest.TestCase):
    """Capability 63: Electronics Analysis tests."""

    def test_ohms_law(self):
        # V=12V, R=4 Ohm -> I=3A, P=36W
        res = OhmsLaw.solve(voltage=12.0, resistance=4.0)
        self.assertAlmostEqual(res["current_A"], 3.0, places=5)
        self.assertAlmostEqual(res["power_W"], 36.0, places=5)

    def test_resistor_networks(self):
        # Series: 10 + 20 + 30 = 60
        r_ser = PassiveNetworks.resistors_series([10.0, 20.0, 30.0])
        self.assertAlmostEqual(r_ser, 60.0, places=5)
        # Parallel: 100 || 100 = 50
        r_par = PassiveNetworks.resistors_parallel([100.0, 100.0])
        self.assertAlmostEqual(r_par, 50.0, places=5)

    def test_rc_transient(self):
        # V=10V, R=1000 Ohm, C=1e-6 Farad -> tau = 0.001s. After 1 tau, v(t) = 10*(1 - 1/e) ~ 6.32V
        rc = PassiveNetworks.rc_transient(v_source=10.0, r_ohm=1000.0, c_farad=1e-6, t_seconds=0.001)
        self.assertAlmostEqual(rc["tau_s"], 0.001, places=6)
        self.assertAlmostEqual(rc["v_t_V"], 6.3212, places=3)

    def test_rlc_resonance(self):
        # L=10mH (0.01H), C=10uF (1e-5F), R=10 Ohm -> f0 = 1 / (2*pi*sqrt(1e-7)) ~ 503.29 Hz
        rlc = RLCAnalysis.series_rlc(resistance=10.0, inductance=0.01, capacitance=1e-5, frequency_hz=503.29)
        self.assertAlmostEqual(rlc["resonant_frequency_hz"], 503.29, places=1)
        self.assertAlmostEqual(rlc["net_reactance_Ohm"], 0.0, places=1)

    def test_op_amp_circuits(self):
        inv = OpAmpCircuits.inverting_amplifier(r_in=10000.0, r_feedback=100000.0)
        self.assertAlmostEqual(inv["gain"], -10.0, places=4)

        non_inv = OpAmpCircuits.non_inverting_amplifier(r_in=10000.0, r_feedback=90000.0)
        self.assertAlmostEqual(non_inv["gain"], 10.0, places=4)

        div = OpAmpCircuits.voltage_divider(v_in=12.0, r1=1000.0, r2=2000.0)
        self.assertAlmostEqual(div["v_out"], 8.0, places=4)


class TestCapability64RoboticsIntelligence(unittest.TestCase):
    """Capability 64: Robotics Intelligence tests."""

    def test_planar_arm_kinematics(self):
        # 2-link: l1=10, l2=10, theta1=0 deg, theta2=90 deg -> end effector at (10, 10)
        fk = PlanarArmKinematics.forward_2link(l1=10.0, l2=10.0, theta1_deg=0.0, theta2_deg=90.0)
        self.assertAlmostEqual(fk["end_effector_x"], 10.0, places=4)
        self.assertAlmostEqual(fk["end_effector_y"], 10.0, places=4)

        # Inverse Kinematics for target (10, 10)
        ik = PlanarArmKinematics.inverse_2link(l1=10.0, l2=10.0, target_x=10.0, target_y=10.0)
        self.assertTrue(ik["reachable"])
        self.assertEqual(len(ik["solutions"]), 2)

    def test_trapezoidal_trajectory(self):
        traj = TrajectoryPlanner.trapezoidal_profile(q0=0.0, q1=100.0, v_max=20.0, a_max=10.0)
        self.assertGreater(traj["total_time_s"], 0.0)
        self.assertAlmostEqual(traj["points"][-1]["q"], 100.0, places=1)
        self.assertAlmostEqual(traj["points"][-1]["v"], 0.0, places=1)

    def test_pid_controller_step_response(self):
        pid = PIDController(kp=10.0, ki=2.0, kd=1.5, output_limits=(-100.0, 100.0))
        sim = pid.simulate_step_response(plant_inertia=1.0, plant_damping=0.5, target=1.0, total_time=4.0)
        self.assertAlmostEqual(sim["final_position"], 1.0, delta=0.05)


class TestCapability65CADAssistance(unittest.TestCase):
    """Capability 65: CAD Assistance tests."""

    def test_dxf_generator(self):
        dxf = DXFGenerator()
        dxf.add_layer("OUTLINE", color_index=1)
        dxf.add_line(0, 0, 100, 100, layer="OUTLINE")
        dxf.add_circle(50, 50, 25)
        dxf.add_text("TEST CAD PART", 10, 20)
        content = dxf.generate_dxf_string()
        self.assertIn("SECTION", content)
        self.assertIn("HEADER", content)
        self.assertIn("ENTITIES", content)
        self.assertIn("EOF", content)
        self.assertIn("OUTLINE", content)

    def test_stl_generator_ascii_and_binary(self):
        # 12 facets for box
        facets = STLGenerator.create_box_facets(10.0, 20.0, 30.0)
        self.assertEqual(len(facets), 12)

        ascii_stl = STLGenerator.to_ascii_stl("BOX_PART", facets)
        self.assertTrue(ascii_stl.startswith("solid BOX_PART"))
        self.assertIn("facet normal", ascii_stl)
        self.assertIn("endsolid BOX_PART", ascii_stl)

        bin_stl = STLGenerator.to_binary_stl(facets)
        # 80-byte header + 4-byte count + 12 * 50 bytes = 684 bytes
        self.assertEqual(len(bin_stl), 80 + 4 + 12 * 50)

    def test_svg_technical_drawer(self):
        drawer = SVGTechnicalDrawer(width=600, height=400, title="BEARING BRACKET")
        drawer.add_rect(50, 50, 200, 150)
        drawer.add_circle(150, 125, 40)
        drawer.add_dimension_h(50, 250, 50, "200 mm")
        svg = drawer.render()
        self.assertTrue(svg.startswith("<svg"))
        self.assertIn("BEARING BRACKET", svg)
        self.assertIn("</svg>", svg)


class TestCapability66Simulators(unittest.TestCase):
    """Capability 66: Simulation Management tests."""

    def test_monte_carlo_pi(self):
        res = MonteCarloEngine.estimate_pi(num_samples=40000, seed=123)
        self.assertAlmostEqual(res["pi_estimate"], math.pi, delta=0.03)

    def test_geometric_brownian_motion(self):
        gbm = MonteCarloEngine.geometric_brownian_motion(s0=100.0, mu=0.05, sigma=0.2, t_total=1.0, num_steps=50, num_paths=100)
        self.assertIn("mean_trajectory", gbm)
        self.assertEqual(len(gbm["mean_trajectory"]), 51)
        self.assertGreater(gbm["final_mean"], 80.0)

    def test_ode_simulator_harmonic_oscillator(self):
        sim = ODESimulator.simulate_harmonic_oscillator(mass=1.0, spring_k=20.0, damping_c=0.8, x0=2.0, t_final=5.0)
        self.assertEqual(len(sim["time"]), len(sim["position"]))
        # Underdamped oscillation should decay from 2.0
        self.assertLess(abs(sim["position"][-1]), 2.0)


class TestCapability67DataAnalysis(unittest.TestCase):
    """Capability 67: Scientific Data Analysis tests."""

    def test_descriptive_stats(self):
        data = [10.0, 12.0, 23.0, 23.0, 16.0, 23.0, 21.0, 16.0]
        stats = ScientificDataAnalyzer.descriptive_stats(data)
        self.assertEqual(stats["count"], 8.0)
        self.assertAlmostEqual(stats["mode"], 23.0, places=2)
        self.assertAlmostEqual(stats["min"], 10.0, places=2)
        self.assertAlmostEqual(stats["max"], 23.0, places=2)
        self.assertGreater(stats["std_dev"], 0.0)

    def test_correlations(self):
        x = [1, 2, 3, 4, 5]
        y = [2, 4, 6, 8, 10]
        r_pearson = ScientificDataAnalyzer.pearson_correlation(x, y)
        self.assertAlmostEqual(r_pearson, 1.0, places=5)

        r_spearman = ScientificDataAnalyzer.spearman_correlation(x, y)
        self.assertAlmostEqual(r_spearman, 1.0, places=5)

    def test_outlier_detection(self):
        # Clean series with one extreme outlier
        series = [10.0, 10.2, 10.1, 9.9, 10.0, 9.8, 10.3, 100.0]
        out_z = ScientificDataAnalyzer.detect_outliers_zscore(series, threshold=2.0)
        self.assertIn(7, out_z["outlier_indices"])

        out_iqr = ScientificDataAnalyzer.detect_outliers_iqr(series)
        self.assertIn(7, out_iqr["outlier_indices"])

    def test_group_by_aggregation(self):
        records = [
            {"dept": "ENG", "salary": 100.0},
            {"dept": "ENG", "salary": 120.0},
            {"dept": "MKT", "salary": 80.0},
        ]
        agg = ScientificDataAnalyzer.group_by_aggregate(records, "dept", "salary", "mean")
        self.assertAlmostEqual(agg["ENG"], 110.0, places=3)
        self.assertAlmostEqual(agg["MKT"], 80.0, places=3)


class TestCapability68StatisticalModeling(unittest.TestCase):
    """Capability 68: Statistical Modeling tests."""

    def test_linear_regression(self):
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [3.0, 5.0, 7.0, 9.0, 11.0]  # y = 2x + 1
        reg = RegressionEngine.linear_regression(x, y)
        self.assertAlmostEqual(reg["slope"], 2.0, places=5)
        self.assertAlmostEqual(reg["intercept"], 1.0, places=5)
        self.assertAlmostEqual(reg["r_squared"], 1.0, places=5)

    def test_distribution_fitting(self):
        data = [10.0, 12.0, 11.0, 9.0, 10.5, 9.5]
        norm = DistributionFitter.fit_normal(data)
        self.assertAlmostEqual(norm["mean_mu"], np.mean(data), places=4)

    def test_hypothesis_tests(self):
        # 1-sample t test against pop mean 10.0
        data = [10.1, 10.2, 9.9, 10.0, 10.1]
        ttest = HypothesisTesting.one_sample_t_test(data, pop_mean=10.0)
        self.assertGreater(ttest["p_value"], 0.05)


class TestCapability69ImageProcessing(unittest.TestCase):
    """Capability 69: Image Processing tests."""

    def test_gaussian_and_box_blur(self):
        img = np.zeros((15, 15), dtype=float)
        img[7, 7] = 255.0
        blurred = ImageProcessingEngine.gaussian_blur(img, size=5, sigma=1.0)
        self.assertEqual(blurred.shape, (15, 15))
        self.assertLess(blurred[7, 7], 255.0)
        self.assertGreater(blurred[7, 6], 0.0)

    def test_sobel_edge_detection(self):
        # Step edge
        img = np.zeros((10, 10), dtype=float)
        img[:, 5:] = 255.0
        sobel = ImageProcessingEngine.sobel_edge_detection(img)
        self.assertGreater(np.max(sobel["magnitude"][:, 5]), 100.0)

    def test_gamma_correction_and_otsu(self):
        img = np.array([[50.0, 50.0], [200.0, 200.0]], dtype=float)
        gamma = ImageProcessingEngine.gamma_correction(img, gamma=2.0)
        self.assertEqual(gamma.shape, (2, 2))

        thresh, binary = ImageProcessingEngine.otsu_threshold(img)
        self.assertGreaterEqual(thresh, 50.0)
        self.assertLessEqual(thresh, 200.0)


class TestCapability70SignalProcessing(unittest.TestCase):
    """Capability 70: Signal Processing tests."""

    def test_fft_spectral_peak_detection(self):
        # Generate 50 Hz sine wave sampled at 1000 Hz
        sample_rate = 1000.0
        duration = 1.0
        sig_data = SignalProcessingEngine.generate_synthetic_signal(
            duration_s=duration, sample_rate_hz=sample_rate,
            frequencies=[50.0, 120.0], amplitudes=[1.0, 0.5]
        )
        fft_res = SignalProcessingEngine.compute_fft(sig_data["signal"], sample_rate)
        peaks = SignalProcessingEngine.detect_peak_frequencies(
            fft_res["frequencies_hz"], fft_res["magnitude"], top_k=2
        )
        found_freqs = [p["frequency_hz"] for p in peaks]
        self.assertIn(50.0, found_freqs)
        self.assertIn(120.0, found_freqs)

    def test_fir_filter_design(self):
        lp = SignalProcessingEngine.design_fir_lowpass(cutoff_hz=100.0, sample_rate_hz=1000.0, num_taps=31)
        self.assertEqual(len(lp), 31)
        self.assertAlmostEqual(np.sum(lp), 1.0, places=4)


class TestCapability71Scene3D(unittest.TestCase):
    """Capability 71: 3D Scene Understanding tests."""

    def test_mesh_properties(self):
        # Unit cube: 8 vertices, 12 faces
        facets = STLGenerator.create_box_facets(2.0, 2.0, 2.0)
        vertices = []
        faces = []
        for norm, (v1, v2, v3) in facets:
            i = len(vertices)
            vertices.extend([v1, v2, v3])
            faces.append((i, i + 1, i + 2))

        mesh = Mesh3D(vertices, faces)
        self.assertAlmostEqual(mesh.compute_surface_area(), 24.0, places=4)
        self.assertAlmostEqual(mesh.compute_enclosed_volume(), 8.0, places=4)

    def test_ray_triangle_intersection(self):
        # Triangle in XY plane at Z=0
        v0 = (-1.0, -1.0, 0.0)
        v1 = (1.0, -1.0, 0.0)
        v2 = (0.0, 1.0, 0.0)
        # Ray aimed directly at origin from Z=5
        ray_origin = (0.0, 0.0, 5.0)
        ray_dir = (0.0, 0.0, -1.0)
        hit = RayTracer3D.ray_triangle_intersect(ray_origin, ray_dir, v0, v1, v2)
        self.assertIsNotNone(hit)
        self.assertAlmostEqual(hit["distance"], 5.0, places=4)
        self.assertAlmostEqual(hit["hit_point"][2], 0.0, places=4)


class TestCapability72ComputerVision(unittest.TestCase):
    """Capability 72: Computer Vision tests."""

    def test_harris_corner_detection(self):
        # Create image with a bright rectangle on black background
        img = np.zeros((30, 30), dtype=float)
        img[10:20, 10:20] = 255.0
        corners = HarrisCornerDetector.detect_corners(img, k=0.04, threshold_ratio=0.01)
        self.assertGreater(len(corners), 0)

    def test_contour_blob_extraction(self):
        mask = np.zeros((20, 20), dtype=int)
        mask[2:7, 2:8] = 1   # 5 x 6 = 30 pixels blob
        blobs = ContourAnalyzer.extract_blobs(mask)
        self.assertEqual(len(blobs), 1)
        self.assertEqual(blobs[0]["area"], 30)
        self.assertEqual(blobs[0]["bbox"]["width"], 6)
        self.assertEqual(blobs[0]["bbox"]["height"], 5)


class TestCapability73SensorIntegration(unittest.TestCase):
    """Capability 73: Sensor Integration tests."""

    def test_nmea_gprmc_parser(self):
        # Real NMEA GPRMC sample with valid checksum
        sentence = "$GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W*6A"
        self.assertTrue(NMEAParser.verify_checksum(sentence))
        parsed = NMEAParser.parse_sentence(sentence)
        self.assertTrue(parsed["valid"])
        self.assertAlmostEqual(parsed["latitude_deg"], 48.1173, places=3)
        self.assertAlmostEqual(parsed["longitude_deg"], 11.5167, places=3)
        self.assertAlmostEqual(parsed["speed_knots"], 22.4, places=2)

    def test_imu_attitude_fusion(self):
        fusion = IMUSensorFusion(alpha=0.98)
        # Stationary flat: ax=0, ay=0, az=9.8
        att = fusion.update_attitude(ax=0.0, ay=0.0, az=9.8, gx_deg_s=0.0, gy_deg_s=0.0, dt_s=0.01)
        self.assertAlmostEqual(att["pitch_deg"], 0.0, delta=1.0)
        self.assertAlmostEqual(att["roll_deg"], 0.0, delta=1.0)

    def test_kalman_filter_1d(self):
        kf = KalmanFilter1D(process_noise_q=1e-3, measurement_noise_r=1e-1, initial_state=0.0)
        for _ in range(20):
            state, cov = kf.update(10.0)
        self.assertAlmostEqual(state, 10.0, delta=0.5)

    def test_telemetry_monitor(self):
        monitor = TelemetryMonitor()
        monitor.set_channel_limits("core_temp_c", min_val=0.0, max_val=85.0)
        alerts = monitor.check_telemetry(100.0, {"core_temp_c": 92.5})
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["condition"], "OVERFLOW")


class TestCapability74EngineeringCalculations(unittest.TestCase):
    """Capability 74: Engineering Calculations tests."""

    def test_unit_converter(self):
        # 1 inch = 25.4 mm
        mm = UnitConverter.convert_length(1.0, "in", "mm")
        self.assertAlmostEqual(mm, 25.4, places=3)
        # 100 C = 212 F
        deg_f = UnitConverter.convert_temperature(100.0, "C", "F")
        self.assertAlmostEqual(deg_f, 212.0, places=3)
        # 1 hp ~ 745.7 W
        watts = UnitConverter.convert_power(1.0, "hp", "W")
        self.assertAlmostEqual(watts, 745.7, places=1)

    def test_mechanics_of_materials(self):
        # Bar: F = 10000 N, Area = 0.0001 m^2 (100 mm^2), L = 1m, E = 200 GPa
        res = MechanicsOfMaterials.axial_stress_strain(
            force_n=10000.0, area_m2=0.0001, original_length_m=1.0,
            youngs_modulus_pa=200e9, yield_strength_pa=250e6
        )
        self.assertAlmostEqual(res["stress_mpa"], 100.0, places=3)
        self.assertAlmostEqual(res["elongation_mm"], 0.5, places=3)
        self.assertAlmostEqual(res["factor_of_safety"], 2.5, places=3)

    def test_beam_deflection(self):
        # Cantilever: L=1.0m, P=1000N, E=200GPa (200e9 Pa), I=1e-6 m^4, c=0.05m
        beam = BeamDeflectionSolver.cantilever_point_load(
            load_n=1000.0, length_m=1.0, youngs_modulus_pa=200e9,
            inertia_m4=1e-6, c_extreme_fiber_m=0.05
        )
        # delta = P * L^3 / (3 * E * I) = 1000 / (3 * 200e9 * 1e-6) = 1000 / 600000 = 1.6667 mm
        self.assertAlmostEqual(beam["max_deflection_mm"], 1.6667, places=3)
        # M_max = 1000 Nm, sigma = 1000 * 0.05 / 1e-6 = 50 MPa
        self.assertAlmostEqual(beam["max_bending_stress_mpa"], 50.0, places=3)


class TestCapability75TechnicalResearch(unittest.TestCase):
    """Capability 75: Technical Research tests."""

    def test_materials_database(self):
        mat = TechnicalResearchEngine.get_material("al_6061_t6")
        self.assertIsNotNone(mat)
        self.assertEqual(mat["density_kg_m3"], 2700.0)
        self.assertEqual(mat["yield_strength_mpa"], 276.0)

        # Filter high strength materials (yield > 250 MPa)
        high_str = TechnicalResearchEngine.filter_materials(min_yield_mpa=250.0)
        self.assertGreater(len(high_str), 1)

    def test_iso_metric_thread_specs(self):
        m6 = TechnicalResearchEngine.get_iso_metric_thread("M6")
        self.assertIsNotNone(m6)
        self.assertEqual(m6["pitch_mm"], 1.0)
        self.assertEqual(m6["tap_drill_mm"], 5.0)

    def test_awg_wire_recommendations(self):
        awg14 = TechnicalResearchEngine.get_awg_wire(14)
        self.assertIsNotNone(awg14)
        self.assertEqual(awg14["ampacity_75c"], 20.0)

        # 15A load at 120V over 10m
        rec = TechnicalResearchEngine.recommend_awg_wire(
            current_amps=15.0, circuit_voltage_v=120.0, one_way_length_m=10.0, max_voltage_drop_pct=3.0
        )
        self.assertIn("recommended_awg", rec)
        self.assertLessEqual(rec["recommended_awg"], 14)


if __name__ == "__main__":
    unittest.main()
