from PySide6.QtWidgets import QMainWindow, QTabWidget
from app.tabs.tab_perfect1d import Perfect1DTab
from app.tabs.tab_projectile import ProjectileTab
from app.tabs.tab_overfitting import OverfittingTab
from app.tabs.tab_pendulum import PendulumTab


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Physics Neural Network GUI — Week 4')
        self.resize(1400, 700)

        tabs = QTabWidget()
        tabs.addTab(Perfect1DTab(), '1D Function Approximation')
        tabs.addTab(ProjectileTab(), 'Projectile Motion')
        tabs.addTab(OverfittingTab(), 'Overfitting')
        tabs.addTab(PendulumTab(), 'Pendulum')

        self.setCentralWidget(tabs)
