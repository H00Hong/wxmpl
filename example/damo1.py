# -*- coding: utf-8 -*-

import os.path
import sys

import numpy as np
import matplotlib.pyplot as plt
import wx

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from wxmpl import wxmpl_gui, FigureCanvas


class MainWin(wx.Frame):
    def __init__(self, fig):
        super(MainWin, self).__init__(None, title='test', size=(800, 600))

        self.canvas = FigureCanvas(self, figure=fig)
        # self.canvas.canvas.mpl_connect('motion_notify_event', self.on_motion)

        btn = wx.Button(self, label='data')
        self.Bind(wx.EVT_BUTTON, self.on_btn_click, btn)
        self._annotation = None
        self._annotation_visible = False
        self._old_annotation_info = (None, None)
        # self._annotation.set_visible(self._annotation_visible)
        layout = wx.BoxSizer(wx.VERTICAL)
        layout.Add(self.canvas, 1, wx.EXPAND)
        layout.Add(btn, 0, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(layout)

    def on_motion(self, event):
        # print(type(event))
        axs = fig.axes
        for ax in axs:
            if event.inaxes == ax:
                # lines = ax.lines
                for l in ax.lines:
                    contains, ind = l.contains(event)
                    if contains:
                        if self._annotation is None:
                            self._annotation = ax.annotate(
                                '',
                                xy=(0, 0),
                                xytext=(20, 20),
                                textcoords='offset points',
                                arrowprops=dict(arrowstyle='->'),
                                bbox=dict(boxstyle='round', fc='w')
                            )
                        self._annotation.set_visible(False)
                        self.update_annotation(int(ind['ind'][0]), l)
                        break

    def update_annotation(self, ind: int, l: plt.Line2D):
        if not self._annotation_visible:
            return
        if self._old_annotation_info == (ind, l):
            return
        x = l.get_xdata()[ind]
        y = l.get_ydata()[ind]
        line_label = l.get_label()
        self._annotation.set_text(f'Line: {line_label}\nPt.   (x: {x},\n        y: {y})\nPtInd {ind}')
        self._annotation.xy = (x, y)
        self._annotation.set_visible(self._annotation_visible)
        self.canvas.redraw()
        self._old_annotation_info = (ind, l)

    def on_btn_click(self, event):
        self._annotation_visible = not self._annotation_visible


if __name__ == '__main__':
    x = np.linspace(0, 2*np.pi, 50)
    y1 = np.sin(x)
    y2 = np.cos(x)

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(x, y1)
    ax.plot(x, y2)
    ax.grid(ls='--', color='k', alpha=0.5)

    app = wx.App()
    win = MainWin(fig)
    win.Center()
    win.Show()
    app.MainLoop()
