#!/usr/bin/env python3

import sys
import os
import platform
import traceback
from PySide2 import QtGui, QtCore, QtWidgets

import pandas
import matplotlib

from matplotlib.pyplot import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT

PROGRAM_PATH = os.path.realpath(os.path.dirname(__file__))
ResTableWidgetID = 0
ResPlotWidgetID = 0


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(800, 600)

        self.mdiArea = QtWidgets.QMdiArea()
        self.mdiArea.cascadeSubWindows()
        self.toolBar = QtWidgets.QToolBar()
        self.menuBar = QtWidgets.QMenuBar()

        self.setCentralWidget(self.mdiArea)
        self.setMenuBar(self.menuBar)
        self.addToolBar(self.toolBar)

        self.menuFile = QtWidgets.QMenu("&File")

        self.actionOpenFile = QtWidgets.QAction("Open file")
        self.actionOpenFile.setIcon(QtGui.QIcon(PROGRAM_PATH +
                                                "/img/open_file.png"))
        self.actionOpenFile.setShortcut(QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_O))
        self.actionOpenFile.triggered.connect(self.slot_openFile)

        self.actionExit = QtWidgets.QAction("Exit")
        self.actionExit.setIcon(QtGui.QIcon(PROGRAM_PATH + "/img/exit.png"))
        self.actionExit.setShortcut(QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_Q))
        self.actionExit.triggered.connect(self.close)

        self.menuFile.addAction(self.actionOpenFile)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)

        self.menuTable = QtWidgets.QMenu("&Table")

        self.actionSaveTable = QtWidgets.QAction("Save table")
        self.actionSaveTable.setIcon(QtGui.QIcon(PROGRAM_PATH + "/img/save_table.png"))
        self.actionSaveTable.triggered.connect(self.slot_SaveTable)

        self.actionSaveTables = QtWidgets.QAction("Save tables")
        self.actionSaveTables.setIcon(QtGui.QIcon(PROGRAM_PATH + "/img/save_tables.png"))
        self.actionSaveTables.triggered.connect(self.slot_SaveTables)

        self.menuTable.addAction(self.actionSaveTable)
        self.menuTable.addAction(self.actionSaveTables)

        self.menuPlot = QtWidgets.QMenu("&Plot")

        self.actionSavePlot = QtWidgets.QAction("Save plot")
        self.actionSavePlot.setIcon(QtGui.QIcon(PROGRAM_PATH + "/img/save_graph.png"))
        self.actionSavePlot.triggered.connect(self.slot_SavePlot)

        self.actionSavePlots = QtWidgets.QAction("Save plots")
        self.actionSavePlots.setIcon(QtGui.QIcon(PROGRAM_PATH + "/img/save_graphs.png"))
        self.actionSavePlots.triggered.connect(self.slot_SavePlots)

        self.menuPlot.addAction(self.actionSavePlot)
        self.menuPlot.addAction(self.actionSavePlots)

        self.menuWindow = QtWidgets.QMenu("&Window")

        self.actionFullScreen = QtWidgets.QAction("Full screen")
        self.actionFullScreen.setIcon(QtGui.QIcon(PROGRAM_PATH + "/img/full_screen.png"))
        self.actionFullScreen.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_F11))
        self.actionFullScreen.triggered.connect(self.slot_FullScreen)

        self.menuWindow.addAction(self.actionFullScreen)

        self.menuHelp = QtWidgets.QMenu("&Help")

        self.actionAboutProgram = QtWidgets.QAction("About program")
        self.actionAboutProgram.setIcon(QtGui.QIcon(PROGRAM_PATH + "/img/about_program.png"))
        self.actionAboutProgram.triggered.connect(self.slot_aboutProgramDialog)

        self.menuHelp.addAction(self.actionAboutProgram)

        self.toolBar.addAction(self.actionOpenFile)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionSaveTable)
        self.toolBar.addAction(self.actionSaveTables)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionSavePlot)
        self.toolBar.addAction(self.actionSavePlots)

        self.menuBar.addMenu(self.menuFile)
        self.menuBar.addMenu(self.menuTable)
        self.menuBar.addMenu(self.menuPlot)
        self.menuBar.addMenu(self.menuWindow)
        self.menuBar.addMenu(self.menuHelp)

    def closeEvent(self, event):
        event.ignore()
        if QtWidgets.QMessageBox.Yes == QtWidgets.QMessageBox.question(self, "", "Exit?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No):
            event.accept()

    @QtCore.Slot()
    def slot_FullScreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    @QtCore.Slot()
    def slot_aboutProgramDialog(self):
        aboutProgramDialog = AboutProgramDialog(self)
        aboutProgramDialog.show()

    @QtCore.Slot()
    def slot_openFile(self):
        dialogOpenFile = DialogOpenFile(self)
        vivisection = dialogOpenFile.exec()
        if vivisection == QtWidgets.QDialog.Accepted:
            self.addTable(dialogOpenFile.getInput())
        elif vivisection == QtWidgets.QDialog.Rejected:
            pass
        else:
            QtWidgets.QMessageBox.critical(self, "Critical error", "QDialog: Unexpected result")

    @QtCore.Slot()
    def slot_SaveTable(self):
        lst = []
        for it_lst in self.mdiArea.subWindowList():
            if it_lst.widget().metaObject().className() == "TableWidget":
                lst.append(it_lst)
        dialogSave = DialogSave(self, 'table', lst)
        vivisection = dialogSave.exec()
        if vivisection == QtWidgets.QDialog.Accepted:
            self.SaveFunc(dialogSave.getInput())
        elif vivisection == QtWidgets.QDialog.Rejected:
            pass
        else:
            QtWidgets.QMessageBox.critical(self, "Critical error", "QDialog: Unexpected result")

    @QtCore.Slot()
    def slot_SaveTables(self):
        lst = []
        for it_lst in self.mdiArea.subWindowList():
            if it_lst.widget().metaObject().className() == "TableWidget":
                lst.append(it_lst)
        dialogSave = DialogSave(self, 'tables', lst)
        vivisection = dialogSave.exec()
        if vivisection == QtWidgets.QDialog.Accepted:
            self.SaveSerialFunc(dialogSave.getInput())
        elif vivisection == QtWidgets.QDialog.Rejected:
            pass
        else:
            QtWidgets.QMessageBox.critical(self, "Critical error", "QDialog: Unexpected result")

    @QtCore.Slot()
    def slot_SavePlot(self):
        lst = []
        for it_lst in self.mdiArea.subWindowList():
            if it_lst.widget().metaObject().className() == "PlotWidget":
                lst.append(it_lst)
        dialogSave = DialogSave(self, 'plot', lst)
        vivisection = dialogSave.exec()
        if vivisection == QtWidgets.QDialog.Accepted:
            self.SaveFunc(dialogSave.getInput())
        elif vivisection == QtWidgets.QDialog.Rejected:
            pass
        else:
            QtWidgets.QMessageBox.critical(self, "Critical error", "QDialog: Unexpected result")

    @QtCore.Slot()
    def slot_SavePlots(self):
        lst = []
        for it_lst in self.mdiArea.subWindowList():
            if it_lst.widget().metaObject().className() == "PlotWidget":
                lst.append(it_lst)
        dialogSave = DialogSave(self, 'plots', lst)
        vivisection = dialogSave.exec()
        if vivisection == QtWidgets.QDialog.Accepted:
            self.SaveSerialFunc(dialogSave.getInput())
        elif vivisection == QtWidgets.QDialog.Rejected:
            pass
        else:
            QtWidgets.QMessageBox.critical(self, "Critical error", "QDialog: Unexpected result")

    def SaveFunc(self, lst):
        windowList = self.mdiArea.subWindowList()
        currentWindow = None
        for it_wl in windowList:
            if it_wl.windowTitle() == lst[0]:
                currentWindow = it_wl
                break
        try:
            currentWindow.widget().Save(lst[1])
        except Exception:
            QtWidgets.QMessageBox.critical(self, "Error", traceback.format_exc())
        else:
            QtWidgets.QMessageBox.information(self, "Save", "Done")

    def SaveSerialFunc(self, lst):
        windowList = self.mdiArea.subWindowList()
        currentWindow = None
        for it_lst in lst[1]:
            for it_wl in windowList:
                if it_wl.windowTitle() == it_lst:
                    currentWindow = it_wl
                    break
            try:
                currentWindow.widget().Save(lst[0] + it_lst + lst[2])
            except Exception:
                QtWidgets.QMessageBox.critical(self, "Error", traceback.format_exc())
                return
        QtWidgets.QMessageBox.information(self, "Save", "Done")

    def loadSubWindow(self, widget):
        window = self.mdiArea.addSubWindow(widget)
        window.setWindowTitle(widget.windowTitle())
        window.setWindowIcon(widget.windowIcon())
        window.resize(widget.geometry().width(), widget.geometry().height())
        window.show()

    def addPlot(self):
        w = self.mdiArea.activeSubWindow().widget()
        if w.metaObject().className() == "TableWidget":
            wl = w.get_Data()
            plotWidget = PlotWidget(self, wl[1])
            plotWidget.set_Data(wl[0])
            self.loadSubWindow(plotWidget)

    @QtCore.Slot()
    def loadPlot(self):
        self.addPlot()

    def addTable(self, lst):
        self.readData(lst)

    @QtCore.Slot(str, pandas.DataFrame)
    def loadTable(self, name, data):
        tableWidget = TableWidget(self, name)
        tableWidget.set_Data(data)
        tableWidget.actionPlot.triggered.connect(self.loadPlot)
        self.loadSubWindow(tableWidget)

    @QtCore.Slot(str)
    def errors_loadTable(self, err):
        QtWidgets.QMessageBox.critical(self, "Critical error", err)

    def readData(self, data):
        self.thread = QtCore.QThread()
        self.worker = FishThread(data[0], data[1], data[2], data[3])
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.loadTable)
        self.worker.errorSignal.connect(self.errors_loadTable)
        self.worker.quit.connect(self.thread.quit)
        self.thread.start()


