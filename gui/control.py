#!/usr/bin/python

# simple.py

import sys
from random import randint
from time import sleep, time

from PyQt4.QtGui import *
from PyQt4.QtCore import *
import serial



class RGButton(QPushButton):
    def __init__(self, app):
        QPushButton.__init__(self)
        self.app = app

    def nextCheckState(self):
        self.change()

    def change(self, color=None):
        if color is not None:
            self.color = color
            if self.color <= 0x01:
                self.color = 0x01
            elif self.color >= 0x04:
                self.color = 0x04
        else:
            if self.color >= 0x04:
                self.color = 0x01
            else:
                self.color = self.color + 1

        colors = {0x01: '#ff0000', 0x02: '#00ff00', 
            0x03: '#ff7700', 0x04: 'none'}

        self.setStyleSheet('RGButton {background-color: %s; }' % (
            colors[self.color]))

        self.app.matrixChanged()
        

    color = 0x04

class SavedFrame(QListWidgetItem):
    def __init__(self, frame_data, text):
        QListWidgetItem.__init__(self)
        self.setText(text)
        self.frameData = frame_data

    frameData = None

class App(QApplication):
    def __init__(self, args=sys.argv):
        QApplication.__init__(self, args)
        self.main_widg = QWidget()
        self.main_widg.resize(400, 500)
        self.main_widg.setWindowTitle('LED Matrix control')
        self.main_widg.show()


        self.top_lay = QHBoxLayout()


        self.matrix_lay = QGridLayout()
        self.matrix_lay.setSpacing(0)


        self.split_lay = QHBoxLayout()


        self.main_lay = QVBoxLayout(self.main_widg)
        self.main_lay.addLayout(self.top_lay)
        self.main_lay.addLayout(self.split_lay)


        self.split_lay.addLayout(self.matrix_lay)


        self.ports_combo = QComboBox()
        #for (i, port) in self.scan():
        #    self.ports_combo.addItem(port)
        self.ports_combo.addItem('/dev/ttyUSB0')
        self.ports_combo.addItem('/dev/ttyUSB1')


        self.saved_frames = QListWidget()
        self.connect(self.saved_frames, SIGNAL('itemClicked(QListWidgetItem *)'), 
            self.load)
        self.split_lay.addWidget(self.saved_frames)

        self.open_port_btn = QPushButton('open')
        self.connect(self.open_port_btn, SIGNAL('clicked()'), self.open_port)


        self.close_port_btn = QPushButton('close')
        self.connect(self.close_port_btn, SIGNAL('clicked()'), self.close_port)


        self.rand_btn = QPushButton('randomize')
        self.connect(self.rand_btn, SIGNAL('clicked()'), self.randomize)


        self.clear_pixels_btn = QPushButton('clear pixels')
        self.connect(self.clear_pixels_btn, SIGNAL('clicked()'), 
            self.clear_pixels)

        self.save_btn = QPushButton('save')
        self.connect(self.save_btn, SIGNAL('clicked()'), self.save)


        self.top_lay.addWidget(self.ports_combo)
        self.top_lay.addWidget(self.open_port_btn)
        self.top_lay.addWidget(self.close_port_btn)
        self.top_lay.addWidget(self.clear_pixels_btn)
        self.top_lay.addWidget(self.rand_btn)
        self.top_lay.addWidget(self.save_btn)


        self.buttons = [RGButton(self) for i in range(64)]
        for i, btn in enumerate(self.buttons):
            x = i/8
            y = i%8
            self.matrix_lay.addWidget(btn, x, y)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


    def clear_pixels(self):
        self.send_ser = False
        for i, btn in enumerate(self.buttons):
            btn.change(0x04)
        self.send_ser = True
        self.matrixChanged()


    def save(self):
        sf = SavedFrame(self.frameData(), 
            str(self.saved_frames.count()))
        self.saved_frames.addItem(sf)
        self.saved_frames.setItemSelected(sf, True)

    def load(self, item):
        self.loadFrameData(item.frameData)

    def matrixChanged(self):
        if not self.send_ser:
            return
        try:
            bytes = bytearray([0xff, 0xff, 0xff] + \
                self.frameData() + [0xff, 0xff, 0xff])
            self.ser.write(bytes)
            b = self.ser.read()
            if (ord(b) != 0x20):
                print 'Frame not sent'
            else:
                print 'Frame sent' , ' '.join(['%X'%b for b in bytes])
        except Exception, e:
            print e

    def randomize(self):
        self.send_ser = False
        for i, btn in enumerate(self.buttons):
            btn.change(randint(0x01, 0x05))
        self.send_ser = True
        self.matrixChanged()


    def frameData(self):
        array = [0x00]*32
        for i in range(0, len(self.buttons), 2):
            array[i/2] = (self.buttons[i].color << 4) & 0xF0
            array[i/2] = array[i/2] ^ ((self.buttons[i+1].color) & 0x0F)

        return array

    def loadFrameData(self, frame_data):
        self.send_ser = False
        for i in range(0, len(self.buttons), 2):
            self.buttons[i].change(frame_data[i/2] >> 4 & 0x0F)
            self.buttons[i+1].change(frame_data[i/2] & 0x0F)
        self.send_ser = True
        self.matrixChanged()

    def open_port(self):
        self.ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=3)
        self.ser.open()

    def close_port(self):
        self.ser.close()

    def scan(self):
        available = []
        for i in range(256):
            try:
                s = serial.Serial(i)
                available.append( (i, s.portstr))
                s.close()
            except serial.SerialException:
                pass
        return available

    ser = None
    send_ser = True

app = App()



sys.exit(app.exec_())
