import numpy as np


def sigmoid(x):
    return 1 / (1 + np.exp(-np.clip(x, -500, 500)))

def relu(x):
    return np.maximum(0, x)

def tanh(x):
    return np.tanh(x)


def target_sin(x):
    return np.sin(2 * np.pi * x)

def target_step(x):
    return np.where(x < 0.5, 0, 1).astype(float)

def target_complex(x):
    return np.sin(2*np.pi*x) + 0.5*np.sin(4*np.pi*x) + 0.3*np.cos(6*np.pi*x)

FUNCTIONS = {
    'sine':    target_sin,
    'step':    target_step,
    'complex': target_complex,
}


class UniversalApproximator:
    def __init__(self, n_hidden):
        self.n_hidden = n_hidden
        limit = np.sqrt(6 / (1 + n_hidden))
        self.W1 = np.random.uniform(-limit, limit, (1, n_hidden))
        self.b1 = np.zeros(n_hidden)
        limit = np.sqrt(6 / (n_hidden + 1))
        self.W2 = np.random.uniform(-limit, limit, (n_hidden, 1))
        self.b2 = np.zeros(1)

    def forward(self, x):
        z1 = x @ self.W1 + self.b1
        a1 = tanh(z1)
        return a1 @ self.W2 + self.b2

    def train(self, X, y, epochs=5000, lr=0.05):
        for _ in range(epochs):
            z1 = X @ self.W1 + self.b1
            a1 = tanh(z1)
            output = a1 @ self.W2 + self.b2
            dL = 2 * (output - y) / len(X)
            self.W2 -= lr * (a1.T @ dL)
            self.b2 -= lr * np.sum(dL, axis=0)
            dz1 = (dL @ self.W2.T) * (1 - a1**2)
            self.W1 -= lr * (X.T @ dz1)
            self.b1 -= lr * np.sum(dz1, axis=0)


def approximate(func_name):
    x_train = np.linspace(0, 1, 100).reshape(-1, 1)
    x_test  = np.linspace(0, 1, 200).reshape(-1, 1)
    target  = FUNCTIONS[func_name]
    y_train = target(x_train)
    y_test  = target(x_test)

    results = []
    for n in [3, 10, 50]:
        lr = 0.05 if n < 20 else 0.05
        model = UniversalApproximator(n_hidden=n)
        model.train(x_train, y_train, epochs=10000, lr=lr)
        y_pred = model.forward(x_test)
        mse = float(np.mean((y_pred - y_test)**2))
        results.append({'n': n, 'x': x_test, 'y_true': y_test, 'y_pred': y_pred, 'mse': mse})

    return results