class TableWidget(QtWidgets.QWidget):
    actionPlot = QtWidgets.QAction("Plot")

    def __init__(self, parent, name):
        super().__init__(parent)

        global ResTableWidgetID
        ResTableWidgetID += 1
        self.name = name.split('/')[-1]

        self.resize(300, 500)
        self.setWindowIcon(QtGui.QIcon(PROGRAM_PATH + "/img/table.png"))
        self.setWindowTitle("Table " + str(ResTableWidgetID) + ": " + self.name)

        self.tableWidget = QtWidgets.QTableWidget()

        gridLayout = QtWidgets.QGridLayout()
        gridLayout.addWidget(self.tableWidget, 0, 0)
        gridLayout.setMargin(0)

        self.setLayout(gridLayout)

        for w in (self.tableWidget.horizontalHeader(), self.tableWidget):
            w.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            w.customContextMenuRequested.connect(self.showContextMenu)

    def set_Data(self, data):
        row = 0
        for col in range(2):
            self.tableWidget.insertColumn(col)
        for it in range(len(data)):
            self.tableWidget.insertRow(row)
            self.tableWidget.setItem(row, 0, QtWidgets.QTableWidgetItem(str(data["two_theta"][row])))
            self.tableWidget.setItem(row, 1, QtWidgets.QTableWidgetItem(str(data["intensity"][row])))
            row += 1
        self.tableWidget.setHorizontalHeaderItem(0, QtWidgets.QTableWidgetItem("2θ"))
        self.tableWidget.setHorizontalHeaderItem(1, QtWidgets.QTableWidgetItem("Intensity"))

    def get_Data(self):
        data = [[], []]
        si = self.tableWidget.selectionModel().selectedIndexes()
        for it in range(len(self.tableWidget.selectionModel().selectedRows())):
            data[0].append(float(self.tableWidget.item(si[it*2].row(), 0).text()))
            data[1].append(float(self.tableWidget.item(si[it*2+1].row(), 1).text()))
        return [data, self.name]

    @QtCore.Slot()
    def showContextMenu(self, pos):
        table = self.sender()
        pos = table.viewport().mapToGlobal(pos)
        menu = QtWidgets.QMenu()
        menu.addAction(self.actionPlot)
        menu.exec_(pos)

    def Save(self,file):
        try:
            data = [[], []]
            for i in range(self.tableWidget.rowCount()):
                data[0].append(float(self.tableWidget.item(i,0).text()))
                data[1].append(float(self.tableWidget.item(i,1).text()))
            data = pandas.DataFrame({"two_theta": data[0], "intensity": data[1]})
            data.to_csv(file,index=False,sep="\t",header=True)
        except Exception:
            QtWidgets.QMessageBox.critical(self, "Save", traceback.format_exc())


