"""Figure Edit函数"""
from itertools import chain

import matplotlib as mpl
from matplotlib import cm
from matplotlib import colors as mcolors
from matplotlib import image as mimage
from matplotlib import markers
from matplotlib.dates import DateConverter, num2date
# from matplotlib.backends.qt_editor.figureoptions import LINESTYLES, DRAWSTYLES, MARKERS

from ._canvas_dialog import ComboDialog, FormDialog

LINESTYLES = {
    '-': 'Solid',
    '--': 'Dashed',
    '-.': 'DashDot',
    ':': 'Dotted',
    'None': 'None',
}

DRAWSTYLES = {
    'default': 'Default',
    'steps-pre': 'Steps (Pre)',
    'steps': 'Steps (Pre)',
    'steps-mid': 'Steps (Mid)',
    'steps-post': 'Steps (Post)'
}

MARKERS = markers.MarkerStyle.markers


def figure_edit(axes, parent=None):
    """编辑 matplotlib 图形选项"""
    sep = (None, None)  # separator

    # Get / General
    def convert_limits(lim, converter):
        """转换轴限制以获得正确的输入编辑器"""
        if isinstance(converter, DateConverter):
            return map(num2date, lim)
        # Cast to builtin floats as they have nicer reprs.
        return map(float, lim)

    axis_map = axes._axis_map
    axis_limits = {
        name:
        tuple(convert_limits(
            getattr(axes, f'get_{name}lim')(), axis.converter))
        for name, axis in axis_map.items()
    }
    general = [
        ('Title', axes.get_title()),
        sep,
        *chain.from_iterable([(
            (None, f"<b>{name.title()}-Axis</b>"),
            ('Min', axis_limits[name][0]),
            ('Max', axis_limits[name][1]),
            ('Label', axis.get_label().get_text()),
            ('Scale', [axis.get_scale(), 'linear', 'log', 'symlog', 'logit']),
            sep,
        ) for name, axis in axis_map.items()]),
        ('(Re-)Generate automatic legend', False),
    ]

    # Save the converter and unit data
    axis_converter = {name: axis.converter for name, axis in axis_map.items()}
    axis_units = {name: axis.get_units() for name, axis in axis_map.items()}

    # Get / Curves
    labeled_lines = []
    for line in axes.get_lines():
        label = line.get_label()
        if label == '_nolegend_':
            continue
        labeled_lines.append((label, line))
    curves = []

    def prepare_data(d, init):
        """
        准备 FormLayout 的条目 Prepare entry for FormLayout.

        *d* is a mapping of shorthands to style names (a single style may
        have multiple shorthands, in particular the shorthands `None`,
        `"None"`, `"none"` and `""` are synonyms); *init* is one shorthand
        of the initial style.

        This function returns an list suitable for initializing a
        FormLayout combobox, namely `[initial_name, (shorthand,
        style_name), (shorthand, style_name), ...]`.
        """
        if init not in d:
            d = {**d, init: str(init)}
        # Drop duplicate shorthands from dict (by overwriting them during
        # the dict comprehension).
        name2short = {name: short for short, name in d.items()}
        # Convert back to {shorthand: name}.
        short2name = {short: name for name, short in name2short.items()}
        # Find the kept shorthand for the style specified by init.
        canonical_init = name2short[d[init]]
        # Sort by representation and prepend the initial value.
        return ([canonical_init] + sorted(
            short2name.items(), key=lambda short_and_name: short_and_name[1]))

    for label, line in labeled_lines:
        color = mcolors.to_hex(mcolors.to_rgba(line.get_color(),
                                               line.get_alpha()),
                               keep_alpha=True)
        ec = mcolors.to_hex(mcolors.to_rgba(line.get_markeredgecolor(),
                                            line.get_alpha()),
                            keep_alpha=True)
        fc = mcolors.to_hex(mcolors.to_rgba(line.get_markerfacecolor(),
                                            line.get_alpha()),
                            keep_alpha=True)
        curvedata = [
            ('Label', label), sep, (None, '<b>Line</b>'),
            ('Line style', prepare_data(LINESTYLES, line.get_linestyle())),
            ('Draw style', prepare_data(DRAWSTYLES, line.get_drawstyle())),
            ('Width', line.get_linewidth()), ('Color (RGBA)', color), sep,
            (None, '<b>Marker</b>'),
            ('Style', prepare_data(MARKERS, line.get_marker())),
            ('Size', line.get_markersize()), ('Face color (RGBA)', fc),
            ('Edge color (RGBA)', ec)
        ]
        curves.append([curvedata, label, ""])
    # Is there a curve displayed?
    has_curve = bool(curves)

    # Get ScalarMappables.
    labeled_mappables = []
    for mappable in [*axes.images, *axes.collections]:
        label = mappable.get_label()
        if label == '_nolegend_' or mappable.get_array() is None:
            continue
        labeled_mappables.append((label, mappable))
    mappables = []
    cmaps = [(cmap, name) for name, cmap in sorted(cm._colormaps.items())]
    for label, mappable in labeled_mappables:
        cmap = mappable.get_cmap()
        if cmap not in cm._colormaps.values():
            cmaps = [(cmap, cmap.name), *cmaps]
        low, high = mappable.get_clim()
        mappabledata = [
            ('Label', label),
            ('Colormap', [cmap.name] + cmaps),
            ('Min. value', low),
            ('Max. value', high),
        ]
        if hasattr(mappable, "get_interpolation"):  # Images.
            interpolations = [(name, name)
                              for name in sorted(mimage.interpolations_names)]
            mappabledata.append(
                ('Interpolation',
                 [mappable.get_interpolation(), *interpolations]))
        mappables.append([mappabledata, label, ""])
    # Is there a scalarmappable displayed?
    has_sm = bool(mappables)

    datalist = [(general, "Axes", "")]
    if curves:
        datalist.append((curves, "Curves", ""))
    if mappables:
        datalist.append((mappables, "Images, etc.", ""))

    def apply_callback(data):
        """用于应用更改的回调"""
        orig_limits = {
            name: getattr(axes, f"get_{name}lim")()
            for name in axis_map
        }

        general, *rest = data
        curves = rest[0] if has_curve else []
        mappables = rest[1] if has_sm else []
        if len(rest) > has_curve + has_sm:
            raise ValueError("Unexpected field")

        title, *general, generate_legend = general
        axes.set_title(title)

        for i, (name, axis) in enumerate(axis_map.items()):
            axis_min, axis_max, axis_label, axis_scale = general[i * 4:i * 4 +
                                                                 4]
            if axis.get_scale() != axis_scale:
                getattr(axes, f"set_{name}scale")(axis_scale)

            axis._set_lim(axis_min, axis_max, auto=False)
            axis.set_label_text(axis_label)

            # Restore the unit data
            axis.converter = axis_converter[name]
            axis.set_units(axis_units[name])

        # Set / Curves
        for index, curve in enumerate(curves):
            line = labeled_lines[index][1]
            (label, linestyle, drawstyle, linewidth, color, marker, markersize,
             markerfacecolor, markeredgecolor) = curve
            line.set_label(label)
            line.set_linestyle(linestyle)
            line.set_drawstyle(drawstyle)
            line.set_linewidth(linewidth)
            rgba = mcolors.to_rgba(color)
            line.set_alpha(None)
            line.set_color(rgba)
            if marker != 'none':
                line.set_marker(marker)
                line.set_markersize(markersize)
                line.set_markerfacecolor(markerfacecolor)
                line.set_markeredgecolor(markeredgecolor)

        # Set ScalarMappables.
        for index, mappable_settings in enumerate(mappables):
            mappable = labeled_mappables[index][1]
            if len(mappable_settings) == 5:
                label, cmap, low, high, interpolation = mappable_settings
                mappable.set_interpolation(interpolation)
            elif len(mappable_settings) == 4:
                label, cmap, low, high = mappable_settings
            mappable.set_label(label)
            mappable.set_cmap(cmap)
            mappable.set_clim(*sorted([low, high]))

        # re-generate legend, if checkbox is checked
        if generate_legend:
            draggable = None
            ncols = 1
            _version = mpl.__version_info__ >= (2, 2)
            if axes.legend_ is not None:
                old_legend = axes.get_legend()
                if _version:
                    draggable = old_legend._draggable is not None
                ncols = old_legend._ncols
            new_legend = axes.legend(ncols=ncols)
            if new_legend and _version:
                new_legend.set_draggable(draggable)

        # Redraw
        figure = axes.get_figure()
        figure.canvas.draw()
        for name in axis_map:
            if getattr(axes, f"get_{name}lim")() != orig_limits[name]:
                figure.canvas.toolbar.push_current()
                break

    dialog = FormDialog(datalist,
                        title="Figure options",
                        parent=parent,
                        apply=apply_callback)
    dialog.ShowModal()
    # if dialog.ShowModal() != wx.ID_OK:
    #     return
