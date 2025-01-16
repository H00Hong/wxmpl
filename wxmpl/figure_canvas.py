"""wxFigureCanvas"""
from typing import Optional, Tuple

import wx
from matplotlib.axes import Axes
from matplotlib.backend_bases import MouseEvent
from matplotlib.figure import Figure

from .wxagg import FigureCanvasWxAgg, NavigationToolbar, mpl


class FigureCanvas(wx.Panel):

    def __init__(
        self,
        parent,
        id=wx.ID_ANY,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=wx.TAB_TRAVERSAL,
        name='wxPythonFigureCanvas',
        *,
        figure: Optional[Figure] = None,
        axes: Optional[Axes] = None) -> None:
        """
        FigureCanvas for wxPython based on matplotlib.

        Parameters
        ----------
        parent : `wx.Window`
            The parent window.
        id : int
            The id of the window.
        pos : `wx.Point` or tuple
            The position of the window.
        size : `wx.Size` or tuple
            The size of the window.
        style : int
            The style of the window.
        name : str
            The name of the window.
        figure : `matplotlib.figure.Figure`, optional
            The figure to plot.
        axes : `matplotlib.axes.Axes`, optional
            The axes to plot, .

        Notes
        -----
        One of `figure` and `axes` must be given. If both are given, `figure`
        will be used.
        """
        super().__init__(parent, id, pos, size, style, name)
        if isinstance(figure, Figure):
            self.figure = figure
        elif isinstance(axes, Axes):
            self.figure = axes.get_figure()
        else:
            raise ValueError('`figure` or `axes` must be given')

        self.canvas = FigureCanvasWxAgg(self, wx.ID_ANY, self.figure)
        self.toolbar = NavigationToolbar(self.canvas)

        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self._sizer.Add(self.canvas, 1, wx.EXPAND | wx.ALL)
        self._sizer.Add(self.toolbar, 0, wx.EXPAND | wx.ALL)
        self.SetSizer(self._sizer)
        self._layout_order = True
        # update the axes menu on the toolbar
        self.toolbar.update()
        # self.Fit()
        self.canvas.mpl_connect('button_press_event', self._on_press)

    def redraw(self) -> None:
        self.canvas.draw()

    def redraw_idle(self) -> None:
        self.canvas.draw_idle()

    def set_cursor(self, cursor) -> None:
        self.canvas.SetCursor(cursor)

    def Refresh(self, eraseBackground=True, rect=None):
        self.redraw()
        return super().Refresh(eraseBackground, rect)

    def SetFont(self, font) -> bool:  # 设置字体
        self.canvas.SetFont(font)
        self.toolbar.SetFont(font)
        return super().SetFont(font)

    def FlipLayout(self) -> None:  # 翻转布局
        self._sizer.Detach(self.canvas)  # 移除控件
        self._sizer.Detach(self.toolbar)
        if self._layout_order:
            self._sizer.Add(self.toolbar, 0, wx.EXPAND | wx.ALL)
            self._sizer.Add(self.canvas, 1, wx.EXPAND | wx.ALL)
        else:
            self._sizer.Add(self.canvas, 1, wx.EXPAND | wx.ALL)
            self._sizer.Add(self.toolbar, 0, wx.EXPAND | wx.ALL)
        self._layout_order = not self._layout_order
        self.Layout()

    def _on_press(self, event: MouseEvent) -> None:
        if event.inaxes is None:
            return

        if event.button == 2 and not event.dblclick:  # 中键单击
            self.toolbar.pan(event)
        if event.button == 1 and event.dblclick:  # 左键双击
            self.toolbar.home()
