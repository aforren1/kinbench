import argparse

import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from toon.input import MpDevice
import struct
from ctypes import c_uint16, c_uint8, Structure
import serial
from serial.tools import list_ports
from toon.input import BaseDevice
from time import sleep

class Data(Structure):
    _fields_ = [('digital', c_uint8), ('a1', c_uint16), ('a2', c_uint16)]

class TestSerial(BaseDevice):
    shape = (1,)
    ctype = Data
    sampling_frequency = 10000

    def __init__(self, nonblocking=False, **kwargs):
        super(TestSerial, self).__init__(**kwargs)
        self.nonblocking = nonblocking
        self._device = None
        ports = list_ports.comports()
        self._dev_name = next((p.device for p in ports if p.pid == 1155))

    def enter(self):
        self._device = serial.Serial(self._dev_name)
        self._device.close()
        sleep(0.5)
        self._device.open()
        return self

    def exit(self):
        self._device.close()

    def read(self):
        data = self._device.read(64)
        time = self.clock()
        if len(data) > 0:
            # TODO: make sure valid ints
            res2 = struct.unpack('<' + 'BHH'*10, data[:50]) # convert
            out = []
            j = 0
            for i in range(10):
                out.append([time, self.ctype(digital=res2[j], a1=res2[j+1], a2=res2[j+2])])
                j += 3
            return out
        return None

class LivePlot(pg.GraphicsLayoutWidget):
    def __init__(self, device):
        super(LivePlot, self).__init__()
        self.device = MpDevice(device, use_views=True)
        self.current_data = None
        self.lines = []
        dummy = np.ones(4)
        self.fig = self.addPlot(title='Foobar')
        self.fig.showGrid(x=True, y=True, alpha=0.4)
        self.fig.setClipToView(True)
        mi, ma = 0, 4000
        self.fig.setRange(yRange=[mi, ma])
        self.fig.setLimits(yMin=mi, yMax=ma)
        for j in range(3):
            pen = pg.mkPen(color=pg.intColor(j, hues=3, alpha=220), width=1)
            self.lines.append(self.fig.plot(dummy, dummy, pen=pen))
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(0)
        self.playing = True

    def update(self):
        pos = self.device.read()
        if pos is None:
            return
        if self.current_data is None:
            self.current_data = pos.data
            self.current_time = pos.time
        elif self.current_data.shape[0] < self.device.device.sampling_frequency:
            self.current_data = np.hstack((self.current_data, pos.data))
            self.current_time = np.hstack((self.current_time, pos.time))
        else:
            ps0 = -pos.data.shape[0]
            self.current_data = np.roll(self.current_data, ps0, axis=0)
            self.current_data[ps0:] = pos.data
            self.current_time = np.roll(self.current_time, ps0)
            self.current_time[ps0:] = pos.time
        if self.playing:
            self.lines[0].setData(y=self.current_data[:]['digital']*2000)
            self.lines[1].setData(y=self.current_data[:]['a1'])
            self.lines[2].setData(y=self.current_data[:]['a2'])
        print(pos.data[-1])


if __name__ == '__main__':
    device = TestSerial()
    app = QtGui.QApplication([])
    w = QtGui.QWidget()
    liveplot = LivePlot(device)

    pause_button = QtGui.QPushButton('Pause')

    def on_click():
        liveplot.playing = not liveplot.playing

    pause_button.clicked.connect(on_click)
    layout = QtGui.QGridLayout()
    w.setLayout(layout)
    layout.addWidget(liveplot, 0, 0, 3, 3)
    layout.addWidget(pause_button, 0, 1)
    w.setGeometry(10, 10, 1600, 600)
    w.show()
    with liveplot.device:
        app.exec_()

# if __name__ == '__main__':
#     dev = MpDevice(TestSerial())
#     # with dev:
#     #     while True:
#     #         res = dev.read()
#     #         if res:
#     #             print(res.data)