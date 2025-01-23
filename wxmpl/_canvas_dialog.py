# -*- coding: utf-8 -*-
"""窗口类"""
from numbers import Integral, Real
from typing import List, Literal, Tuple

import wx
from matplotlib import cbook
from matplotlib.colors import Colormap

FONT = (12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,
        False, 'Microsoft Yahei')


class ComboDialog(wx.Dialog):  # 选择视图

    def __init__(self, parent, title, lab, lst):
        super(ComboDialog, self).__init__(parent, title=title, size=(300, 200))

        font = wx.Font(*FONT)
        label = wx.StaticText(self, label=lab)
        self.choice = wx.Choice(self, choices=lst)
        self.choice.SetSelection(0)
        # 创建确定和取消按钮
        ok_button = wx.Button(self, label='确定')
        cancel_button = wx.Button(self, label='取消')
        # 绑定按钮事件
        ok_button.Bind(wx.EVT_BUTTON, self.on_ok)
        cancel_button.Bind(wx.EVT_BUTTON, self.on_cancel)

        self.choice_selection = -1
        self.SetFont(font)
        label.SetFont(font)
        self.choice.SetFont(font)
        ok_button.SetFont(font)
        cancel_button.SetFont(font)

        layout = wx.BoxSizer(wx.VERTICAL)
        layout.Add(label, 0, wx.ALL, 10)
        layout.Add(self.choice, 0, wx.ALL | wx.EXPAND, 10)
        layout1 = wx.BoxSizer(wx.HORIZONTAL)
        layout1.Add(wx.StaticText(self, label=''), 1, wx.ALL | wx.EXPAND)
        layout1.Add(ok_button, 0, wx.ALL, 4)
        layout1.Add(cancel_button, 0, wx.ALL, 4)
        layout.Add(layout1, 0, wx.ALL | wx.EXPAND, 6)
        self.SetSizer(layout)

    def on_ok(self, event):
        self.choice_selection = self.choice.GetSelection()
        self.EndModal(wx.ID_OK)

    def on_cancel(self, event):
        self.choice_selection = -1
        self.EndModal(wx.ID_CANCEL)


# ==============================================================================
def _to_wxcolor(color: str):
    return wx.Colour(int(color[1:3], 16),
                     int(color[3:5], 16),
                     int(color[5:7], 16),
                     alpha=int(color[7:9], 16))


def _to_scolor(color: wx.Colour):

    def to_hex(c_):
        return hex(c_)[-2:].replace('x', '0')

    s = '#' + to_hex(color.Red()) + to_hex(color.Green()) + to_hex(
        color.Blue())
    return s


class LineLabel(wx.Panel):

    def __init__(self, parent, tupdat, size=(400, 30), name='', setsizer=True):
        super().__init__(parent, size=size, name=name)
        if tupdat[0] is None:
            if tupdat[1] is None:  # 空行
                widget0 = wx.StaticText(self,
                                        label='',
                                        size=(400, 30),
                                        name='none')
            else:  # 标签行
                widget0 = wx.StaticText(self,
                                        label=tupdat[1],
                                        size=(400, 30),
                                        name='label_none')
        else:
            widget0 = wx.StaticText(self,
                                    label=tupdat[0],
                                    size=(200, 30),
                                    name='label')

        self._lab = widget0.GetLabel()  # 保存原始值 防止后续修改时被覆盖
        self._widgets = [widget0]
        self.set_font()
        if setsizer:
            self.set_sizer()

    def set_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        for i in range(len(self._widgets)):
            sizer.Add(self._widgets[i], int(i == 1), wx.ALIGN_CENTER | wx.ALL)
        self.SetSizer(sizer)

    def set_font(self):
        font = wx.Font(*FONT)
        self.SetFont(font)
        for i in self._widgets:
            i.SetFont(font)

            lab: str = i.GetLabel()
            if lab.startswith('<b>') and lab.endswith('</b>'):
                i.SetFont(font.Bold())
                i.SetLabel(lab[3:-4])

    def get_val(self):
        pass

    def set_val(self, val):
        pass

    def get_lab(self) -> str:
        return self._lab


