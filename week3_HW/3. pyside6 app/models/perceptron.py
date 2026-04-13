import numpy as np


class Perceptron:
    def __init__(self, input_size, learning_rate=0.1):
        self.weights = np.random.randn(input_size)
        self.bias = np.random.randn()
        self.lr = learning_rate

    def activation(self, x):
        return 1 if x >= 0 else 0

    def predict(self, inputs):
        summation = np.dot(inputs, self.weights) + self.bias
        return self.activation(summation)

    def train(self, training_inputs, labels, epochs):
        for epoch in range(epochs):
            for inputs, label in zip(training_inputs, labels):
                prediction = self.predict(inputs)
                error = label - prediction
                self.weights += self.lr * error * inputs
                self.bias += self.lr * error

    def get_decision_boundary(self):
        x_min, x_max = -0.5, 1.5
        y_min, y_max = -0.5, 1.5
        xx, yy = np.meshgrid(np.linspace(x_min, x_max, 100),
                              np.linspace(y_min, y_max, 100))
        Z = np.array([self.predict(np.array([xi, yi]))
                      for xi, yi in zip(xx.ravel(), yy.ravel())])
        Z = Z.reshape(xx.shape)
        return xx, yy, Z