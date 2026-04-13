import numpy as np
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
from tensorflow import keras
from .worker_base import BaseWorker, EpochCallback

G = 9.81


def generate_projectile_data(n_samples: int, noise_level: float = 0.5):
    v0 = np.random.uniform(10, 50, n_samples)
    theta = np.random.uniform(20, 70, n_samples)
    theta_rad = np.deg2rad(theta)
    t_max = 2 * v0 * np.sin(theta_rad) / G
    t = np.random.uniform(0, t_max * 0.9, n_samples)
    x = v0 * np.cos(theta_rad) * t + np.random.normal(0, noise_level, n_samples)
    y = v0 * np.sin(theta_rad) * t - 0.5 * G * t ** 2 + np.random.normal(0, noise_level, n_samples)
    valid = y >= 0
    X = np.column_stack([v0[valid], theta[valid], t[valid]])
    Y = np.column_stack([x[valid], y[valid]])
    return X, Y


def predict_trajectory(model, v0: float, theta: float, n_points: int = 50):
    theta_rad = np.deg2rad(theta)
    t_max = 2 * v0 * np.sin(theta_rad) / G
    t = np.linspace(0, t_max, n_points)
    X_in = np.column_stack([np.full(n_points, v0), np.full(n_points, theta), t])
    pred = model.predict(X_in, verbose=0)
    return pred[:, 0], pred[:, 1], t


def create_projectile_model(lr: float = 0.001):
    model = keras.Sequential([
        keras.layers.Input(shape=(3,)),
        keras.layers.Dense(128, activation='relu'),
        keras.layers.Dropout(0.1),
        keras.layers.Dense(64, activation='relu'),
        keras.layers.Dropout(0.1),
        keras.layers.Dense(32, activation='relu'),
        keras.layers.Dropout(0.1),
        keras.layers.Dense(2, activation='linear'),
    ])
    model.compile(optimizer=keras.optimizers.Adam(lr), loss='mse', metrics=['mae'])
    return model


class ProjectileWorker(BaseWorker):
    def run(self):
        try:
            p = self.params
            X_tr, Y_tr = generate_projectile_data(p['n_samples'], noise_level=0.5)
            X_te, Y_te = generate_projectile_data(500, noise_level=0.0)
            model = create_projectile_model(p['lr'])
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

            v0_test, theta_test = p['v0_test'], p['theta_test']
            x_pred, y_pred, t = predict_trajectory(model, v0_test, theta_test)
            theta_rad = np.deg2rad(theta_test)
            x_true = v0_test * np.cos(theta_rad) * t
            y_true = v0_test * np.sin(theta_rad) * t - 0.5 * G * t ** 2

            angles = np.arange(20, 71, 5)
            errors_angle = []
            for ang in angles:
                xp, yp, tt = predict_trajectory(model, 30, ang)
                ar = np.deg2rad(ang)
                xt = 30 * np.cos(ar) * tt
                yt = 30 * np.sin(ar) * tt - 0.5 * G * tt ** 2
                errors_angle.append(float(np.mean((xp - xt) ** 2 + (yp - yt) ** 2)))

            velocities = np.arange(10, 51, 5)
            errors_vel = []
            for v in velocities:
                xp, yp, tt = predict_trajectory(model, v, 45)
                ar = np.deg2rad(45)
                xt = v * np.cos(ar) * tt
                yt = v * np.sin(ar) * tt - 0.5 * G * tt ** 2
                errors_vel.append(float(np.mean((xp - xt) ** 2 + (yp - yt) ** 2)))

            test_loss, test_mae = model.evaluate(X_te, Y_te, verbose=0)

            self.signals.training_done.emit({
                'history': history.history,
                'x_pred': x_pred, 'y_pred': y_pred,
                'x_true': x_true, 'y_true': y_true, 't': t,
                'v0_test': v0_test, 'theta_test': theta_test,
                'angles': angles.tolist(), 'errors_angle': errors_angle,
                'velocities': velocities.tolist(), 'errors_vel': errors_vel,
                'test_loss': float(test_loss), 'test_mae': float(test_mae),
            })
        except Exception as e:
            self.signals.error.emit(str(e))
