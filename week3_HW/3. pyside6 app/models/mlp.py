import numpy as np


def sigmoid(x):
    return 1 / (1 + np.exp(-np.clip(x, -500, 500)))

def sigmoid_derivative(x):
    s = sigmoid(x)
    return s * (1 - s)


class MLP:
    def __init__(self, learning_rate=0.5):
        self.lr = learning_rate
        self.loss_history = []
        self._init_weights()

    def _init_weights(self):
        self.W1 = np.random.randn(2, 4) * np.sqrt(2.0 / 2)
        self.b1 = np.zeros((1, 4))
        self.W2 = np.random.randn(4, 1) * np.sqrt(2.0 / 4)
        self.b2 = np.zeros((1, 1))

    def forward(self, X):
        self.z1 = np.dot(X, self.W1) + self.b1
        self.a1 = sigmoid(self.z1)
        self.z2 = np.dot(self.a1, self.W2) + self.b2
        self.a2 = sigmoid(self.z2)
        return self.a2

    def backward(self, X, y, output):
        m = X.shape[0]
        dz2 = output - y
        dW2 = (1/m) * np.dot(self.a1.T, dz2)
        db2 = (1/m) * np.sum(dz2, axis=0, keepdims=True)
        da1 = np.dot(dz2, self.W2.T)
        dz1 = da1 * sigmoid_derivative(self.z1)
        dW1 = (1/m) * np.dot(X.T, dz1)
        db1 = (1/m) * np.sum(dz1, axis=0, keepdims=True)
        self.W2 -= self.lr * dW2
        self.b2 -= self.lr * db2
        self.W1 -= self.lr * dW1
        self.b1 -= self.lr * db1

    def train(self, X, y, epochs):
        self.loss_history = []
        self._init_weights()
        for epoch in range(epochs):
            output = self.forward(X)
            loss = np.mean((output - y) ** 2)
            self.loss_history.append(loss)
            self.backward(X, y, output)
            yield epoch, loss

    def predict(self, X):
        output = self.forward(X)
        return (output > 0.5).astype(int)

    def get_decision_boundary(self):
        x_min, x_max = -0.5, 1.5
        y_min, y_max = -0.5, 1.5
        xx, yy = np.meshgrid(np.linspace(x_min, x_max, 200),
                              np.linspace(y_min, y_max, 200))
        Z = self.forward(np.c_[xx.ravel(), yy.ravel()])
        return xx, yy, Z.reshape(xx.shape)