class LineColor(LineLabel):

    def __init__(self, parent, tupdat, size=(400, 30), name=''):
        super().__init__(parent, tupdat, size=size, name=name, setsizer=False)

        widget1 = wx.TextCtrl(self,
                              value=tupdat[1],
                              size=(172, 30),
                              name='color')
        widget2 = wx.Button(self, label='', size=(28, 28), name='color_btn')
        widget2.SetBackgroundColour(_to_wxcolor(tupdat[1]))
        widget2.Bind(wx.EVT_BUTTON, self._on_color_btn)
        widget1.Bind(wx.EVT_TEXT, self._on_color_text)

        self._widgets.extend((widget1, widget2))
        self.set_font()
        self.set_sizer()

    def set_val(self, val: str):
        assert isinstance(val, str) and val[0] == '#'
        self._widgets[1].SetValue(val)
        self._widgets[2].SetBackgroundColour(_to_wxcolor(val))

    def get_val(self) -> str:
        return self._widgets[1].GetValue()

    def _on_color_btn(self, event: wx.MouseEvent):
        c_str_old: str = self._widgets[1].GetValue()
        c_wx_old = _to_wxcolor(c_str_old)
        cdata_old = wx.ColourData()
        cdata_old.SetColour(c_wx_old)
        cdata_old.SetChooseFull(True)
        colorwin = wx.ColourDialog(self, cdata_old)
        if colorwin.ShowModal() != wx.ID_OK:
            return

        c_wx_new: wx.Colour = colorwin.GetColourData().GetColour()
        c_str_new = _to_scolor(c_wx_new) + c_str_old[-2:]
        self._widgets[1].SetValue(c_str_new)
        self._widgets[2].SetBackgroundColour(c_wx_new)

    def _on_color_text(self, event: wx.CommandEvent):
        c_str_new = self._widgets[1].GetValue()
        self._widgets[2].SetBackgroundColour(_to_wxcolor(c_str_new))


class LineChoice(LineLabel):

    def __init__(self, parent, tupdat, size=(400, 30), name=''):
        super().__init__(parent, tupdat, size=size, name=name, setsizer=False)

        dat = tupdat[1]
        if isinstance(dat[1], str):
            self._type = 0
            name = 'axes_choice'
        elif isinstance(dat[1], tuple):
            if isinstance(dat[1][0], Colormap):
                self._type = 2
                name = 'cmap_choice'
            else:
                self._type = 1
                name = 'canvas_choice'
        else:
            raise TypeError('type error')
        select: str = dat[0]
        lst = dat[1:]
        if self._type == 0:
            choice_show = lst
            self.choice_value = lst
            self._map_val2index = dict(
                zip(self.choice_value, range(len(self.choice_value))))
        else:
            lst_ = list(zip(*lst))
            choice_show = lst_[1]
            self.choice_value = lst_[0]
            index = range(len(self.choice_value))
            if self._type == 1:
                self._map_val2index = dict(zip(self.choice_value, index))
            else:
                self.choice_value = choice_show
                self._map_val2index = dict(zip(choice_show, index))

        widget1 = wx.Choice(self,
                            choices=choice_show,
                            size=(200, 30),
                            name=name)
        widget1.SetSelection(self._map_val2index[select])

        self._widgets.append(widget1)
        self.set_font()
        self.set_sizer()

    def set_val(self, val: str):  # data->
        self._widgets[1].SetSelection(self._map_val2index[val])

    def get_val(self):
        # cmap: return str
        return self.choice_value[self._widgets[1].GetSelection()]


class LineEdit(LineLabel):

    def __init__(self, parent, tupdat, size=(400, 30), name=''):
        super().__init__(parent, tupdat, size=size, name=name, setsizer=False)

        if isinstance(tupdat[1], str):
            self._type = 0
            name = 'str_edit'
        elif isinstance(tupdat[1],
                        Real) and (not isinstance(tupdat[1], Integral)):
            self._type = 1
            name = 'float_edit'
        else:
            raise TypeError('type error')
        widget1 = wx.TextCtrl(self,
                              value=str(tupdat[1]),
                              size=(200, 30),
                              name=name)

        self._widgets.append(widget1)
        self.set_font()
        self.set_sizer()

    def get_val(self):
        val = self._widgets[1].GetValue()
        if self._type == 0:
            return val
        elif self._type == 1:
            return float(val)

    def set_val(self, val):
        self._widgets[1].SetValue(str(val))


class LineCheck(LineLabel):

    def __init__(self, parent, tupdat, size=(400, 30), name=''):
        super().__init__(parent, tupdat, size=size, name=name, setsizer=False)

        assert isinstance(tupdat[1], bool)
        widget1 = wx.CheckBox(self, label='', size=(200, 30), name='bool')

        self._widgets.append(widget1)
        self.set_font()
        self.set_sizer()

    def get_val(self) -> bool:
        return self._widgets[1].GetValue()

    def set_val(self, val: bool):
        self._widgets[1].SetValue(bool(val))


