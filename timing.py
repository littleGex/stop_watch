# -*- coding: utf-8 -*-
import sys
import os
import pandas as pd
from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtWidgets import QMainWindow, QAction, QMessageBox, QFileDialog, QCheckBox, QGroupBox, QApplication, QTableWidgetItem, QTableWidget, QLineEdit, QDialog
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QSettings, QTimer
import inspect
import datetime

import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


#============================================================================================================
class Stopwindow (QMainWindow):
    def __init__(self):
        super(Stopwindow, self).__init__()
        uic.loadUi('stop.ui', self)
        self.setupui()
        self.set_menu() 
        self.location()

    def setupui(self):
        self.setStyleSheet("""
            QPushButton:hover {background-color: LightCyan;
            }
            QLineEdit:hover {background-color: AliceBlue;
            }
            QTabBar::tab:selected {background: Lightgrey;
            }
            QTabWidget>QWidget>QWidget{background: Lightgrey;
            }
                           """)
        # self.tabWidget.setStyleSheet('QTabBar::tab {background-color: red;}')
        self.tabWidget.setCurrentIndex(0)
        self.figure = Figure()
        
        #FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.canvas = FigureCanvas(self.figure)

        self.toolbar = NavigationToolbar(self.canvas, self)  

        self.plotlayout.addWidget(self.toolbar)

        self.plotlayout.addWidget(self.canvas) 
        
        self.timer = QTimer(self)
        # print(QtCore.QTimer.timerType(QtCore.QTimer(self)))
        # self.timer.setTimerType(4)
        self.timer.timeout.connect(self.run_watch)
        self.timer.setInterval(1) # milliseconds
        # self.timer.setInterval(1000) # seconds
        self.mscounter = 0
        self.isreset = True
        self.showLCD()
        
        #============================================================================================================       
        self.pushButtonReset.released.connect(self.watch_reset)
        self.pushButtonStart.released.connect(self.watch_start)
        self.pushButtonStop.released.connect(self.watch_stop)
        self.pushButtonPause.released.connect(self.watch_pause)
        self.pushButtonAdd.released.connect(self.Add)
        self.pushButtonRemove.released.connect(self.Remove)
        self.pushButtonCommit.released.connect(self.commit)
        self.pushButtonExport.released.connect(self.saveCSV)

        #============================================================================================================       
        self.tableWidget.setStyleSheet("border: 1px solid grey; border-radius: 3px; font: EADS Sans; font-size: 10;")
        self.tableWidget.setRowCount(1)
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setHorizontalHeaderLabels(('Project', 'Time on project'))    
        self.tableWidget.cellChanged.connect(self.row)
        
        # self.location()
        self.combo()

        #============================================================================================================
    def set_menu (self):
        main_menu = self.menuBar()
        main_menu.setNativeMenuBar(False) #needed for mac
       
        file_menu = main_menu.addMenu('File')

        new_session = QAction("New", self)
        new_session.setShortcut("Ctrl+N")
        new_session.setStatusTip("Click to start new session")
        file_menu.addAction(new_session)
        new_session.triggered.connect(self.newSession)     

        save_csv = QAction("Save project list as CSV", self)
        save_csv.setShortcut("Ctrl+C")
        save_csv.setStatusTip("Click to save CSV")
        file_menu.addAction(save_csv)
        save_csv.triggered.connect(self.saveCSV) 

        print = QAction("Print", self)
        print.setShortcut("Ctrl+P")
        print.setStatusTip("Click to print Plot")
        file_menu.addAction(print)
        print.triggered.connect(self.Print)

        quit = QAction("Quit", self)
        quit.setShortcut("Ctrl+Q")
        quit.setStatusTip("Click to Exit")
        file_menu.addAction(quit)
        quit.triggered.connect(self.closeSession)

        session_menu = main_menu.addMenu('Session')
        
        save_session = QAction("Save session", self)
        save_session.setShortcut("Ctrl+S")
        save_session.setStatusTip("Click to save session")
        session_menu.addAction(save_session)
        save_session.triggered.connect(self.saveSession) 
        
        restore_session = QAction("Restore session", self)
        restore_session.setShortcut("Ctrl+R")
        restore_session.setStatusTip("Click to restore session")
        session_menu.addAction(restore_session)
        restore_session.triggered.connect(self.restoreSession)
        
        #============================================================================================================        
    def location(self):
        self.location = (os.path.join(os.path.join(os.path.expanduser('~')), 'Documents', 'Timer'))
        if os.path.exists(self.location):
            print('Location exists')
        else:
            os.makedirs(self.location)
        
        msg = QMessageBox.question(self, 'restore session',
                                    'Do you want to restore a previous session?',
                                    QMessageBox.Yes | QMessageBox.No)
        if msg == QMessageBox.Yes:
            self.restoreSession()
        if msg == QMessageBox.No:
            pass

        #============================================================================================================        
    def browse_folder_file( self ):
        ''' Called when the user presses the Browse button
        '''
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,
                                                  "Choose file to import",
                                                  os.sep.join((os.path.expanduser('~'), 'Desktop')),
                                                  'CSV files (*.csv)',
                                                  options=options)
        if fileName:
            self.lineEdit.setText(fileName)
            
        #============================================================================================================               
    def row(self):
        # numRow = self.tableWidget.rowCount()
        # self.tableWidget.insertRow(numRow)
        
        self.load()
        # pass
        
        #============================================================================================================               
    def combo(self, poscol=0):
        num_of_rows = self.tableWidget.rowCount()
        # print(num_of_rows)
        b=[]
        for row in range(num_of_rows):
            df_list2= []
            table_item = self.tableWidget.item(row,poscol)
            df_list2.append('' if table_item is None else str(table_item.text()))
            b.append(str(df_list2).strip('[]').strip("'"))
            # print(b)
            self.comboBox.clear()
            # self.comboBox.addItems(b)
            for word in b:
                self.comboBox.addItem(word)

        #============================================================================================================               
    def commit(self):        
        # for row in range(self.tableWidget.rowCount()):
        #     for column in range(self.tableWidget.columnCount()):
        #         item = self.tableWidget.item(row, column)
        #         if item and item.data (QtCore.Qt.DisplayRole) == str(self.comboBox.currentText()):
        #             location = (self.tableWidget.indexFromItem(item))
        #             print(location)
        
        # self.lcdNumber.value()
        # print(self.lcdNumber.digitCount())
        # date_time_obj = datetime.timedelta(self.lcdNumber.value())
        # print(date_time_obj)
        # print(self.a)
        
        items = self.tableWidget.findItems(self.comboBox.currentText(), QtCore.Qt.MatchExactly)
        # if items:
        #     results = '\n'.join('row %d column %d' % (item.row(), item.column())for item in items)
        # else:
        #     results = 'Found Nothing'
            
        # QMessageBox.information(self, 'Search Results', results)
        
        if items:
            for item in items:
                location = item.row()
                # print(item.row())
            
            itam = self.tableWidget.item(location,1)
            a_name = '0:00:00.000' if itam is None else itam.text() # milliseconds
            # a_name = '0:00:00' if itam is None else itam.text() # seconds
            tList = [a_name, self.a]
            # print(tList)
            
            sum = datetime.timedelta()
            for i in tList:
                (h, m, s) = i.split(':')
                d = datetime.timedelta(hours=int(h), minutes=int(m), seconds=float(s))
                sum += d
            # print(str(sum))
            
        self.tableWidget.setItem(location, 1, QTableWidgetItem(str(sum)[:-3]))

        #============================================================================================================               
    def showLCD(self):
        text = str(datetime.timedelta(milliseconds=self.mscounter))[:-3] # Milliseconds
        # text = str(datetime.timedelta(seconds=self.mscounter)) # seconds
        # print(text)
        self.a=text
        self.lcdNumber.setDigitCount(11) # milliseconds
        # self.lcdNumber.setDigitCount(7) # seconds
        if not self.isreset:  # if "isreset" is False
            self.lcdNumber.display(text)
        else:
            self.lcdNumber.display('0:00:00.000') # milliseconds
            # self.lcdNumber.display('0:00:00') # seconds
    
    def run_watch(self):
        self.mscounter += 1
        self.showLCD()
            
    def watch_start(self):
        self.timer.start()
        self.isreset = False
        self.pushButtonReset.setDisabled(True)
        self.pushButtonStart.setDisabled(True)
        self.pushButtonStop.setDisabled(False)
        self.pushButtonPause.setDisabled(False)

    def watch_stop(self):
        self.timer.stop()
        # self.mark_time()
        self.mscounter = 0

        self.pushButtonReset.setDisabled(False)
        self.pushButtonStart.setDisabled(False)
        self.pushButtonStop.setDisabled(True)
        self.pushButtonPause.setDisabled(True)

    def watch_pause(self):
        self.timer.stop()

        self.pushButtonReset.setDisabled(False)
        self.pushButtonStart.setDisabled(False)
        self.pushButtonStop.setDisabled(True)
        self.pushButtonPause.setDisabled(True)

    def watch_reset(self):
        self.timer.stop()
        self.mscounter = 0
        self.isreset = True
        self.showLCD()

        self.pushButtonReset.setDisabled(True)
        self.pushButtonStart.setDisabled(False)
        self.pushButtonStop.setDisabled(True)
        self.pushButtonPause.setDisabled(True)

        #============================================================================================================
    def load (self):
        num_of_rows = self.tableWidget.rowCount()
        num_of_col = self.tableWidget.columnCount()
        headers = [str(self.tableWidget.horizontalHeaderItem(i).text())for i in range(num_of_col)]
        
        df_list = []
        for row in range(num_of_rows):
            df_list2= []
            for col in range(num_of_col):
                table_item = self.tableWidget.item(row, col)
                df_list2.append('' if table_item is None else str(table_item.text()))
            df_list.append(df_list2)
        
        df = pd.DataFrame(df_list, columns=headers)
        
        # df['Time on project']=pd.to_numeric(df['Time on project'])
        df['Time on project']=pd.to_datetime(df['Time on project'])
        # df['Time on project'] = df['Time on project'].apply(lambda x: datetime.datetime.strftime(x, "%H:%M:%S.%f")[:-3])
        # df['Time on project'] = df['Time on project'].astype('datetime64')
        # print (df)
        # print(df.dtypes)
        # return df
        
        df['hours'] = (df['Time on project'].dt.hour + df['Time on project'].dt.minute/60 + df['Time on project'].dt.second/3600).round(decimals=4)
        
        self.plot(df)   

        #============================================================================================================     
    def plot (self, df):
        ax = self.figure.add_subplot(111)
        ax.clear()
        
        # df.plot.bar(x='Project',y='Time on project', ax=ax)
        # df.plot(x='Project',y='Time on project', ax=ax, marker='*')
        # df.plot(x='Project',y='hours', ax=ax, marker='*') # Line graph
        df.plot(kind='bar', x='Project',y='hours', ax=ax) # bar chart
        
        for tick in ax.get_xticklabels():
            tick.set_rotation(90)
        
        leg= ax.legend(prop={'size':8}, loc='center left', bbox_to_anchor=(1,0.5))
        if leg:
            leg.set_draggable(True)

        ax.set_ylabel('Time (hours)')

        # Add major and Minor gridlines
        # Customize the major grid
        ax.grid(which='major', linestyle=':', linewidth='0.5', color='grey')
        # Customize the minor grid
        ax.grid(which='minor', linestyle=':', linewidth='0.5', color='grey')

        self.figure.tight_layout()

        plt.isinteractive()      

        self.canvas.draw()

        #============================================================================================================
    def closeSession (self):
        choice = QMessageBox.question(self, 'Close',
                                            "Do you want to quit the application?",
                                            QMessageBox.Yes | QMessageBox.No)
        if choice == QMessageBox.Yes:
            msg = QMessageBox.question(self, 'Save Session',
                                       "Do you want to save the session before quiting?",
                                       QMessageBox.Yes | QMessageBox.No)
            if msg == QMessageBox.Yes:
                self.saveSession()
                print("Session closed")
                sys.exit()
            if msg == QMessageBox.No:
                print("Session closed")
                sys.exit()
        if choice == QMessageBox.No:
            pass

        #============================================================================================================        
    def Print (self):
        filename,_ = QFileDialog.getSaveFileName(self, "Save plots as PDF file", (os.path.join(os.path.join(os.path.expanduser('~')), 'Documents', 'Timer')), "Portable Document File (*.pdf)")
        if filename == "":
            return
        self.canvas.print_figure(filename)

        #============================================================================================================        
    def saveSession(self):
        self.fname, _ = QFileDialog.getSaveFileName(self, 'Select save session name', (os.path.join(os.path.join(os.path.expanduser('~')), 'Documents', 'Timer')), 'INI files (*.ini)')
        self.settings = QSettings(self.fname, QSettings.IniFormat)
        
        for name, obj in inspect.getmembers(self):
            if isinstance(obj, QLineEdit):
                name = obj.objectName()
                value = obj.text()
                self.settings.setValue(name, value)
            if isinstance(obj, QCheckBox):
                name = obj.objectName()
                state = obj.isChecked()
                self.settings.setValue(name, state)
            if isinstance(obj, QGroupBox):
                name = obj.objectName()
                state = obj.isChecked()
                self.settings.setValue(name, state)
            if isinstance(obj, QTableWidget):
                self.settings.setValue("rowCount", obj.rowCount())
                self.settings.setValue("columnCount", obj.columnCount())
                items = QtCore.QByteArray()
                stream = QtCore.QDataStream(items, QtCore.QIODevice.WriteOnly)
                for i in range(obj.rowCount()):
                    for j in range(obj.columnCount()):
                        it = obj.item(i,j)
                        if it is not None:
                            stream.writeInt(i)
                            stream.writeInt(j)
                            stream << it
                self.settings.setValue("items", items)
                selecteditems = QtCore.QByteArray()
                stream = QtCore.QDataStream(selecteditems, QtCore.QIODevice.WriteOnly)
                for it in obj.selectedItems():
                    stream.writeInt(it.row())
                    stream.writeInt(it.column())
                self.settings.setValue("selecteditems", selecteditems)
