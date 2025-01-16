# -*- coding: utf-8 -*-

from .figure_canvas import Axes, Figure, FigureCanvas, Optional, Tuple, mpl, wx


def wxmpl_gui(
    figure: Optional[Figure] = None,
    axes: Optional[Axes] = None,
    title: str = 'wxmpl',
    size: Tuple[int, int] = (800, 600),
    style: int = wx.DEFAULT_FRAME_STYLE,
) -> None:
    """
    Display a matplotlib figure in a wxPython window.

    Parameters
    ----------
    figure : `matplotlib.figure.Figure`, optional
        The figure to display. Defaults to `None`.
    axes : `matplotlib.axes.Axes`, optional
        The axes of the figure to display. Defaults to `None`.
    title : str, optional
        The title of the window. Defaults to 'wxmpl'.
    size : tuple, optional
        The size of the window in pixels. Defaults to (800, 600).
    style : int, optional
        The style of the window. Defaults to `wx.DEFAULT_FRAME_STYLE`.

    Notes
    -----
    One of `figure` and `axes` must be given. If both are given, `figure`
    will be used.
    """
    app = wx.App()
    win = wx.Frame(None, title=title, size=size, style=style)
    FigureCanvas(win, figure=figure, axes=axes)
    win.Center()
    # figcanvas.Fit()
    # win.Fit()
    win.Show()
    app.MainLoop()


__all__ = ['wxmpl_gui', 'FigureCanvas']
__version_info__ = (0, 1, 0)
__version__ = '.'.join(map(str, __version_info__))
__updated__ = '2025-1-16'
