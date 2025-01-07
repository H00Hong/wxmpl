"""修改 backend_wx 渲染内核"""
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

ico_square = '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'


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

        image_data = base64.b64decode(ico_square)
        stream = io.BytesIO(image_data)
        # toolbarIconSize = wx.ArtProvider().GetDIPSizeHint(wx.ART_TOOLBAR)
        image = wx.Image(stream, wx.BITMAP_TYPE_ANY).Scale(32, 32)
        self.wx_ids['DataLabel'] = (
                self.InsertTool(
                    len(self.toolitems)-1,
                    -1,
                    label='DataLabel', 
                    bitmap=wx.Bitmap(image),
                    bmpDisabled=wx.NullBitmap,
                    shortHelp='Data label button',
                    kind=wx.ITEM_CHECK).Id)
        self.Bind(wx.EVT_TOOL, self.on_datalabel,
                  id=self.wx_ids['DataLabel'])
        self.Realize()

    # def _icon(self, name):
    #     try:
    #         return super()._icon(name)
    #     except FileNotFoundError:
    #         if name == 'datalabel.svg':
    #             image_data = base64.b64decode(ico_square)
    #             stream = io.BytesIO(image_data)
    #             toolbarIconSize = wx.ArtProvider().GetDIPSizeHint(
    #                 wx.ART_TOOLBAR)
    #             image = wx.Image(stream, wx.BITMAP_TYPE_ANY).Scale(
    #                 toolbarIconSize.x, toolbarIconSize.y)
    #             return wx.Bitmap(image)

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
                        elif self._old_annotation_info[-1] != id(ax):
                            print(self._old_annotation_info[-1])
                            self._annotation.set_visible(False)
                            self._init_annotation(ax)
                        self._annotation.set_visible(False)
                        self.update_annotation(int(ind['ind'][0]), l, ax)
                        break

    def _init_annotation(self, ax: plt.Axes):
        self._annotation = ax.annotate('',
                                       xy=(0, 0),
                                       xytext=(20, 20),
                                       textcoords='offset points',
                                       arrowprops=dict(arrowstyle='->'),
                                       bbox=dict(boxstyle='round', fc='w'))

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
