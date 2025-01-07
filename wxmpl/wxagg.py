"""修改 backend_wx 渲染内核"""
import os.path
import base64
import io
import matplotlib as mpl
import matplotlib.pyplot as plt
import wx
from matplotlib.backend_bases import MouseEvent, cursors
from matplotlib.backends.backend_wx import _api
from matplotlib.backends.backend_wxagg import (FigureCanvasWxAgg,
                                               NavigationToolbar2WxAgg)
from matplotlib.widgets import Button, SubplotTool

from ._figure_edit import ComboDialog, figure_edit

ico_143846 = "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"

class SubplotTool(SubplotTool):  # 增加按钮 tight_layout
    def __init__(self, targetfig, toolfig):
        super().__init__(targetfig, toolfig)
        self.buttontight = Button(toolfig.add_axes((0.575, 0.05, 0.2, 0.075)), 'Tight Layout')
        self.buttontight.on_clicked(self._on_tight_layout)
        # toolfig.suptitle('点击滑块调整子图参数')

    def _on_tight_layout(self, event):
        self.targetfig.tight_layout()
        self.targetfig.canvas.draw()
        # for item, name in zip(self._sliders, ['left', 'bottom', 'right', 'top', 'wspace', 'hspace']):
        #     item.val=getattr(self.targetfig.subplotpars, name)
        #     print(getattr(self.targetfig.subplotpars, name))


# matplotlib.backends.backend_wx._FigureCanvasWxBase.set_cursor 763 cursors.MOVE: wx.CURSOR_SIZING,
class FigureCanvasWxAgg(FigureCanvasWxAgg):  # 修改鼠标样式

    def set_cursor(self, cursor):
        # docstring inherited
        cursor = wx.Cursor(
            _api.check_getitem(
                {
                    cursors.MOVE: wx.CURSOR_SIZING,
                    cursors.HAND: wx.CURSOR_HAND,
                    cursors.POINTER: wx.CURSOR_ARROW,
                    cursors.SELECT_REGION: wx.CURSOR_CROSS,
                    cursors.WAIT: wx.CURSOR_WAIT,
                    cursors.RESIZE_HORIZONTAL: wx.CURSOR_SIZEWE,
                    cursors.RESIZE_VERTICAL: wx.CURSOR_SIZENS,
                },
                cursor=cursor))
        self.SetCursor(cursor)
        self.Refresh()


