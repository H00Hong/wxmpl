"""修改 backend_wx 渲染内核"""
import os.path

import matplotlib as mpl
import matplotlib.pyplot as plt
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


class FigureCanvasWxAgg(FigureCanvasWxAgg):  # 修改鼠标样式

    def set_cursor(self, cursor):
        # docstring inherited
        cursor = wx.Cursor(
            _api.check_getitem(
                {
                    cursors.MOVE: wx.CURSOR_SIZING,  # 修改
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
        self._slen0 = 19
        self._annotation = None
        self._annotation_visible = False
        self._old_annotation_info = (None, None, None)
        if self._coordinates:
            self._label_text.SetLabel('(x=-0.000 y=-0.000)')

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

        with open(os.path.join(os.path.dirname(__file__), 'datalabel.svg'), 'rb') as f:
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
            slen0 = len(s)
            self._label_text.SetLabel(s)
            if slen0 > self._slen0:
                self.Realize()
                self._slen0 = slen0

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
            self.canvas.draw_idle()

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
                                       bbox=dict(boxstyle='round', fc='w', alpha=0.5),
                                       annotation_clip=False)

    def update_annotation(self, ind: int, l: plt.Line2D, ax: plt.Axes):
        if not self._annotation_visible:
            return
        if self._old_annotation_info == (ind, id(l), id(ax)):
            return
        x = l.get_xdata()[ind]
        y = l.get_ydata()[ind]
        text = f'Axes: {ax.get_title()}\nLine: {l.get_label()}\n\
Pt.   (x: {x.round(6)},\n        y: {y.round(6)})\nPtInd. {ind}'

        self._annotation.set_position((20, 10))
        self._annotation.set_text(text)
        self._annotation.xy = (x, y)
        self._annotation.set_visible(True)
        contains = self._check_contains_bbox(ax)
        if not contains:
            bbox = self._annotation.get_window_extent(renderer=self.canvas.get_renderer())
            len_ = - int(70 / bbox.height * bbox.width)
            for xy in ((len_, 10), (len_, -70), (20, -70)):
                self._annotation.set_position(xy)
                contains = self._check_contains_bbox(ax)
                if contains:
                    break
            if not contains:
                self._annotation.set_position((20, 10))
                print('Annotation is outside the axes bounds.')
        self._old_annotation_info = (ind, id(l), id(ax))
        self.canvas.draw()

    def _check_contains_bbox(self, ax: plt.Axes) -> bool:
        # 获取注释的边界框
        bbox = self._annotation.get_window_extent(renderer=self.canvas.get_renderer())
        # 检查边界框是否在轴范围内
        contains_point0 = ax.contains_point((bbox.x0, bbox.y0))
        contains_point1 = ax.contains_point((bbox.x1, bbox.y1))
        return contains_point0 and contains_point1

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
