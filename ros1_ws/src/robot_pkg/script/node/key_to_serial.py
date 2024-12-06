import serial
#import time
#Arduino serial communication module for TTL signal
#This program is for python 2.7

def openArduino():
    global Ser
    Ser=serial.Serial('/dev/ttyACM0',9600,timeout=3)
    print Ser.readline()
    #time.sleep(1)

def writeArduino(Message):
    Ser.write(Message.encode())

def closeArduino(): 
    Ser.close()

if __name__ == '__main__':
    openArduino()
    mes=raw_input("Input message:")
    #mes='1'でTTL信号が生じる
    writeArduino(mes)
    closeArduino()