# -*- coding: utf-8 -*-

import os.path
import sys

import numpy as np
import matplotlib.pyplot as plt
import wx

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from wxmpl import FigureCanvas

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)

x = np.linspace(0, 2 * np.pi, 50)
y1 = np.sin(x)
y2 = np.cos(x)

ax.plot(x, y1, label='sin')
ax.plot(x, y2, lebel='cos')
ax.grid(ls='--', color='k', alpha=0.5)

app = wx.App()
frame = wx.Frame(None, title='wxmpl', size=(800, 600))
FigureCanvas(frame, figure=fig)
frame.Center()
frame.Show()
app.MainLoop()
