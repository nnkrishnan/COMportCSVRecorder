from decimal import Decimal
import tkinter as tk
import tkinter.font as tkFont
import time
import serial
from datetime import datetime
import csv
import threading
from tkinter import scrolledtext

recordingStatus = False
serialPort = serial.Serial(port = "COM4", baudrate=115200,bytesize=8,stopbits=serial.STOPBITS_ONE)
now = datetime.now()

fields = ['Recording Set Number','Average', 'Values']
rows = []


def FormatSerialData(valueString):
    valueString = valueString.replace('\r', '')
    valueString = valueString.replace('\n', '')
    valueString = valueString.replace('g', '')
    valueString = valueString.replace(' ', '')
    # valueString.replace('-', '')
    return valueString
def Average(lst):
    return sum(lst) / len(lst)

def Record(app):
    count = 0
    newRow = []
    newRow.append('Recording ' + str(len(rows)))
    newRow.append(0)
    while recordingStatus:
        serialString = serialPort.readline()
        serialStringDecoded = serialString.decode('Ascii')
        if(serialStringDecoded):
            value = Decimal(FormatSerialData(serialStringDecoded))
            count += 1
            newRow.append(value)
            app.PrintCurrentRow(newRow)
        time.sleep(0.5)
    newRow[1] = Average(newRow[2:])
    rows.append(newRow)
    app.PrintCompleteRow(rows)
    message = "Recording Stopped"
    print("------- "+ message + " -------")


class App:
    def __init__(self, root):
        #setting title
        root.title("SerialDataCSVRecorder")
        #setting window size
        width=720
        height=320
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(alignstr)
        root.resizable(width=False, height=False)

        self.RecordButton=tk.Button(root)
        self.RecordButton["bg"] = "#cc0000"
        ft = tkFont.Font(family='Times',size=12)
        self.RecordButton["font"] = ft
        self.RecordButton["fg"] = "#ffffff"
        self.RecordButton["justify"] = "center"
        self.RecordButton["text"] = "Record"
        self.RecordButton.place(x=80,y=30,width=100,height=30)
        self.RecordButton["command"] = self.RecordButton_command

        self.StopButton=tk.Button(root)
        self.StopButton["bg"] = "#cc0000"
        ft = tkFont.Font(family='Times',size=12)
        self.StopButton["font"] = ft
        self.StopButton["fg"] = "#ffffff"
        self.StopButton["justify"] = "center"
        self.StopButton["text"] = "Stop"
        self.StopButton.place(x=80,y=80,width=99,height=30)
        self.StopButton["command"] = self.StopButton_command
        self.StopButton['state'] = "disabled"


        self.GenerateButton=tk.Button(root)
        self.GenerateButton["bg"] = "#ff4500"
        ft = tkFont.Font(family='Times',size=14)
        self.GenerateButton["font"] = ft
        self.GenerateButton["fg"] = "#ffffff"
        self.GenerateButton["justify"] = "center"
        self.GenerateButton["text"] = "Generate File"
        self.GenerateButton.place(x=20,y=180,width=216,height=39)
        self.GenerateButton["command"] = self.GenerateButton_command

        self.MessegeLabel=tk.Label(root)
        ft = tkFont.Font(family='Times',size=8)
        self.MessegeLabel["font"] = ft
        self.MessegeLabel["fg"] = "#333333"
        self.MessegeLabel["justify"] = "center"
        self.MessegeLabel["text"] = ""
        self.MessegeLabel.place(x=50,y=130,width=147,height=40)
        self.MessegeLabel['wraplength'] = 130
        self.MessegeLabel['justify'] = 'center'

        self.CurrentRowTexteBox=tk.Text(root)
        self.CurrentRowTexteBox.place(x=300,y=20,width=376,height=52)
        # self.CurrentRowTexteBox.insert(tk.END,"printing Rows")
        self.CurrentRowTexteBox.configure(state="disabled")

        self.CompleteTableTextBox=tk.Text(root)
        self.CompleteTableTextBox.place(x=300,y=90,width=371,height=158)
        # self.CompleteTableTextBox.insert(tk.END,"printing Rows")
        self.CompleteTableTextBox.configure(state="disabled")
        

    def RecordButton_command(self):
        global recordingStatus
        recordingStatus = True
        message = "Starting Recording"
        print("------- "+ message + " -------")
        self.MessegeLabel["text"] = message
        x = threading.Thread(target=Record, args=(self,))
        x.start()
        self.RecordButton['state'] = "disabled"
        self.StopButton['state'] = "normal"



    def PrintCurrentRow(self, row):
        self.CurrentRowTexteBox.configure(state="normal")
        self.CurrentRowTexteBox.delete('1.0', tk.END)
        self.CurrentRowTexteBox.insert(tk.END,row)
        self.CurrentRowTexteBox.configure(state="disabled")
    
    def PrintCompleteRow(self, row):
        self.CompleteTableTextBox.configure(state="normal")
        self.CompleteTableTextBox.delete('1.0', tk.END)
        self.CompleteTableTextBox.insert(tk.END,row)
        self.CompleteTableTextBox.configure(state="disabled")

    def StopButton_command(self):
        message = "Stoping Recording"
        print("------- "+ message + " -------")
        self.MessegeLabel["text"] = message
        global recordingStatus
        recordingStatus = False
        time.sleep(1)
        self.StopButton['state'] = "disabled"
        self.RecordButton['state'] = "normal"
        message = "Recording Stopped"
        self.MessegeLabel["text"] = message
        


    def GenerateButton_command(self):
        time.sleep(2)
        message = "Witing CSV file"
        print("------- "+ message + " -------")
        self.MessegeLabel["text"] = message
        nowDateTimeString =  now.strftime("%Y-%m-%d_%H-%M-%S")
        csvFilename = "Recording-" + nowDateTimeString + ".csv"
        # writing to csv file
        with open(csvFilename, 'w', newline='') as csvfile:
            # creating a csv writer object
            csvwriter = csv.writer(csvfile)
            
            # writing the fields
            csvwriter.writerow(fields)
            
            # writing the data rows
            csvwriter.writerows(rows)
        message = "file " + csvFilename + " generated"
        print("------- "+ message + " -------")
        self.MessegeLabel["text"] = message


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