class LineSpin(LineLabel):

    def __init__(self, parent, tupdat, size=(400, 30), name=''):
        super().__init__(parent, tupdat, size=size, name=name, setsizer=False)

        assert isinstance(tupdat[1], Integral)
        widget1 = wx.SpinCtrl(self,
                              value=str(tupdat[1]),
                              min=-10**9,
                              max=10**9,
                              size=(200, 30),
                              name='int')

        self._widgets.append(widget1)
        self.set_font()
        self.set_sizer()

    def get_val(self) -> int:
        return self._widgets[1].GetValue()

    def set_val(self, val: int):
        self._widgets[1].SetValue(int(val))


class FormDialog(wx.Dialog):  # 表单对话框
    """表单对话框"""

    def __init__(self,
                 data: List[Tuple[list, str, str]],
                 title,
                 parent=None,
                 apply=None):
        super(FormDialog, self).__init__(parent,
                                         title=title,
                                         size=(440, 700),
                                         style=wx.CAPTION | wx.CLOSE_BOX
                                         | wx.RESIZE_BORDER)
        path = cbook._get_data_path('images', 'matplotlib.svg')
        svg = path.read_bytes()
        iconsize = wx.ArtProvider().GetDIPSizeHint(wx.ART_TOOLBAR)
        bmp = wx.BitmapBundle.FromSVG(svg, iconsize)
        self.SetIcon(bmp.GetIcon(iconsize))
        self.SetMinSize((440, 640))
        self._data: List[Tuple[list, str, str]] = data
        self.apply_callback = apply

        self._font = wx.Font(*FONT)
        self.layout0 = wx.BoxSizer(wx.VERTICAL)

        self._set_notebook()
        self._widgets = [self._set_notetab0()]
        for i in range(1, len(self._notetab)):
            self._widgets.append(self._set_notetab1(i))

        self.okbutton = wx.Button(self, label='确定')
        self.cancelbutton = wx.Button(self, label='取消')
        self.applybutton = wx.Button(self, label='应用')

        self.layout0.Add(self._notebook, 1, wx.EXPAND | wx.ALL, 3)
        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(wx.StaticText(self, label=''), 1, wx.EXPAND)
        sizer1.Add(self.okbutton, 0, wx.ALL, 3)
        sizer1.Add(self.cancelbutton, 0, wx.ALL, 3)
        sizer1.Add(self.applybutton, 0, wx.ALL, 3)
        self.layout0.Add(sizer1, 0, wx.EXPAND | wx.ALL, 3)
        self.SetSizer(self.layout0)

        self.okbutton.Bind(wx.EVT_BUTTON, self.on_ok)
        self.cancelbutton.Bind(wx.EVT_BUTTON, self.on_cancel)
        self.applybutton.Bind(wx.EVT_BUTTON, self.on_apply)

    def _set_notebook(self):
        assert isinstance(self._data, list) and isinstance(
            self._data[0], tuple)
        note_num = len(self._data)
        # 创建Notebook控件
        self._notebook = wx.Notebook(self)
        self._notebook.SetFont(self._font)
        # 创建Tab页列表
        self._notetab: List[wx.Panel] = []
        for i in range(note_num):
            name = self._data[i][1]
            panel = wx.Panel(self._notebook, name=name)  # 创建Tab面板
            panel.SetFont(self._font)
            self._notetab.append(panel)
            self._notebook.AddPage(panel, name)

    def _set_notetab0(self):  # set axes
        panel = self._notetab[0]
        data0 = self._data[0][0]  # list[tuple[item]]
        widgets = []
        sizer = wx.BoxSizer(orient=wx.VERTICAL)

        for i in range(len(data0)):
            panel_ = self._set_linewidget(data0[i], panel, 'axes')
            sizer.Add(panel_, 1, wx.EXPAND | wx.ALL, 3)
            widgets.append(panel_)
        panel.SetSizer(sizer)
        return widgets

    def _set_notetab1(self, num: Literal[1, 2]):  # set curves | mappables
        data = self._data[num][0]  # list[list[tuple[item]]]
        name = str(num)
        panel = self._notetab[num]
        panel_line = wx.Panel(panel, name=name + '_0')
        choices = [i[1] for i in data]
        choice = wx.Choice(panel, choices=choices, size=(400, 30), name=name)
        choice.SetSelection(0)
        choice.SetFont(self._font)
        choice.Bind(wx.EVT_CHOICE, self._on_notetab_choice)
        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        sizer.Add(choice, 0, wx.ALL | wx.EXPAND, 3)

        sizer1 = wx.BoxSizer(orient=wx.VERTICAL)
        data0 = data[0][0]
        for i in range(len(data0)):
            line_panel = self._set_linewidget(data0[i],
                                              panel_line,
                                              name=name + '_' + str(i))
            sizer1.Add(line_panel, 1, wx.EXPAND | wx.ALL, 3)
        panel_line.SetSizer(sizer1)
        sizer.Add(panel_line, 1, wx.EXPAND)
        panel.SetSizer(sizer)
        return [choice, panel_line]

    def _on_notetab_choice(self, event: wx.MouseEvent):
        widget: wx.Choice = event.GetEventObject()
        num = widget.GetSelection()
        name = widget.GetName()
        data_t = self._data[int(name)][0]
        widgets_t = self._widgets[int(name)][1]
        # if name == '1':
        #     data_t = self._data[1][0]
        #     widgets_t = self._widgets[1][1]
        # elif name == '2':
        #     data_t = self._data[2][0]
        #     widgets_t = self._widgets[2][1]
        # else:
        #     raise ValueError('name error')
        widgets_t.SetName(name + '_' + str(num))
        data_0 = data_t[num][0]
        widgets_0 = widgets_t.GetChildren()
        for i, it in enumerate(widgets_0):
            val = data_0[i][1]
            if isinstance(val, (list, tuple)):
                val = val[0]
            it.set_val(val)

    def _set_linewidget(self, linedata: tuple, parent, name: str):
        dat1, dat2 = linedata
        if dat1 is None:
            return LineLabel(parent, linedata, name=name + '_none')
        if 'RGB' in dat1:
            return LineColor(parent, linedata, name=name + '_color')
        elif isinstance(dat2, bool):
            return LineCheck(parent, linedata, name=name + '_bool')
        elif isinstance(dat2, Integral):
            return LineSpin(parent, linedata, name=name + '_int')
        elif isinstance(dat2, (Real, str)):
            return LineEdit(parent, linedata, name=name + '_edit')
        elif isinstance(dat2, (list, tuple)):
            return LineChoice(parent, linedata, name=name + '_choice')
        else:
            raise ValueError(f'not support {dat1} {dat2}')

    def _get_value(self):
        data0, data1, data2 = [], [], []
        for it in self._notetab[0].GetChildren():
            val = it.get_val()
            if val is None:
                continue
            data0.append(val)

        if len(self._notetab) > 1:
            self._update_data(self._widgets[1][1])
            data1 = self._get_fromdata(1)
        if len(self._notetab) > 2:
            self._update_data(self._widgets[2][1])
            data2 = self._get_fromdata(2)
        dat = [data0]
        if data1:
            dat.append(data1)
        if data2:
            dat.append(data2)
        return dat

    def _update_data(self, panel: wx.Panel):
        # panel:wx.Panel = widget[1]
        line_widgets = panel.GetChildren()  # List[LineLabel]
        name, num = panel.GetName().split('_')
        num1 = int(num)
        num0 = int(name)

        for i in range(len(line_widgets)):
            line_widget = line_widgets[i]
            lab = line_widget.get_lab()
            val = line_widget.get_val()
            line_data_old = self._data[num0][0][num1][0][i]
            if val is None:
                line_data_new = (None, None if lab == '' else lab)
            else:
                if isinstance(line_data_old[1], (list, tuple)):
                    val = [val] + list(line_data_old[1][1:])
                line_data_new = (lab, val)
            if line_data_new != line_data_old:
                self._data[num0][0][num1][0][i] = line_data_new

    def _get_fromdata(self, num: Literal[1, 2]):
        dat = self._data[num][0]
        res = []
        for it in dat:
            res_ = []
            itt = it[0]
            for ii in itt:
                if ii[0] is None:
                    continue
                val = ii[1]
                if isinstance(val, (list, tuple)):
                    res_.append(val[0])
                else:
                    res_.append(val)
            res.append(res_)
        return res

    def on_ok(self, event):
        self.on_apply(event)
        self.EndModal(wx.ID_OK)

    def on_cancel(self, event):
        self.EndModal(wx.ID_CANCEL)

    def on_apply(self, event):
        if self.apply_callback is not None:
            self.apply_callback(self._get_value())
        else:
            raise NotImplementedError


