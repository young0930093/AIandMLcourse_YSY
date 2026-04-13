from PySide6.QtWidgets import QMainWindow, QTabWidget
from app.tabs.tab_perceptron import PerceptronTab
from app.tabs.tab_activation import ActivationTab
from app.tabs.tab_forward import ForwardTab
from app.tabs.tab_mlp import MLPTab
from app.tabs.tab_universal import UniversalTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Neural Networks Explorer")
        self.setMinimumSize(1280, 800)

        tabs = QTabWidget()
        tabs.addTab(PerceptronTab(),  "Perceptron")
        tabs.addTab(ActivationTab(),  "Activation Functions")
        tabs.addTab(ForwardTab(),     "Forward Propagation")
        tabs.addTab(MLPTab(),         "MLP / Backprop")
        tabs.addTab(UniversalTab(),   "Universal Approximation")

        self.setCentralWidget(tabs)