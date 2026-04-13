import numpy as np


def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def relu(x):
    return np.maximum(0, x)


class SimpleNetwork:
    def __init__(self):
        np.random.seed(42)
        self.W1 = np.random.randn(2, 3) * 0.5
        self.b1 = np.random.randn(3) * 0.1
        self.W2 = np.random.randn(3, 1) * 0.5
        self.b2 = np.random.randn(1) * 0.1

    def forward(self, X):
        self.z1 = np.dot(X, self.W1) + self.b1
        self.a1 = relu(self.z1)
        self.z2 = np.dot(self.a1, self.W2) + self.b2
        self.a2 = sigmoid(self.z2)
        return self.a2

    def randomize_weights(self):
        self.W1 = np.random.randn(2, 3) * 0.5
        self.b1 = np.random.randn(3) * 0.1
        self.W2 = np.random.randn(3, 1) * 0.5
        self.b2 = np.random.randn(1) * 0.1