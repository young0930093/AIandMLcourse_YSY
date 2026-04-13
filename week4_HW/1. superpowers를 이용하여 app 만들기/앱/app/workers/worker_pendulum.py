import numpy as np
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
from tensorflow import keras
from .worker_base import BaseWorker, EpochCallback

G = 9.81


def calculate_true_period(L: float, theta0_deg: float) -> float:
    theta_rad = np.deg2rad(theta0_deg)
    T_small = 2 * np.pi * np.sqrt(L / G)
    correction = 1 + (1/16) * theta_rad**2 + (11/3072) * theta_rad**4
    return float(T_small * correction)


def generate_pendulum_data(n_samples: int, noise_level: float = 0.01):
    L = np.random.uniform(0.5, 3.0, n_samples)
    theta0 = np.random.uniform(5, 80, n_samples)
    T_true = np.array([calculate_true_period(l, t) for l, t in zip(L, theta0)])
    T_noisy = T_true * (1 + np.random.normal(0, noise_level, n_samples))
    X = np.column_stack([L, theta0])
    Y = T_noisy.reshape(-1, 1)
    return X, Y


def create_pendulum_model(lr: float = 0.001):
    model = keras.Sequential([
        keras.layers.Input(shape=(2,)),
        keras.layers.Dense(64, activation='relu'),
        keras.layers.Dropout(0.1),
        keras.layers.Dense(32, activation='relu'),
        keras.layers.Dropout(0.1),
        keras.layers.Dense(16, activation='relu'),
        keras.layers.Dropout(0.1),
        keras.layers.Dense(1, activation='linear'),
    ])
    model.compile(
        optimizer=keras.optimizers.Adam(lr),
        loss='mse',
        metrics=['mae'],
    )
    return model


def simulate_pendulum_rk4(L: float, theta0_deg: float, t_max: float, dt: float = 0.01):
    theta = np.deg2rad(theta0_deg)
    omega = 0.0
    t_arr = np.arange(0, t_max, dt)
    theta_arr = np.zeros_like(t_arr)
    omega_arr = np.zeros_like(t_arr)
    for i in range(len(t_arr)):
        theta_arr[i] = theta
        omega_arr[i] = omega
        k1t, k1o = omega, -(G / L) * np.sin(theta)
        k2t, k2o = omega + 0.5*dt*k1o, -(G/L)*np.sin(theta + 0.5*dt*k1t)
        k3t, k3o = omega + 0.5*dt*k2o, -(G/L)*np.sin(theta + 0.5*dt*k2t)
        k4t, k4o = omega + dt*k3o,     -(G/L)*np.sin(theta + dt*k3t)
        theta += (dt/6)*(k1t + 2*k2t + 2*k3t + k4t)
        omega += (dt/6)*(k1o + 2*k2o + 2*k3o + k4o)
    return t_arr, np.rad2deg(theta_arr), omega_arr


class PendulumWorker(BaseWorker):
    def run(self):
        try:
            p = self.params
            X_tr, Y_tr = generate_pendulum_data(2000, noise_level=0.01)
            X_te, Y_te = generate_pendulum_data(500, noise_level=0.0)
            model = create_pendulum_model(p['lr'])
            epochs = p['epochs']
            self._callback = EpochCallback(self.signals, epochs)

            history = model.fit(
                X_tr, Y_tr,
                validation_split=0.2,
                epochs=epochs,
                batch_size=32,
                verbose=0,
                callbacks=[self._callback],
            )
            if self._callback._stop:
                return

            L_test = p['L_test']
            angles = np.linspace(5, 80, 50)
            X_in = np.column_stack([np.full(50, L_test), angles])
            T_pred = model.predict(X_in, verbose=0).flatten()
            T_true = np.array([calculate_true_period(L_test, a) for a in angles])

            theta_test = p['theta_test']
            T_pred_single = float(model.predict(np.array([[L_test, theta_test]]), verbose=0)[0, 0])
            T_true_single = calculate_true_period(L_test, theta_test)
            t_sim, theta_sim, omega_sim = simulate_pendulum_rk4(L_test, theta_test, T_true_single * 3)

            test_loss, test_mae = model.evaluate(X_te, Y_te, verbose=0)

            self.signals.training_done.emit({
                'history': history.history,
                'angles': angles.tolist(),
                'T_pred': T_pred.tolist(),
                'T_true': T_true.tolist(),
                'L_test': L_test,
                'theta_test': theta_test,
                'T_pred_single': T_pred_single,
                'T_true_single': T_true_single,
                't_sim': t_sim.tolist(),
                'theta_sim': theta_sim.tolist(),
                'omega_sim': omega_sim.tolist(),
                'test_loss': float(test_loss),
                'test_mae': float(test_mae),
            })
        except Exception as e:
            self.signals.error.emit(str(e))