#        print(self.fname)

    #read in previous session links and settings
    def restoreSession(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Select session to restore', (os.path.join(os.path.join(os.path.expanduser('~')), 'Documents', 'Timer')), 'INI files (*.ini)')
        if not os.path.exists(fname):
            return
        self.settings = QSettings(fname, QSettings.IniFormat)
        for name, obj in inspect.getmembers(self):
            if isinstance(obj, QLineEdit):
                name = obj.objectName()
                value = (self.settings.value(name))
                obj.setText(value)  # restore
            # if isinstance(obj, QCheckBox):
            #     name = obj.objectName()
            #     value = self.settings.value(name).lower()
            #     if value != None:
            #         obj.setChecked(strtobool(value))
            #     else:
            #         continue
            # if isinstance(obj, QGroupBox):
            #     name = obj.objectName()
            #     value = self.settings.value(name).lower()
            #     if value != None:
            #         obj.setChecked(strtobool(value))
            #     else:
            #         continue
            if isinstance(obj, QTableWidget):
                rowCount = self.settings.value("rowCount", type=int)
                columnCount = self.settings.value("columnCount", type=int)
                obj.setRowCount(rowCount)
                obj.setColumnCount(columnCount)
                items = self.settings.value("items")
                if items is None:
                    continue
                else:
                    stream = QtCore.QDataStream(items, QtCore.QIODevice.ReadOnly)
                    while not stream.atEnd():
                        it = QtWidgets.QTableWidgetItem()
                        i = stream.readInt()
                        j = stream.readInt()
                        stream >> it
                        obj.setItem(i, j, it)
                    selecteditems = self.settings.value("selecteditems")
                    stream = QtCore.QDataStream(selecteditems, QtCore.QIODevice.ReadOnly)
                    while not stream.atEnd():
                        i = stream.readInt()
                        j = stream.readInt()
                        it = obj.item(i, j)
                        if it is not None:
                            it.setSelected(True)
            
        #============================================================================================================        
    def newSession (self):
        # reset timer
        self.watch_reset()
        
        # clear all fields to allow new data to be loaded - issue with clearing plot still though
        self.lineEdit.clear()

        self.tableWidget.clear()
        self.tableWidget.setRowCount(1)
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setHorizontalHeaderLabels(('Project', 'Time on project')) 
        
        self.tableWidget.setItem(0, 0, QTableWidgetItem('Project A'))
        
        self.combo()

        #============================================================================================================            
    def Add (self):
        # get file name and add it to the table view
        a = self.lineEdit.text()

        # Create empty row at bottom of table
        numRows = self.tableWidget.rowCount()

        self.tableWidget.insertRow(numRows)

        # Add text to row
        self.tableWidget.setItem(numRows, 0, QTableWidgetItem(a))
        
        self.combo()
        
        self.lineEdit.clear()

        #============================================================================================================            
    def Remove (self):
        # Remove selected row from table
        self.tableWidget.removeRow(self.tableWidget.currentRow())

        #============================================================================================================
    def saveCSV (self):
        num_of_rows = self.tableWidget.rowCount()
        num_of_col = self.tableWidget.columnCount()
        headers = [str(self.tableWidget.horizontalHeaderItem(i).text())for i in range(num_of_col)]
        
        df_list = []
        for row in range(num_of_rows):
            df_list2= []
            for col in range(num_of_col):
                table_item = self.tableWidget.item(row, col)
                df_list2.append('' if table_item is None else str(table_item.text()))
            df_list.append(df_list2)
        
        df = pd.DataFrame(df_list, columns=headers)
        
        df['Time on project']=pd.to_datetime(df['Time on project'])
        # df['Time on project'] = df['Time on project'].apply(lambda x: datxetime.datetime.strftime(x, "%H:%M:%S.%f")[:-3])
        
        df['hr'] = df['Time on project'].dt.hour
        df['mn'] = df['Time on project'].dt.minute
        df['sec'] = df['Time on project'].dt.second

        df['minutes'] = df['Time on project'].dt.hour * 60 + df['Time on project'].dt.minute + df['Time on project'].dt.second/60

        df['hours'] = (df['Time on project'].dt.hour + df['Time on project'].dt.minute/60 + df['Time on project'].dt.second/3600).round(decimals=4)
        # df['time_hour'] = df['Time on project'].dt.time
        

        #Save csv file to allow reload/reuse
        filename,_ = QFileDialog.getSaveFileName(self, "Save dataframe", (os.path.join(os.path.join(os.path.expanduser('~')), 'Documents', 'Timer')), "CSV files (*.csv)")
        df.to_csv(filename, index=False)

#============================================================================================================
if __name__=="__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = Stopwindow()
    MainWindow.show ()
    sys.exit(app.exec_())
    