# matplotlib.backends.backend_wx.NavigationToolbar2Wx.__init__ 1100 label=' '*27
class NavigationToolbar(NavigationToolbar2WxAgg):

    toolitems = [*NavigationToolbar2WxAgg.toolitems]
    toolitems.insert(
        # Add 'customize' action after 'subplots'
        [name for name, *_ in toolitems].index('Subplots') + 1,
        ('Customize', 'Edit axis, curve and image parameters',
         'qt4_editor_options', 'edit_parameters'))
    # toolitems.insert(
    #     # Add 'customize' action after 'subplots'
    #     [name for name, *_ in toolitems].index('Customize') + 1,
    #     ('DataLabel', 'Data label button',
    #      'datalabel', 'on_datalabel'))

    def __init__(self, canvas, coordinates=True, *, style=wx.TB_BOTTOM):
        super(NavigationToolbar, self).__init__(canvas,
                                                coordinates,
                                                style=style)
        self._id_scroll = self.canvas.mpl_connect('scroll_event', self.do_scrollZoom)
        self._on_scroll = False
        self._s0 = 19
        self._annotation = None
        self._annotation_visible = False
        self._old_annotation_info = (None, None, None)
        if self._coordinates:
            self._label_text.SetLabel('(x=-0.000 y=-0.000)')

        image_data = base64.b64decode(ico_143846)
        stream = io.BytesIO(image_data)
        image = wx.Image(stream, wx.BITMAP_TYPE_ANY).Scale(32,32)
        self.wx_ids['DataLabel'] = (
                self.InsertTool(
                    len(self.toolitems)-2,
                    -1,
                    label='DataLabel',
                    bitmap=self._load_datalabel_svg(),
                    bmpDisabled=wx.NullBitmap,
                    shortHelp='Displays data labels near the mouse',
                    kind=wx.ITEM_CHECK).Id)
        self.Bind(wx.EVT_TOOL, self.on_datalabel,
                  id=self.wx_ids['DataLabel'])
        self.Realize()

    def _load_datalabel_svg(self):
        try:
            dark = wx.SystemSettings.GetAppearance().IsDark()
        except AttributeError:  # wxpython < 4.1
            # copied from wx's IsUsingDarkBackground / GetLuminance.
            bg = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)
            fg = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT)
            # See wx.Colour.GetLuminance.
            bg_lum = (.299 * bg.red + .587 * bg.green + .114 * bg.blue) / 255
            fg_lum = (.299 * fg.red + .587 * fg.green + .114 * fg.blue) / 255
            dark = fg_lum - bg_lum > .2

        with open(os.path.join(os.path.dirname(__file__), '143846.svg'), 'rb') as f:
            svg = f.read()
        if dark:
            svg = svg.replace(b'fill:black;', b'fill:white;')
        toolbarIconSize = wx.ArtProvider().GetDIPSizeHint(wx.ART_TOOLBAR)
        return wx.BitmapBundle.FromSVG(svg, toolbarIconSize)

    def configure_subplots(self, *args):  # 替换 SubplotTool 增加tight_layout按钮
        if hasattr(self, 'subplot_tool'):
            self.subplot_tool.figure.canvas.manager.show()
            return
        # This import needs to happen here due to circular imports.
        from matplotlib.figure import Figure
        with mpl.rc_context({'toolbar': 'none'}):  # No navbar for the toolfig.
            manager = type(self.canvas).new_manager(Figure(figsize=(6, 3)), -1)
        manager.set_window_title('Subplot configuration tool')
        tool_fig = manager.canvas.figure
        tool_fig.subplots_adjust(top=0.9)
        self.subplot_tool = SubplotTool(self.canvas.figure, tool_fig)
        cid = self.canvas.mpl_connect('close_event', lambda e: manager.destroy())
        def on_tool_fig_close(e):
            self.canvas.mpl_disconnect(cid)
            del self.subplot_tool
        tool_fig.canvas.mpl_connect('close_event', on_tool_fig_close)
        manager.show()
        return self.subplot_tool

    def set_message(self, s: str):  # 根据str的长度是否刷新
        if self._coordinates:
            s0 = len(s)
            self._label_text.SetLabel(s)
            if s0 > self._s0:
                self.Realize()
                self._s0 = s0

    def do_scrollZoom(self, event: MouseEvent):  # 鼠标滚轮缩放
        if self._on_scroll:
            # print('do_scrollZoom')
            ax = event.inaxes  # 产生事件axes对象
            if ax is None:
                return
            if self._nav_stack() is None:
                self.push_current()  # set the home button to this view

            xmin, xmax = ax.get_xbound()
            ymin, ymax = ax.get_ybound()
            ratio = event.step / 40
            xchg = ratio * (xmax - xmin)
            ychg = ratio * (ymax - ymin)
            ax.set_xbound(xmin + xchg, xmax - xchg)
            ax.set_ybound(ymin + ychg, ymax - ychg)
            self.canvas.draw()

    def pan(self, event: MouseEvent):
        super().pan(event)
        self._on_scroll = not self._on_scroll

    def mouse_move(self, event: MouseEvent):
        super().mouse_move(event)
        self.set_annotation(event)

    def on_datalabel(self, event: MouseEvent):
        self._annotation_visible = not self._annotation_visible
        if not self._annotation_visible:
            self._annotation.set_visible(False)
            self.canvas.draw_idle()

    def set_annotation(self, event: MouseEvent):
        for ax in self.canvas.figure.axes:
            if event.inaxes == ax:
                for l in ax.lines:
                    contains, ind = l.contains(event)
                    if contains:
                        if self._annotation is None:
                            self._init_annotation(ax)
                        elif self._old_annotation_info[-1] != id(ax) and self._annotation_visible:
                            self._annotation.set_visible(False)
                            self._init_annotation(ax)
                        self._annotation.set_visible(False)
                        self.update_annotation(int(ind['ind'][0]), l, ax)
                        break

    def _init_annotation(self, ax: plt.Axes):
        self._annotation = ax.annotate('',
                                       xy=(0, 0),
                                       xytext=(20, 10),
                                       textcoords='offset points',
                                       arrowprops=dict(arrowstyle='->'),
                                       bbox=dict(boxstyle='round', fc='w', alpha=0.5))

    def update_annotation(self, ind: int, l: plt.Line2D, ax: plt.Axes):
        if not self._annotation_visible:
            return
        if self._old_annotation_info == (ind, id(l), id(ax)):
            return
        x = l.get_xdata()[ind]
        y = l.get_ydata()[ind]
        line_label = l.get_label()
        ax_title = ax.get_title()
        text = f'Axes: {ax_title}\nLine: {line_label}\nPt.   (x: {x:.6f},\n        y: {y:.6f})\nPtInd {ind}'

        self._annotation.set_text(text)
        self._annotation.xy = (x, y)
        self._annotation.set_visible(True)
        self._old_annotation_info = (ind, id(l), id(ax))
        self.canvas.draw_idle()

    def edit_parameters(self, event):  # 增加视图选择窗口
        axes = self.canvas.figure.get_axes()
        if not axes:
            wx.MessageBox('There are no Axes to edit.', 'Error', wx.OK | wx.ICON_ERROR)
            return
        elif len(axes) == 1:
            ax = axes[0]
        else:
            titles = [
                ax.get_label() or
                ax.get_title() or
                ax.get_title('left') or
                ax.get_title('right') or
                ' - '.join(filter(None, [ax.get_xlabel(), ax.get_ylabel()])) or
                f'<anonymous {type(ax).__name__}>'
                for ax in axes]
            duplicate_titles = [
                title for title in titles if titles.count(title) > 1]
            for i, ax in enumerate(axes):
                if titles[i] in duplicate_titles:
                    titles[i] += f' (id: {id(ax):#x})'  # type: ignore # Deduplicate titles.
            choice = ComboDialog(self, 'Customize', 'Select Axes:', titles)
            if choice.ShowModal() != wx.ID_OK:
                return
            item = choice.choice_selection
            ax = axes[item]
        figure_edit(ax, self.canvas)
