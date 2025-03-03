import numbers
import os
import warnings

import numpy as np
import pandas as pd
import progressbar
from bokeh.embed import file_html
from bokeh.io import export_png, export_svg
from bokeh.layouts import gridplot, column
from bokeh.models import Whisker, NumeralTickFormatter, Range1d, ColumnDataSource, PanTool, TapTool, \
    WheelZoomTool, BoxZoomTool, SaveTool, HoverTool, ResetTool, LinearAxis, LabelSet, Div
from bokeh.plotting import figure
from bokeh.resources import CDN

colors = {
    "red": "#e60049",
    "purple": "#9b19f5",
    "orange": "#ffa300",
    "dark_green": "#047865",
    "blue": "#0bb4ff",
    "golden": "#ffa600",
    "dark_magenta": "#d45087",
    "violet": "#665191",
    "black": "#444444",
}


class Bokeh:
    def __init__(self, root_dir):
        # Hard-coded plot params
        self.title_font_size = 20
        self.label_font_size = 20
        self.tick_font_size = 18  # Also sets the font size of the scientific notation (offset, exponent)
        self.plot_dimension = (900, 480)
        self.grid_columns = 2
        self.root_dir = root_dir

        # Variable plot params
        self.groups = {}

    def write_to_file(self, plot, output_formats, config=None, group=None):
        # Write to file
        if config is None and group is None:
            warnings.warn("Either config or group should be present when writing to file!")
        output_path = ""
        # Discard output path from group
        if group is not None:
            output_path, group = str(group).split(":")

        if config is None:
            config = {
                "results_file": "results.json",
                "output_path": output_path,
                "plot": {
                    "title": str(group)
                },
                "output_file": "plot"
            }
        os.chdir(self.root_dir)
        plot_dir = os.path.abspath(os.path.join(config["results_file"], os.pardir, "plots",
                                                config["output_path"]))
        if not os.path.exists(plot_dir):
            os.makedirs(plot_dir)
        os.chdir(plot_dir)
        output_file_name = f'{config["output_file"]}' if group is None else f'{str(group)}'

        for output_format in output_formats:
            if output_format not in ["html", "svg", "png"]:
                warnings.warn("Output format not supported. Defaulting to html")
                output_format = "html"
            if output_format == "html":
                html = file_html(plot, CDN, config["plot"]["title"] if group is None else str(group))
                with open(output_file_name + ".html", "w") as f:
                    f.write(html)
            elif output_format == "svg":
                export_svg(plot, filename=output_file_name + ".svg")
            elif output_format == "png":
                curr_toolbar_location = plot.toolbar_location
                plot.toolbar_location = None
                export_png(plot, filename=output_file_name + ".png")
                plot.toolbar_location = curr_toolbar_location

    def write_group_plots(self):
        if len(self.groups) == 0:
            return
        print("Writing group plots to file...")
        progress_bar = progressbar.ProgressBar(max_value=len(self.groups))
        progress = 0
        for group, (plots, output_format) in self.groups.items():
            grid = gridplot(plots, ncols=self.grid_columns)
            self.write_to_file(grid, output_formats=output_format, group=group)
            progress += 1
            progress_bar.update(progress)
        progress_bar.finish()

    @staticmethod
    def get_heatmap_color(min_val: float, max_val: float, value: float):
        if value < min_val or value > max_val:
            print("Value is out of range for heatmap. This should never happen! Report this bug")

        ratio = (value - min_val) / (max_val - min_val)
        r = int(255 * ratio)
        g = int(255 * (1 - ratio))
        b = 0

        return r, g, b

    def plot_by_type(self, plot, config, values):
        plot_type = config["plot"]["type"]
        color_list = list(colors)
        for i in range(0, len(values)):
            value = values[i]
            x_axis_values = value[0]
            x_axis_err = value[1]
            y_axis_values = value[2]
            y_axis_err = value[3]
            legend = value[4]
            position = value[5]
            visible = value[6]
            labels = value[7]
            color = value[8]
            marker = value[9]
            color = color if color is not None else colors[color_list[i % len(color_list)]]

            label_offset_x = 5
            label_offset_y = 5

            # Skip the plot if no parameters were found
            if y_axis_values is None or len(y_axis_values) == 0:
                return -1

            if plot_type == "line":
                if x_axis_values is None:
                    x_axis_values = range(len(y_axis_values))

                # Draw line and points
                plot.line(x_axis_values, y_axis_values, legend_label=legend, line_width=2, line_color=color, alpha=0.8,
                          muted_color=color, muted_alpha=0.2, y_range_name=position, visible=visible)
                plot.scatter(x_axis_values, y_axis_values, fill_color=color, size=8, alpha=0.8, legend_label=legend,
                             marker=marker, muted_color=color, muted_alpha=0.2, y_range_name=position, visible=visible)

                # Draw error bars
                upper_x = pd.Series([x + err for x, err in zip(x_axis_values, x_axis_err)], index=x_axis_values)
                lower_x = pd.Series([x - err for x, err in zip(x_axis_values, x_axis_err)], index=x_axis_values)
                upper_y = pd.Series([y + err for y, err in zip(y_axis_values, y_axis_err)], index=x_axis_values)
                lower_y = pd.Series([y - err for y, err in zip(y_axis_values, y_axis_err)], index=x_axis_values)

                source_x = ColumnDataSource(data=dict(base=y_axis_values, upper=upper_x, lower=lower_x))
                source_y = ColumnDataSource(data=dict(base=x_axis_values, upper=upper_y, lower=lower_y))
                if x_axis_err != [0] * len(x_axis_err):
                    plot.add_layout(Whisker(base="base", upper="upper", lower="lower", level='glyph', dimension='width',
                                            source=source_x, line_color='black', y_range_name=position,
                                            visible=visible))
                if y_axis_err != [0] * len(y_axis_err):
                    # plot.add_layout(Whisker(base="base", upper="upper", lower="lower", level='glyph',
                    #                        dimension='height', source=source_y, line_color='black'))
                    # Vertical area for 1 std deviation
                    plot.varea(x="base", y1="lower", y2="upper", source=source_y, fill_color=color, fill_alpha=0.15,
                               legend_label=legend, y_range_name=position, visible=visible)

            elif plot_type == "scatter":
                dot_size = 10
                if x_axis_values is not None:
                    plot.scatter(x_axis_values, y_axis_values, legend_label=legend, color=color, size=dot_size,
                                 marker=marker, alpha=0.8, muted_color=color, muted_alpha=0.2, y_range_name=position,
                                 visible=visible)
                else:
                    plot.scatter(y_axis_values, legend_label=legend, color=color, size=dot_size, alpha=0.8,
                                 marker=marker, muted_color=color, muted_alpha=0.2, y_range_name=position,
                                 visible=visible)
            elif plot_type == "histogram":
                bin_width = config["plot"]["histogram"]["bin_width"]
                if x_axis_values is not None:
                    data = x_axis_values
                else:
                    data = y_axis_values

                data = [elem for elem in data if not np.isnan(elem)]
                if bin_width != 0:
                    bins = np.arange(min(data), max(data), bin_width)
                else:
                    bins = "auto"

                hist, edges = np.histogram(data, bins=bins)
                hist = hist / sum(hist)

                plot.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], fill_color=color, line_color="white",
                          legend_label=legend, alpha=0.8, muted_color=color, muted_alpha=0.2, y_range_name=position,
                          visible=visible)
                if bins != "auto" and config["x_axis"]["ticks"] is None:
                    config["x_axis"]["ticks"] = bins
                yticks = [0, 0.2, 0.4, 0.6, 0.8, 1]
                config["y_axis"]["ticks"] = yticks
                plot.y_range = Range1d(0, 1)
                plot.yaxis.formatter = NumeralTickFormatter(format="0%")
            elif plot_type == "heatmap":
                if labels is None:
                    print("Heatmap requires labels for y axes")
                    return -1
                min_val = np.nanmin(
                    [float(label) if isinstance(label, (numbers.Number, str)) else float('nan') for label in labels])
                max_val = np.nanmax(
                    [float(label) if isinstance(label, (numbers.Number, str)) else float('nan') for label in labels])
                for j in range(0, len(x_axis_values)):
                    if labels[j] is None:
                        continue
                    plot.rect(x=x_axis_values[j], y=y_axis_values[j], width=1, height=1,
                              fill_color=Bokeh.get_heatmap_color(min_val, max_val, float(labels[j])),
                              line_color=None)

                label_offset_x = 0
                label_offset_y = 0
            else:
                warnings.warn(f"Invalid plot type, skipping plot with title {config['plot']['title']}")
                return -1

            # Add Labels
            if labels is not None:
                source = ColumnDataSource(data=dict(x=x_axis_values, y=y_axis_values, labels=labels))
                label_set = LabelSet(x='x', y='y', text='labels', source=source,
                                     x_offset=label_offset_x, y_offset=label_offset_y,
                                     text_font_size=f"{self.label_font_size / 2}pt",
                                     text_align="center", text_baseline="middle",
                                     text_color="white")
                plot.add_layout(label_set)

    # Plot the values based on the x_axis_values and y_axis_values
    def plot(self, config, values):
        # Plot hover
        tooltips = [("(x, y)", "($x, $y)"), ("mode", "vline")]

        # Plot tools
        pan = PanTool()
        wheel_zoom = WheelZoomTool()
        box_zoom = BoxZoomTool()
        tap = TapTool()
        save = SaveTool()
        hover = HoverTool(tooltips=tooltips)
        reset = ResetTool()

        x_dim = config["plot"]["dimensions"][0]
        x_dim = x_dim if x_dim is not None else self.plot_dimension[0]
        y_dim = config["plot"]["dimensions"][1]
        y_dim = y_dim if y_dim is not None else self.plot_dimension[1]
        # Plot
        plot = figure(width=x_dim, height=y_dim, title=config["plot"]["title"],
                      toolbar_location="below", toolbar_sticky=False,
                      tools=[pan, wheel_zoom, box_zoom, tap, save, hover, reset],
                      x_axis_type=config["x_axis"]["plot_scale"], y_axis_type=config["y_axis"]["plot_scale"],
                      output_backend="webgl")

        # Plot borders
        plot.min_border = 30

        # Set default active tools
        plot.toolbar.active_drag = pan
        plot.toolbar.active_scroll = wheel_zoom
        plot.toolbar.active_tap = None

        # Axis labels and titles
        x_params = config["x_axis"]
        y_params = config["y_axis"]

        plot.xaxis.axis_label = x_params["label"]
        plot.yaxis.axis_label = y_params["label"]
        plot.axis.axis_label_text_font_size = f"{self.label_font_size}pt"
        plot.title.text = config["plot"]["title"]
        plot.title.text_font_size = f"{self.title_font_size}pt"

        # Axis scale
        if x_params["plot_scale"] == "log":
            plot.xaxis.formatter = NumeralTickFormatter(format="0")
        if y_params["plot_scale"] == "log":
            plot.yaxis.formatter = NumeralTickFormatter(format="0")

        # Plot ticks
        if x_params["ticks"] is not None:
            plot.xaxis.ticker = x_params["ticks"]
        if x_params["tick_labels"] is not None:
            plot.xaxis.major_label_overrides = x_params["tick_labels"]
        if y_params["ticks"] is not None:
            plot.yaxis.ticker = y_params["ticks"]
        if y_params["tick_labels"] is not None:
            plot.yaxis.major_label_overrides = y_params["tick_labels"]
        plot.axis.major_label_text_font_size = f"{self.tick_font_size}pt"

        # Axis limits (min, max with 10% padding)
        if config["plot"]["type"] != "histogram":
            # X-axis
            x_max = max([x + err for value in values for x, err, y in
                         zip(value[0], value[1], value[2]) if not np.isnan(x) and not np.isnan(y)], default=10)
            x_min = min([x - err for value in values for x, err, y in
                         zip(value[0], value[1], value[2]) if not np.isnan(x) and not np.isnan(y)], default=0)
            diff = x_max - x_min
            x_max = x_max + 0.1 * diff
            x_min = x_min - 0.1 * diff
            plot.x_range = Range1d(x_min, x_max)

            # Left Y-axis
            y_max = max(
                [y + err for value in values if value[5] == "default"
                 for y, err, x in zip(value[2], value[3], value[0]) if not np.isnan(y) and not np.isnan(x)], default=10)
            y_min = min(
                [y - err for value in values if value[5] == "default"
                 for y, err, x in zip(value[2], value[3], value[0]) if not np.isnan(y) and not np.isnan(x)], default=0)
            diff = y_max - y_min
            y_max = y_max + 0.1 * diff
            y_min = y_min - 0.1 * diff
            plot.y_range = Range1d(y_min, y_max)

            # Right Y-axis
            if any(value[5] == "right" for value in values):
                y_max = max(
                    [y + err for value in values if value[5] == "right" for y, err, x in
                     zip(value[2], value[3], value[0]) if not np.isnan(y) and not np.isnan(x)], default=10)
                y_max += 0.1 * y_max
                y_min = min(
                    [y - err for value in values if value[5] == "right" for y, err, x in
                     zip(value[2], value[3], value[0]) if not np.isnan(y) and not np.isnan(x)], default=0)
                y_min -= 0.1 * y_min
                plot.extra_y_ranges["right"] = Range1d(y_min, y_max)
                # Add the right axis
                right_y_axis = LinearAxis(
                    axis_label=y_params["label_right"],
                    y_range_name="right",
                    ticker=y_params["ticks_right"],
                    major_label_overrides=y_params["tick_labels_right"],
                    axis_label_text_font_size=f"{self.label_font_size}pt",
                    major_label_text_font_size=f"{self.tick_font_size}pt"
                )
                plot.add_layout(right_y_axis, "right")

        # Plot the values
        retval = self.plot_by_type(plot, config, values)
        if retval == -1:
            return -1

        # Legend Location
        if len(plot.legend) > 0:
            plot.legend.click_policy = "hide"  # "hide" or "mute"
            plot.legend.location = "top_left"
            plot.legend.ncols = int(len(plot.legend.items) / 10) + 1
            if plot.legend.ncols > 2:
                plot.add_layout(plot.legend[0], "below")
                plot.height = int(plot.height * 1.5)
            else:
                plot.add_layout(plot.legend[0], "center")

        # Notes
        if config["plot"]["notes"] is not None:
            notes = Div(text=config["plot"]["notes"])
            plot = column(plot, notes)

        if config["plot"]["group"] is not None:
            if config["plot"]["group"] not in self.groups:
                self.groups[config["plot"]["group"]] = ([], config["plot"]["output_format"])
            self.groups[config["plot"]["group"]][0].append(plot)
        else:
            self.write_to_file(plot, config["plot"]["output_format"], config=config)