class PlotWidget(QtWidgets.QWidget):
    def __init__(self, parent, title):
        super().__init__(parent)

        global ResPlotWidgetID
        ResPlotWidgetID += 1

        self.resize(600, 500)
        self.setWindowIcon(QtGui.QIcon(PROGRAM_PATH + "/img/plot.png"))
        self.setWindowTitle("Plot " + str(ResPlotWidgetID) + ": " + title)

        vBoxLayout = QtWidgets.QVBoxLayout()

        self.sc = PlotCanvas(self, width=5, height=4, dpi=100)
        toolbar = NavigationToolbar(self.sc, self)

        vBoxLayout.addWidget(toolbar)
        vBoxLayout.addWidget(self.sc)
        vBoxLayout.setMargin(0)

        self.setLayout(vBoxLayout)

    def set_Data(self, data):
        self.sc.update_figure(data)

    def set_serialData(self,listData):
        self.sc.update_serialFigure(listData)

    def Save(self,file):
        try:
            self.sc.print_figure(filename=file, dpi=300)
        except Exception:
            QtWidgets.QMessageBox.critical(self, "Save", traceback.format_exc())


class NavigationToolbar(NavigationToolbar2QT):
    toolitems = [t for t in NavigationToolbar2QT.toolitems if t[0] in ('Pan', 'Zoom', 'Subplots', 'Customize', 'Save')]


class plotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)

        self.compute_initial_figure()

        super().__init__(self.fig)
        self.setParent(parent)

        super().updateGeometry()

    def compute_initial_figure(self):
        pass


class PlotCanvas(plotCanvas):
    def __init__(self, *args, **kwargs):
        plotCanvas.__init__(self, *args, **kwargs)

    def compute_initial_figure(self):
        pass

    def update_figure(self, data):
        self.axes.cla()
        self.axes.plot(data[0], data[1])

        self.axes.set_xlabel("2θ, °")
        self.axes.set_ylabel("Intensity")

        self.axes.get_yaxis().set_ticks([])

        self.draw()

    def update_serialFigure(self,listData):
        self.axes.cla()

        for data in listData:
            self.axes.plot(data[0], data[1])

        self.axes.set_xlabel("2θ, °")
        self.axes.set_ylabel("Intensity")

        self.axes.get_yaxis().set_ticks([])

        self.draw()



class AboutProgramDialog(QtWidgets.QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.resize(500, 400)
        self.setWindowTitle("About program")

        gridLayout = QtWidgets.QGridLayout()

        hLayout = QtWidgets.QHBoxLayout()
        vLayout = QtWidgets.QVBoxLayout()

        iconLabel = QtWidgets.QLabel(self)
        iconLabel.setPixmap(QtGui.QPixmap(PROGRAM_PATH + "/img/FishX.png"))
        iconLabel.setFixedSize(120,120)
        nameLabel = QtWidgets.QLabel("<html><head/><body><p><span style=\" font-size:16pt; font-weight:600;\">" + QtCore.QCoreApplication.applicationName() + "</span></p></body></html>")
        versionLabel = QtWidgets.QLabel("Version " + QtCore.QCoreApplication.applicationVersion())

        vLayout.addSpacerItem(CustomSpacer('v'))
        vLayout.addWidget(nameLabel)
        vLayout.addWidget(versionLabel)
        vLayout.addSpacerItem(CustomSpacer('v'))
        hLayout.addWidget(iconLabel)
        hLayout.addLayout(vLayout)

        gridLayout.addLayout(hLayout, 0, 0)

        tabsWidget = QtWidgets.QTabWidget()

        tabAbout = QtWidgets.QWidget()
        labelAbout = QtWidgets.QLabel("Analysis of diffraction digital data")
        labelAbout.setWordWrap(True)
        labelAboutOwner = QtWidgets.QLabel("<html><head/><body><p>© Raven-98, 2021</p></body></html>")
        # labelAboutWEB = QtWidgets.QLabel("<html><head/><body><p><a href=\"https://github.com/Raven-98/stress-strain_diagram_builder.git\"><span style=\" text-decoration: underline; color:#2980b9;\">https://github.com/Raven-98/stress-strain_diagram_builder.git</span></a></p></body></html>")
        labelAboutLicense = QtWidgets.QLabel("<html><head/><body><p>License: GNU General Public License v3.0</p><p><a href=\"http://www.gnu.org/licenses/gpl-3.0.html\"><span style=\" text-decoration: underline; color:#2980b9;\">http://www.gnu.org/licenses/gpl-3.0.html</span></a></p></body></html>")
        boxLayoutAbout = QtWidgets.QVBoxLayout()
        boxLayoutAbout.addWidget(labelAbout)
        boxLayoutAbout.addWidget(labelAboutOwner)
        # boxLayoutAbout.addWidget(labelAboutWEB)
        boxLayoutAbout.addWidget(labelAboutLicense)
        tabAbout.setLayout(boxLayoutAbout)
        tabsWidget.addTab(tabAbout, "About")

        tabLibraries = QtWidgets.QWidget()
        labelLibraries_Python = QtWidgets.QLabel("<html><head/><body><p><br/>Python " + platform.python_version() + "</p><p><a href=\"https://www.python.org/\"><span style=\" text-decoration: underline; color:#2980b9;\">https://www.python.org/</span></a></p></body></html>")
        labelLibraries_PySide = QtWidgets.QLabel("<html><head/><body><p><br/>Qt for Python (PySide) " + QtCore.qVersion() + "</p><p><a href=\"https://www.qt.io/\"><span style=\" text-decoration: underline; color:#2980b9;\">https://www.qt.io/</span></a></p></body></html>")
        labelLibraries_pandas = QtWidgets.QLabel("<html><head/><body><p><br/>pandas " + pandas.__version__ + "</p><p><a href=\"https://pandas.pydata.org/\"><span style=\" text-decoration: underline; color:#2980b9;\">https://pandas.pydata.org/</span></a></p></body></html>")
        labelLibraries_Matplotlib = QtWidgets.QLabel("<html><head/><body><p><br/>Matplotlib " + matplotlib.__version__ + "</p><p><a href=\"https://matplotlib.org/\"><span style=\" text-decoration: underline; color:#2980b9;\">https://matplotlib.org/</span></a></p></body></html>")
        boxLayoutLibraries = QtWidgets.QVBoxLayout()
        boxLayoutLibraries.addWidget(labelLibraries_Python)
        boxLayoutLibraries.addWidget(labelLibraries_PySide)
        boxLayoutLibraries.addWidget(labelLibraries_pandas)
        boxLayoutLibraries.addWidget(labelLibraries_Matplotlib)
        tabLibraries.setLayout(boxLayoutLibraries)
        tabsWidget.addTab(tabLibraries, "Platforms and libraries")

        tabAuthors = QtWidgets.QWidget()
        labelAuthors_Raven98 = QtWidgets.QLabel("<html><head/><body><p><span style=\" font-weight:600;\">Raven-98</span></p><p><span style=\" font-style:italic;\">Developer</span></p><p>E-mail: <a href=\"andriy1898k@hotmail.com\"><span style=\" text-decoration: underline; color:#2980b9;\">andriy1898k@hotmail.com</span></a></p></body></html>")
        boxLayoutAuthors = QtWidgets.QVBoxLayout()
        boxLayoutAuthors.addWidget(labelAuthors_Raven98)
        tabAuthors.setLayout(boxLayoutAuthors)
        tabsWidget.addTab(tabAuthors, "Authors")

        gridLayout.addWidget(tabsWidget, 1, 0)

        self.setLayout(gridLayout)


class DialogOpenFile(QtWidgets.QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.resize(450, 200)
        self.setWindowTitle("Open file")

        self.sett = QtCore.QSettings(PROGRAM_PATH + "/settings.ini", QtCore.QSettings.IniFormat)

        self.labelFile = QtWidgets.QLabel("File:")
        self.lineEditFile = QtWidgets.QLineEdit()
        self.lineEditFile.setText(self.sett.value("DialogOpenFile/file"))
        self.pushButtonOpen = QtWidgets.QPushButton("Open")
        self.pushButtonOpen.clicked.connect(self.slot_openFile)

        self.labelTwoThetaStart = QtWidgets.QLabel("<html><head/><body><p align=\"right\">2θ<span style=\" vertical-align:sub;\">start</span>:</p></body></html>")
        self.labelTwoThetaEnd = QtWidgets.QLabel("<html><head/><body><p align=\"right\">2θ<span style=\" vertical-align:sub;\">end</span>:</p></body></html>")
        self.lineEditTwoThetaStart = QtWidgets.QLineEdit()
        self.lineEditTwoThetaStart.setText(self.sett.value("DialogOpenFile/two_theta_start"))
        self.lineEditTwoThetaEnd = QtWidgets.QLineEdit()
        self.lineEditTwoThetaEnd.setText(self.sett.value("DialogOpenFile/two_theta_end"))

        self.labelDelimiter = QtWidgets.QLabel("Delimiter")
        self.comboBoxDelimiter = QtWidgets.QComboBox()
        self.comboBoxDelimiter.addItems(("Comma", "Tab step", "Semicolon", "Space"))
        vivisection = self.sett.value("DialogOpenFile/delimiter")
        if vivisection == ",":
            self.comboBoxDelimiter.setCurrentIndex(0)
        elif vivisection == "\t":
            self.comboBoxDelimiter.setCurrentIndex(1)
        elif vivisection == ";":
            self.comboBoxDelimiter.setCurrentIndex(2)
        elif vivisection == " ":
            self.comboBoxDelimiter.setCurrentIndex(3)

        self.buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.horizontalBoxLayout_openFile = QtWidgets.QHBoxLayout()
        self.horizontalBoxLayout_openFile.addWidget(self.labelFile)
        self.horizontalBoxLayout_openFile.addWidget(self.lineEditFile)
        self.horizontalBoxLayout_openFile.addWidget(self.pushButtonOpen)

        self.horizontalBoxLayout_TwoTheta = QtWidgets.QHBoxLayout()
        self.horizontalBoxLayout_TwoTheta.addWidget(self.labelTwoThetaStart)
        self.horizontalBoxLayout_TwoTheta.addWidget(self.lineEditTwoThetaStart)
        self.horizontalBoxLayout_TwoTheta.addWidget(self.labelTwoThetaEnd)
        self.horizontalBoxLayout_TwoTheta.addWidget(self.lineEditTwoThetaEnd)

        self.horizontalBoxLayout_Delimiter = QtWidgets.QHBoxLayout()
        self.horizontalBoxLayout_Delimiter.addWidget(self.labelDelimiter)
        self.vBoxLayout_Delimiter = QtWidgets.QVBoxLayout()
        self.vBoxLayout_Delimiter.addWidget(self.comboBoxDelimiter)
        self.vBoxLayout_Delimiter.addSpacerItem(CustomSpacer('h'))
        self.horizontalBoxLayout_Delimiter.addLayout(self.vBoxLayout_Delimiter)

        self.verticalBoxLayout = QtWidgets.QVBoxLayout()
        self.verticalBoxLayout.addSpacerItem(CustomSpacer('v'))
        self.verticalBoxLayout.addLayout(self.horizontalBoxLayout_openFile)
        self.verticalBoxLayout.addSpacerItem(CustomSpacer('v'))
        self.verticalBoxLayout.addLayout(self.horizontalBoxLayout_TwoTheta)
        self.verticalBoxLayout.addSpacerItem(CustomSpacer('v'))
        self.verticalBoxLayout.addLayout(self.horizontalBoxLayout_Delimiter)
        self.verticalBoxLayout.addSpacerItem(CustomSpacer('v'))
        self.verticalBoxLayout.addWidget(self.buttonBox)

        self.setLayout(self.verticalBoxLayout)

    @QtCore.Slot()
    def accept(self):
        if self.lineEditFile.text() == "":
            QtWidgets.QMessageBox.warning(self, "Warning", "The \"File\" field cannot be empty")
            return
        if self.lineEditTwoThetaStart.text() == "":
            QtWidgets.QMessageBox.warning(self, "Warning", "<html><head/><body><p align=\"right\">The \"2θ<span style=\" vertical-align:sub;\">start</span>\" field cannot be empty</p></body></html>")
            return
        if self.lineEditTwoThetaEnd.text() == "":
            QtWidgets.QMessageBox.warning(self, "Warning", "<html><head/><body><p align=\"right\">The \"2θ<span style=\" vertical-align:sub;\">end</span>\" field cannot be empty</p></body></html>")
            return

        super().accept()

    @QtCore.Slot()
    def slot_openFile(self):
        self.lineEditFile.setText(QtWidgets.QFileDialog.getOpenFileName(self, "Open file", self.sett.value("DialogOpenFile/file"), "All files(*.*);;CSV files(*.csv);;Text files(*.txt)")[0])

    def getInput(self):
        delimiter = None

        vivisection = self.comboBoxDelimiter.currentIndex()
        if vivisection == 0:
            delimiter = ","
        elif vivisection == 1:
            delimiter = "\t"
        elif vivisection == 2:
            delimiter = ";"
        elif vivisection == 3:
            delimiter = " "

        self.sett.setValue("DialogOpenFile/file", self.lineEditFile.text())
        self.sett.setValue("DialogOpenFile/delimiter", delimiter)
        self.sett.setValue("DialogOpenFile/two_theta_start", self.lineEditTwoThetaStart.text())
        self.sett.setValue("DialogOpenFile/two_theta_end", self.lineEditTwoThetaEnd.text())

        return [self.lineEditFile.text(), delimiter, self.lineEditTwoThetaStart.text(), self.lineEditTwoThetaEnd.text()]


class DialogSave(QtWidgets.QDialog):
    def __init__(self, parent, pattern, lst):
        super().__init__(parent)

        self.pattern = pattern

        self.resize(400, 200)
        self.setWindowTitle("Save " + self.pattern)

        self.sett = QtCore.QSettings(PROGRAM_PATH + "/settings.ini", QtCore.QSettings.IniFormat)

        self.vBoxLayout = QtWidgets.QVBoxLayout()

        self.hBoxLayoutName = QtWidgets.QHBoxLayout()
        self.hBoxLayoutPath = QtWidgets.QHBoxLayout()
        self.vBoxLayoutCustom = QtWidgets.QVBoxLayout()
        self.hBoxLayoutFormat = QtWidgets.QHBoxLayout()

        self.labelPath = QtWidgets.QLabel("Path")
        self.lineEditPath = QtWidgets.QLineEdit()
        self.lineEditPath.setText(self.sett.value("DialogSave/path"))
        self.pushButtonPath = QtWidgets.QPushButton(QtGui.QIcon(PROGRAM_PATH + "/img/open_path.png"), "")
        self.pushButtonPath.clicked.connect(self.slot_ButtonPath)

        self.hBoxLayoutPath.addWidget(self.labelPath)
        self.hBoxLayoutPath.addWidget(self.lineEditPath)
        self.hBoxLayoutPath.addWidget(self.pushButtonPath)

        self.labelFormat = QtWidgets.QLabel("Format")
        self.comboBoxFormat = QtWidgets.QComboBox()

        self.vBoxLayoutFormat = QtWidgets.QVBoxLayout()
        self.vBoxLayoutFormat.addWidget(self.comboBoxFormat)
        self.vBoxLayoutFormat.addSpacerItem(CustomSpacer('h'))

        self.hBoxLayoutFormat.addWidget(self.labelFormat)
        self.hBoxLayoutFormat.addLayout(self.vBoxLayoutFormat)

        if self.pattern == 'table' or self.pattern == 'plot':
            self.labelFileName = QtWidgets.QLabel("Name")
            self.lineEditFileName = QtWidgets.QLineEdit()
            self.lineEditFileName.setText(self.sett.value("DialogSave/file_name"))
            self.pushButtonFileName = QtWidgets.QPushButton(QtGui.QIcon(PROGRAM_PATH + "/img/file.png"), "")
            self.pushButtonFileName.clicked.connect(self.slot_ButtonFileName)

            self.hBoxLayoutName.addWidget(self.labelFileName)
            self.hBoxLayoutName.addWidget(self.lineEditFileName)
            self.hBoxLayoutName.addWidget(self.pushButtonFileName)

            self.comboBoxWindows = QtWidgets.QComboBox()
            nlst = [it_lst.widget().windowTitle() for it_lst in lst]
            self.comboBoxWindows.addItems(nlst)

            self.vBoxLayoutCustom.addWidget(self.comboBoxWindows)
        elif self.pattern == 'tables' or self.pattern == 'plots':
            self.groupBox = QtWidgets.QGroupBox()
            self.groupBox.setFlat(True)
            scrollArea = QtWidgets.QScrollArea()
            layout = QtWidgets.QVBoxLayout()
            for it_lst in lst:
                radioButton = QtWidgets.QCheckBox(it_lst.widget().windowTitle())
                layout.addWidget(radioButton)
            self.groupBox.setLayout(layout)
            scrollArea.setWidget(self.groupBox)
            scrollArea.setWidgetResizable(True)
            self.vBoxLayoutCustom.addWidget(scrollArea)

        i = None
        if self.pattern == 'table' or self.pattern == 'tables':
            self.comboBoxFormat.addItems(("DAT file (*.dat)", "CSV file (*.csv)", "Text file (*.txt)"))
            i = self.sett.value("DialogSave/format_table")
        elif self.pattern == 'plot' or self.pattern == 'plots':
            self.comboBoxFormat.addItems(("JPEG file (*.jpg)", "PNG file (*.png)"))
            i = self.sett.value("DialogSave/format_plot")
        if i == None:
            self.comboBoxFormat.setCurrentIndex(0)
        else:
            self.comboBoxFormat.setCurrentIndex(int(i))

        if self.pattern == 'tables':
            self.groupBox.setTitle("Tables")
        elif self.pattern == 'plots':
            self.groupBox.setTitle("Plots")

        self.buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        if self.pattern == 'table' or self.pattern == 'plot':
            self.vBoxLayout.addSpacerItem(CustomSpacer('v'))
            self.vBoxLayout.addLayout(self.hBoxLayoutName)
        self.vBoxLayout.addSpacerItem(CustomSpacer('v'))
        self.vBoxLayout.addLayout(self.hBoxLayoutPath)
        self.vBoxLayout.addSpacerItem(CustomSpacer('v'))
        self.vBoxLayout.addLayout(self.vBoxLayoutCustom)
        self.vBoxLayout.addSpacerItem(CustomSpacer('v'))
        self.vBoxLayout.addLayout(self.hBoxLayoutFormat)
        self.vBoxLayout.addSpacerItem(CustomSpacer('v'))
        self.vBoxLayout.addWidget(self.buttonBox)

        self.setLayout(self.vBoxLayout)

    def getInput(self):
        self.sett.setValue("DialogSave/path", self.lineEditPath.text())
        if self.pattern == 'table' or self.pattern == 'tables':
            self.sett.setValue("DialogSave/format_table",self.comboBoxFormat.currentIndex())
        elif self.pattern == 'plot' or self.pattern == 'plots':
            self.sett.setValue("DialogSave/format_plot",self.comboBoxFormat.currentIndex())

        if self.pattern == 'table' or self.pattern == 'plot':
            self.sett.setValue("DialogSave/file_name", self.lineEditFileName.text())
            file = self.lineEditPath.text() + '/' + self.lineEditFileName.text() + self.comboBoxFormat.currentText().split('*')[-1][:-1]
            return [self.comboBoxWindows.currentText(), file]
        elif self.pattern == 'tables' or self.pattern == 'plots':
            path = self.lineEditPath.text() + '/'
            files = []
            for checkbox in self.groupBox.findChildren(QtWidgets.QCheckBox):
                if checkbox.isChecked():
                    files.append(checkbox.text())
            return [path, files, self.comboBoxFormat.currentText().split('*')[-1][:-1]]

    @QtCore.Slot()
    def slot_ButtonFileName(self):
        text = QtWidgets.QFileDialog.getOpenFileName(self, "Get file name", self.lineEditPath.text(), "All files(*.*)")[0].split("/")[-1]
        text = text.split('.' + text.split('.')[-1])[0]
        self.lineEditFileName.setText(text)

    @QtCore.Slot()
    def slot_ButtonPath(self):
        self.lineEditPath.setText(QtWidgets.QFileDialog.getExistingDirectory(self, "Get file name", self.lineEditPath.text()))


class CustomSpacer(QtWidgets.QSpacerItem):
    def __init__(self, orientation):
        if orientation == 'v':
            super().__init__(0, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        elif orientation == 'h':
            super().__init__(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)


class FishThread(QtCore.QObject):
    finished = QtCore.Signal(str, pandas.DataFrame)
    quit = QtCore.Signal()
    errorSignal = QtCore.Signal(str)

    def __init__(self, file_name, separator, min_A, max_A):
        super().__init__()

        self.file_name = file_name
        self.separator = separator
        self.min_A = float(min_A)
        self.max_A = float(max_A)

    def run(self):
        try:
            data = pandas.read_csv(self.file_name, sep=self.separator)
            minIndex = 0
            n = len(data)-1
            two_theta = [self.min_A + i * ((self.max_A-self.min_A)/(n-1)) for i in range(minIndex, n)]
            intensity = [float(data['Value'][i + 1]) for i in range(minIndex, n)]
            two_theta_n = ["%.3f" % (two_theta[i] - (0.544+0.000599591 * two_theta[i])) for i in range(1, n)]
            intensity_n = [intensity[i] for i in range(minIndex, n-1)]

            Data = pandas.DataFrame({'two_theta': two_theta_n, 'intensity': intensity_n})
        except Exception:
            self.errorSignal.emit(traceback.format_exc())
        else:
            self.finished.emit(self.file_name, Data)
        finally:
            self.quit.emit()


def main():
    app = QtWidgets.QApplication(sys.argv)

    app.setApplicationName("FishX")
    app.setApplicationVersion("1.0.0")
    app.setWindowIcon(QtGui.QIcon(PROGRAM_PATH + "/img/FishX.png"))

    win = MainWindow()
    win.show()

    ####
    win.slot_openFile()
    ####

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