def fedit(data, title="", parent=None, apply=None):
    """
    Create form dialog

    data: datalist, datagroup
    title: str
    parent: parent QWidget
    apply: apply callback (function)

    datalist: list/tuple of (field_name, field_value)
    datagroup: list/tuple of (datalist *or* datagroup, title, comment)

    -> one field for each member of a datalist
    -> one tab for each member of a top-level datagroup
    -> one page (of a multipage widget, each page can be selected with a combo
       box) for each member of a datagroup inside a datagroup

    Supported types for field_value:
      - int, float, str, bool
      - colors: in Qt-compatible text form, i.e. in hex format or name
                (red, ...) (automatically detected from a string)
      - list/tuple:
          * the first element will be the selected index (or value)
          * the other elements can be couples (key, value) or only values
    """

    dialog = FormDialog(data, title, parent, apply)

    if parent is not None:
        if hasattr(parent, "_fedit_dialog"):
            parent._fedit_dialog.close()
        parent._fedit_dialog = dialog

    dialog.ShowModal()


if __name__ == "__main__":

    def set_axes():
        return [('标题', ''), (None, None), (None, '<b>X-轴</b>'), ('最小值', -3.0),
                ('最大值', 3.0), ('图例名', ''),
                ('轴尺度', ['linear', 'linear', 'log', 'symlog', 'logit']),
                (None, None), (None, '<b>Y-轴</b>'), ('最小值', -3.0),
                ('最大值', 3.0), ('图例名', ''),
                ('轴尺度', ['linear', 'linear', 'log', 'symlog', 'logit']),
                (None, None), ('(Re-)生成自动图例', False)]

    def set_line(lst=[
        '_child1', '--', 'default', 1.5, '#000000ff', '', 6.0, '#000000ff',
        '#000000ff'
    ]):
        return [('名称', lst[0]), (None, None), (None, '<b>曲线</b>'),
                ('线型', [
                    lst[1], ('-.', 'DashDot'), ('--', 'Dashed'),
                    (':', 'Dotted'), ('None', 'None'), ('-', 'Solid')
                ]),
                ('绘图样式', [
                    lst[2],
                    ('default', 'Default'), ('steps-mid', 'Steps (Mid)'),
                    ('steps-post', 'Steps (Post)'), ('steps', 'Steps (Pre)')
                ]), ('线宽', lst[3]), ('线颜色 (RGBA)', lst[4]), (None, None),
                (None, '<b>标签</b>'),
                ('类型', [
                    lst[5], (7, 'caretdown'), (11, 'caretdownbase'),
                    (4, 'caretleft'), (8, 'caretleftbase'), (5, 'caretright'),
                    (9, 'caretrightbase'), (6, 'caretup'), (10, 'caretupbase'),
                    ('o', 'circle'), ('D', 'diamond'), ('h', 'hexagon1'),
                    ('H', 'hexagon2'), ('_', 'hline'), ('', 'nothing'),
                    ('8', 'octagon'), ('p', 'pentagon'), (',', 'pixel'),
                    ('+', 'plus'), ('P', 'plus_filled'), ('.', 'point'),
                    ('s', 'square'), ('*', 'star'), ('d', 'thin_diamond'),
                    (3, 'tickdown'), (0, 'tickleft'), (1, 'tickright'),
                    (2, 'tickup'), ('1', 'tri_down'), ('3', 'tri_left'),
                    ('4', 'tri_right'), ('2', 'tri_up'),
                    ('v', 'triangle_down'), ('<', 'triangle_left'),
                    ('>', 'triangle_right'), ('^', 'triangle_up'),
                    ('|', 'vline'), ('x', 'x'), ('X', 'x_filled')
                ]), ('大小', lst[6]), ('填充颜色 (RGBA)', lst[7]),
                ('轮廓颜色 (RGBA)', lst[8])]

    datalist = [
        (set_axes(), '坐标轴', ''),
        ([[
            set_line([
                '_child1', '--', 'default', 1.5, '#900000ff', '', 6.0,
                '#000090ff', '#009000ff'
            ]), '_child1', ''
        ],
          [
              set_line([
                  '_child2', '-', 'default', 1.5, '#000090ff', '', 5.0,
                  '#009000ff', '#900000ff'
              ]), '_child2', ''
          ]], '曲线', ''),
    ]

    app = wx.App()
    win = FormDialog(datalist, title="测试")
    win.Show()
    app.MainLoop()
