import numpy as np

def test_projectile_data_shapes():
    from app.workers.worker_projectile import generate_projectile_data
    X, Y = generate_projectile_data(200, noise_level=0.0)
    assert X.shape[1] == 3   # v0, theta, t
    assert Y.shape[1] == 2   # x, y
    assert np.all(Y[:, 1] >= -0.01)  # y >= 0 (노이즈 없음)

def test_projectile_data_physics():
    import numpy as np
    v0, theta, t = 20.0, 45.0, 0.5
    theta_rad = np.deg2rad(theta)
    g = 9.81
    expected_x = v0 * np.cos(theta_rad) * t
    expected_y = v0 * np.sin(theta_rad) * t - 0.5 * g * t**2
    assert expected_x > 0
    assert expected_y > 0

def test_projectile_model_shape():
    from app.workers.worker_projectile import create_projectile_model
    model = create_projectile_model(lr=0.001)
    import numpy as np
    out = model.predict(np.zeros((5, 3)), verbose=0)
    assert out.shape == (5, 2)

def test_overfitting_data_shapes():
    from app.workers.worker_overfitting import generate_data
    x_tr, y_tr, x_val, y_val, x_te, y_te = generate_data(50, 20, 100, 0.3)
    assert x_tr.shape == (50, 1)
    assert y_te.shape == (100, 1)

def test_overfitting_true_function():
    from app.workers.worker_overfitting import true_function
    import numpy as np
    x = np.array([[0.0]])
    # sin(2*0) + 0.5*0 = 0
    assert abs(true_function(x)[0, 0]) < 1e-9

def test_overfitting_model_shapes():
    from app.workers.worker_overfitting import create_underfit, create_good, create_overfit
    import numpy as np
    for create_fn in [create_underfit, create_good, create_overfit]:
        model = create_fn(lr=0.001)
        out = model.predict(np.zeros((3, 1)), verbose=0)
        assert out.shape == (3, 1)

def test_pendulum_small_angle():
    """작은 각도 근사: T ≈ 2π√(L/g)"""
    from app.workers.worker_pendulum import calculate_true_period
    import numpy as np
    L, g = 1.0, 9.81
    T = calculate_true_period(L, 5.0)
    T_approx = 2 * np.pi * np.sqrt(L / g)
    assert abs(T - T_approx) < 0.01

def test_pendulum_data_shapes():
    from app.workers.worker_pendulum import generate_pendulum_data
    X, Y = generate_pendulum_data(100, noise_level=0.0)
    assert X.shape == (100, 2)
    assert Y.shape == (100, 1)
    assert all(Y > 0)

def test_rk4_returns_arrays():
    from app.workers.worker_pendulum import simulate_pendulum_rk4
    t, theta, omega = simulate_pendulum_rk4(L=1.0, theta0_deg=30.0, t_max=2.0)
    assert len(t) > 0
    assert len(t) == len(theta) == len(omega)
    assert abs(theta[0] - 30.0) < 0.1

def test_pendulum_model_shape():
    from app.workers.worker_pendulum import create_pendulum_model
    import numpy as np
    model = create_pendulum_model(lr=0.001)
    out = model.predict(np.zeros((5, 2)), verbose=0)
    assert out.shape == (5, 1)
