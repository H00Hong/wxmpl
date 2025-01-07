# -*- coding: utf-8 -*-

from .figure_canvas import Axes, Figure, FigureCanvas, Tuple, mpl, wx


def wxmpl_gui(
    fig: Figure,
    axes_shape: tuple = (),
    title: str = 'wxmpl',
    size: Tuple[int, int] = (800, 600),
    style: int = wx.DEFAULT_FRAME_STYLE,
) -> None:
    """
    Display a matplotlib figure in a wxPython window.

    Parameters
    ----------
    fig : `matplotlib.figure.Figure`
        The figure to display.
    axes_shape : tuple[int, ...], optional
        The shape of the axes to create in the figure. If not given,
        the figure's existing axes are used.
    title : str, optional
        The title of the window. Defaults to 'wxmpl'.
    size : tuple, optional
        The size of the window in pixels. Defaults to (800, 600).
    style : int, optional
        The style of the window. Defaults to `wx.DEFAULT_FRAME_STYLE`.
    """
    app = wx.App()
    win = wx.Frame(None, title=title, size=size, style=style)
    FigureCanvas(win, figure=fig, axes_shape=axes_shape)
    win.Center()
    # figcanvas.Fit()
    # win.Fit()
    win.Show()
    app.MainLoop()


__all__ = ['wxmpl_gui', 'FigureCanvas']
