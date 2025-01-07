"""wxFigureCanvas"""
from typing import Optional, Tuple

import numpy as np
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
        data: Optional[Tuple[dict, ...]] = None,
        figure: Optional[Figure] = None,
        axes_shape: tuple = ()) -> None:
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
        data : Tuple[dict, ...], optional
            The data to plot.
        figure : Figure, optional
            The figure to plot.
        axes_shape : tuple, optional
            The shape of the axes.
        """
        super().__init__(parent, id, pos, size, style, name)

        if figure is None:
            self.figure = Figure(dpi=96)
            self.axes = None
            assert data is not None
            self._plot(data)
        else:
            self.figure = figure
            axes = self.figure.axes  # 不包含行列信息
            if len(axes) == 1:
                self.axes = axes[0]
            else:
                self.axes = np.asarray(axes, object)
                if not axes_shape:
                    num_rows = len(
                        set(ax.get_position().bounds[1] for ax in axes))
                    num_cols = len(
                        set(ax.get_position().bounds[0] for ax in axes))
                    axes_shape = (num_rows, num_cols)
                try:
                    self.axes = self.axes.reshape(axes_shape)
                except:
                    pass

        self.canvas = FigureCanvasWxAgg(self, wx.ID_ANY, self.figure)
        self.toolbar = NavigationToolbar(self.canvas)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.EXPAND | wx.ALL)
        self.sizer.Add(self.toolbar, 0, wx.EXPAND | wx.ALL)
        self.SetSizer(self.sizer)
        self._layout_order = True
        # update the axes menu on the toolbar
        self.toolbar.update()
        # self.Fit()
        self.canvas.mpl_connect('button_press_event', self._on_press)

    def redraw(self) -> None:
        self.canvas.draw()

    def Refresh(self, eraseBackground=True, rect=None):
        self.redraw()
        return super().Refresh(eraseBackground, rect)

    def SetFont(self, font) -> bool:  # 设置字体
        self.canvas.SetFont(font)
        self.toolbar.SetFont(font)
        return super().SetFont(font)

    def FlipLayout(self) -> None:  # 翻转布局
        self.sizer.Detach(self.canvas)  # 移除控件
        self.sizer.Detach(self.toolbar)
        if self._layout_order:
            self.sizer.Add(self.toolbar, 0, wx.EXPAND | wx.ALL)
            self.sizer.Add(self.canvas, 1, wx.EXPAND | wx.ALL)
        else:
            self.sizer.Add(self.canvas, 1, wx.EXPAND | wx.ALL)
            self.sizer.Add(self.toolbar, 0, wx.EXPAND | wx.ALL)
        self._layout_order = not self._layout_order
        self.Layout()

    def _plot(self, dat: Tuple[dict, ...]) -> None:
        if self.axes is None:
            if 'ax_shape' not in dat[0]:
                self.axes = self.figure.add_subplot()
            else:
                tup = tuple([0] * len(dat[0]['ax_shape']))
                for i in dat:
                    tup0 = tuple(i['ax_shape'])
                    if tup0 > tup:
                        tup = tup0
                self.axes = self.figure.add_subplot(*tup)

        for i in dat:
            item = i.copy()
            ax: Axes = self.axes[tuple(item.pop('ax_shape'))] if 'ax_shape' in item else self.axes[0]  # type: ignore

            if 'data' in item:
                data = [item.pop('data')]
            elif 'x' in item and 'y' in item:
                data = [item.pop('x'), item.pop('y')]
            else:
                raise ValueError('data not in item')
            if 'fmt' in item:
                data.append(item.pop('fmt'))

            ax.plot(*data, **item)
            ax.grid(ls='--', color='k', alpha=0.5)
            if 'label' in item:
                if mpl.__version_info__ < (2, 2):
                    ax.legend(loc='best')
                else:
                    ax.legend(loc='best', draggable=True)
        self.figure.tight_layout()

    def _on_press(self, event: MouseEvent) -> None:
        if event.inaxes is None:
            return

        if event.button == 2 and not event.dblclick:  # 中键单击
            self.toolbar.pan(event)
        if event.button == 1 and event.dblclick:  # 左键双击
            self.toolbar.home()
