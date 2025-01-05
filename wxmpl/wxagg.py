'''修改 backend_wx 渲染内核'''
import matplotlib as mpl
import wx
from matplotlib.backend_bases import MouseEvent, cursors
from matplotlib.backends.backend_wx import _api
from matplotlib.backends.backend_wxagg import (FigureCanvasWxAgg,
                                               NavigationToolbar2WxAgg)
from matplotlib.widgets import Button, SubplotTool

from ._figure_edit import ComboDialog, figure_edit


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

    def __init__(self, canvas, coordinates=True, *, style=wx.TB_BOTTOM):
        NavigationToolbar2WxAgg.__init__(self,
                                         canvas,
                                         coordinates,
                                         style=style)
        self._id_scroll = self.canvas.mpl_connect('scroll_event', self.do_scrollZoom)
        self._on_scroll = False
        self._s0 = 19
        if self._coordinates:
            self._label_text.SetLabel('(x=-0.000 y=-0.000)')
            self.Realize()

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


