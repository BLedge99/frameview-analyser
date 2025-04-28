import sys
import pandas as pd
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from app.data import frameViewDataAnalyser


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Frame View Analyser")
        self.resize(1600, 800)  # Adjust main window dimensions
        self.dataAnalyser = None

        # Setup UI
        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.mainLayout = QtWidgets.QVBoxLayout(self.centralwidget)

        # Horizontal layout for controls and graph
        self.horizontalLayout = QtWidgets.QHBoxLayout()

        # Vertical layout for controls
        self.controlLayout = QtWidgets.QVBoxLayout()

        # Load CSV Button
        self.loadButton = QtWidgets.QPushButton("Load CSV", self)
        self.loadButton.clicked.connect(self.loadCSV)
        self.controlLayout.addWidget(self.loadButton)

        # X-Axis Label and List
        self.xAxisLabel = QtWidgets.QLabel("X Axis", self)
        self.controlLayout.addWidget(self.xAxisLabel)
        self.xAxisListWidget = QtWidgets.QListWidget(self)
        self.xAxisListWidget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.xAxisListWidget.itemSelectionChanged.connect(self.refreshPlot)
        self.controlLayout.addWidget(self.xAxisListWidget)

        # Y-Axis Label and List
        self.yAxisLabel = QtWidgets.QLabel("Y Axis", self)
        self.controlLayout.addWidget(self.yAxisLabel)
        self.yAxisListWidget = QtWidgets.QListWidget(self)
        self.yAxisListWidget.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.yAxisListWidget.itemSelectionChanged.connect(self.refreshPlot)
        self.controlLayout.addWidget(self.yAxisListWidget)

        self.horizontalLayout.addLayout(self.controlLayout)

        # Plot area with scrollable feature
        self.scrollArea = QtWidgets.QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 800, 600))
        self.plotLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.plotWidget = QtWidgets.QWidget(self.scrollAreaWidgetContents)
        self.plotLayout.addWidget(self.plotWidget)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.horizontalLayout.addWidget(self.scrollArea)

        # Add the horizontal layout to the main layout
        self.mainLayout.addLayout(self.horizontalLayout)

        # Setup matplotlib canvas
        self.canvas = FigureCanvas(plt.figure(figsize=(20, 6)))
        layout = QtWidgets.QVBoxLayout(self.plotWidget)
        layout.addWidget(self.canvas)

    def loadCSV(self):
        try:
            # File dialog to load CSV
            options = QFileDialog.Options()
            filePath, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)", options=options)
            if filePath:
                # Load CSV with error handling
                df = pd.read_csv(filePath)
                self.dataAnalyser = frameViewDataAnalyser(df)

                # Populate ListWidgets with column names
                self.xAxisListWidget.clear()
                self.yAxisListWidget.clear()
                self.xAxisListWidget.addItems(self.dataAnalyser.getCols())
                self.yAxisListWidget.addItems(self.dataAnalyser.getCols())

                # Update average metrics
                latency = self.dataAnalyser.getAvgLatency()
                fps = self.dataAnalyser.getAvgFPS()
                frametime = self.dataAnalyser.getAvgFrametime()
                print(f"Avg Latency: {latency:.2f}" if latency else "Avg Latency: N/A")
                print(f"Avg FPS: {fps:.2f}" if fps else "Avg FPS: N/A")
                print(f"Avg Frametime: {frametime:.2f}" if frametime else "Avg Frametime: N/A")
        except Exception as e:
            print(f"Error loading CSV: {str(e)}")

    def refreshPlot(self):
        if not self.dataAnalyser:
            return  # Skip if no data is loaded

        # Restrict X-axis to a single selection
        x_selected = self.xAxisListWidget.selectedItems()
        if len(x_selected) != 1:
            self.canvas.figure.clear()
            ax = self.canvas.figure.add_subplot(111)
            ax.set_title("Please select exactly one column for the X-axis")
            self.canvas.draw()
            return

        # Allow multiple selections for Y-axis
        y_selected = self.yAxisListWidget.selectedItems()
        if not y_selected:
            self.canvas.figure.clear()
            ax = self.canvas.figure.add_subplot(111)
            ax.set_title("Please select one or more columns for the Y-axis")
            self.canvas.draw()
            return

        # Extract the selected column names
        x_plot = x_selected[0].text()
        y_plots = [item.text() for item in y_selected]

        # Clear the current canvas
        self.canvas.figure.clear()

        # Make the graph wider (adjust figure dimensions)
        self.canvas.figure.set_size_inches(20, 6)

        ax = self.canvas.figure.add_subplot(111)
        try:
            # Normalize and plot Y-axis values
            for y_plot in y_plots:
                max_value = self.dataAnalyser.df[y_plot].max()
                if max_value == 0:
                    normalized_values = self.dataAnalyser.df[y_plot]  # Handle max value of zero
                else:
                    normalized_values = self.dataAnalyser.df[y_plot] / max_value
                ax.plot(self.dataAnalyser.df[x_plot], normalized_values, label=f"{y_plot} (Normalized)")
            ax.set_xlabel(x_plot)
            ax.set_ylabel("Normalized Values")
            ax.set_title("Normalized Line Graph")
            ax.legend()
            ax.grid(True)
        except Exception as e:
            print(f"Error during plotting: {e}")
            ax.set_title("Error in plotting")

        # Redraw the canvas
        self.canvas.draw()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Base, QtGui.QColor(15, 15, 15))
    palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
    palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(142, 45, 197).lighter())
    palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
    app.setPalette(palette)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())