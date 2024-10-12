import argparse
import json
import numbers
import os
import re
import subprocess
import warnings
import progressbar

import numpy as np
import pandas as pd
from bokeh.embed import file_html
from bokeh.models import Whisker, NumeralTickFormatter, Range1d, ColumnDataSource, PanTool, TapTool, \
    WheelZoomTool, SaveTool, HoverTool, ResetTool, LinearAxis, AdaptiveTicker, LabelSet, Div
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.layouts import gridplot, column

from matplotlib import pyplot as plt
from matplotlib import ticker
from matplotlib.lines import Line2D
from matplotlib.ticker import PercentFormatter

colors = {
    "red": "#e60049",
    "purple": "#9b19f5",
    "orange": "#ffa300",
    "dark_green": "#047865",
    "blue": "#0bb4ff",
    "black": "#000000",
}


class Matplotlib:
    def __init__(self):
        # Hard-coded plot params
        self.title_font_size = 20
        self.label_font_size = 20
        self.tick_font_size = 18  # Also sets the font size of the scientific notation (offset, exponent)
        px = 1 / plt.rcParams['figure.dpi']
        self.plot_dimension = (1800 * px, 500 * px)
        self.grid_columns = 2

        # Variable plot params
        self.groups = {}

    @staticmethod
    def write_to_file(plot, config=None, group=None):
        # Write to file
        if config is None and group is None:
            warnings.warn("Either config or group should be present when writing to file!")
        output_path = ""
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
        os.chdir(root_dir)
        plot_dir = os.path.abspath(os.path.join(config["results_file"], os.pardir, "plots",
                                                config["output_path"]))
        if not os.path.exists(plot_dir):
            os.makedirs(plot_dir)
        os.chdir(plot_dir)
        plot.savefig(f'{config["output_file"]}.png' if group is None else f'{str(group)}.png')

    def write_group_plots(self):
        if len(self.groups) == 0:
            return
        print("Writing group plots to file...")
        progress_bar = progressbar.ProgressBar(max_value=len(self.groups))
        progress = 0
        for group, plots in self.groups.items():
            rows = len(plots) // self.grid_columns
            figs, axs = plt.subplots(rows, self.grid_columns, figsize=(
                self.plot_dimension[0] * self.grid_columns, self.plot_dimension[1] * rows))
            axs.flatten()
            for i, fig in enumerate(plots):
                # Render figure onto grid
                fig.canvas.draw()
                axs[i].imshow(fig.canvas.buffer_rgba())
            self.write_to_file(figs, group=group)
            progress += 1
            progress_bar.update(progress)
        progress_bar.finish()

    @staticmethod
    def plot_by_type(fig, config, values, ax1, ax2):
        plot_type = config["plot"]["type"]
        color_list = list(colors)
        elems = []
        for i in range(0, len(values)):
            value = values[i]
            color = colors[color_list[i % len(color_list)]]
            x_axis_values = value[0]
            x_axis_err = value[1]
            y_axis_values = value[2]
            y_axis_err = value[3]
            legend = value[4]
            position = value[5]

            if plot_type == "line":
                if x_axis_values is None:
                    x_axis_values = range(len(y_axis_values))

                if position == "right":
                    elems += ax2.errorbar(x_axis_values, y_axis_values, label=legend, marker='o', linestyle='-',
                                          color=color,
                                          xerr=x_axis_err, yerr=y_axis_err, ecolor=colors["black"], capsize=5)
                else:
                    elems += ax1.errorbar(x_axis_values, y_axis_values, label=legend, marker='o', linestyle='-',
                                          color=color,
                                          xerr=x_axis_err, yerr=y_axis_err, ecolor=colors["black"], capsize=5)

            elif plot_type == "scatter":
                dot_size = 10
                if x_axis_values is not None:
                    if position == "right":
                        ax2.scatter(x_axis_values, y_axis_values, label=legend, color=color, s=dot_size)
                    else:
                        ax1.scatter(x_axis_values, y_axis_values, label=legend, color=color, s=dot_size)
                else:
                    if position == "right":
                        ax2.scatter(y_axis_values, label=legend, color=color, s=dot_size)
                    else:
                        ax1.scatter(y_axis_values, label=legend, color=color, s=dot_size)
            elif plot_type == "histogram":
                bin_width = config["plot"]["histogram"]["bin_width"]
                if x_axis_values is not None:
                    data = x_axis_values
                else:
                    data = y_axis_values

                if bin_width != 0:
                    bins = np.arange(min(data), max(data), bin_width)
                else:
                    bins = None

                ax1.hist(data, bins=bins, label=legend, color=color)
                if bins is not None and config["x_axis"]["ticks"] is None:
                    config["x_axis"]["ticks"] = bins
                yticks = [0, 0.2, 0.4, 0.6, 0.8, 1]
                config["y_axis"]["ticks"] = [tick * len(data) for tick in yticks]
                ax1.ylim(0, len(data))
                fig.gca().yaxis.set_major_formatter(PercentFormatter(xmax=len(data)))
            else:
                warnings.warn(f"Invalid plot type, skipping plot with title {config['plot']['title']}")
                return -1
        return elems

    # Plot the values based on the x_axis_values and y_axis_values
    def plot(self, config, values):
        # Plot size
        fig, ax = plt.subplots(figsize=self.plot_dimension)

        ax1 = ax
        ax2 = None
        if any(value[5] == "right" for value in values):
            ax2 = ax1.twinx()

        # Plot the values
        elems = self.plot_by_type(fig, config, values, ax1, ax2)
        if elems == -1:
            return -1
        elems = [elem for elem in elems if isinstance(elem, Line2D)]

        # Legend
        legends = [value[4] for value in values]
        ax.legend(elems, legends, loc=0)

        # Axis labels and titles
        x_params = config["x_axis"]
        y_params = config["y_axis"]

        ax.set_xlabel(x_params["label"], fontsize=self.label_font_size)
        ax1.set_ylabel(y_params["label"], fontsize=self.label_font_size)
        if ax2 is not None:
            ax2.set_ylabel(y_params["label_right"], fontsize=self.label_font_size)
        ax.set_title(config["plot"]["title"], fontsize=self.title_font_size)

        # Axis scale
        if x_params["plot_scale"] == "log":
            ax.xscale("log")
            fig.gca().xaxis.set_major_formatter(ticker.ScalarFormatter())
        if y_params["plot_scale"] == "log":
            ax.yscale("log")
            fig.gca().yaxis.set_major_formatter(ticker.ScalarFormatter())

        # Plot ticks
        if x_params["ticks"] is not None:
            ax.set_xticks(ticks=x_params["ticks"], labels=x_params["tick_labels"], fontsize=self.tick_font_size)
        if y_params["tick_labels"] is not None:
            ax1.set_yticks(ticks=y_params["ticks"], labels=y_params["tick_labels"], fontsize=self.tick_font_size)
        else:
            ax1.tick_params(axis='y', labelsize=self.tick_font_size)
        if ax2 is not None:
            if y_params["tick_labels_right"] is not None:
                ax2.set_yticks(ticks=y_params["ticks_right"], labels=y_params["tick_labels_right"],
                               fontsize=self.tick_font_size)
            else:
                ax2.tick_params(axis='y', labelsize=self.tick_font_size)
        fig.gca().xaxis.offsetText.set_fontsize(self.tick_font_size)

        if config["plot"]["group"] is not None:
            if config["plot"]["group"] not in self.groups:
                self.groups[config["plot"]["group"]] = []
            self.groups[config["plot"]["group"]].append(fig)
        else:
            self.write_to_file(fig, config=config)


class Bokeh:
    def __init__(self):
        # Hard-coded plot params
        self.title_font_size = 20
        self.label_font_size = 20
        self.tick_font_size = 18  # Also sets the font size of the scientific notation (offset, exponent)
        self.plot_dimension = (900, 480)
        self.grid_columns = 2

        # Variable plot params
        self.groups = {}

    @staticmethod
    def write_to_file(plot, config=None, group=None):
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
        os.chdir(root_dir)
        plot_dir = os.path.abspath(os.path.join(config["results_file"], os.pardir, "plots",
                                                config["output_path"]))
        if not os.path.exists(plot_dir):
            os.makedirs(plot_dir)
        os.chdir(plot_dir)
        html = file_html(plot, CDN, config["plot"]["title"] if group is None else str(group))
        with open(f'{config["output_file"]}.html' if group is None else f'{str(group)}.html', "w") as f:
            f.write(html)

    def write_group_plots(self):
        if len(self.groups) == 0:
            return
        print("Writing group plots to file...")
        progress_bar = progressbar.ProgressBar(max_value=len(self.groups))
        progress = 0
        for group, plots in self.groups.items():
            grid = gridplot(plots, ncols=self.grid_columns)
            self.write_to_file(grid, group=group)
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
            color = colors[color_list[i % len(color_list)]]
            x_axis_values = value[0]
            x_axis_err = value[1]
            y_axis_values = value[2]
            y_axis_err = value[3]
            legend = value[4]
            position = value[5]
            visible = value[6]
            labels = value[7]

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
                             muted_color=color, muted_alpha=0.2, y_range_name=position, visible=visible)

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
                                 alpha=0.8, muted_color=color, muted_alpha=0.2, y_range_name=position, visible=visible)
                else:
                    plot.scatter(y_axis_values, legend_label=legend, color=color, size=dot_size, alpha=0.8,
                                 muted_color=color, muted_alpha=0.2, y_range_name=position, visible=visible)
            elif plot_type == "histogram":
                bin_width = config["plot"]["histogram"]["bin_width"]
                if x_axis_values is not None:
                    data = x_axis_values
                else:
                    data = y_axis_values

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
        tap = TapTool()
        save = SaveTool()
        hover = HoverTool(tooltips=tooltips)
        reset = ResetTool()

        # Plot
        plot = figure(width=self.plot_dimension[0], height=self.plot_dimension[1], title=config["plot"]["title"],
                      toolbar_location="below", toolbar_sticky=False,
                      tools=[pan, wheel_zoom, tap, save, hover, reset], x_axis_type=config["x_axis"]["plot_scale"],
                      y_axis_type=config["y_axis"]["plot_scale"])

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
            x_max += 0.1 * x_max
            x_min = min([x - err for value in values for x, err, y in
                         zip(value[0], value[1], value[2]) if not np.isnan(x) and not np.isnan(y)], default=0)
            x_min -= 0.1 * x_min
            plot.x_range = Range1d(x_min, x_max)

            # Left Y-axis
            y_max = max(
                [y + err for value in values if value[5] == "default"
                 for y, err, x in zip(value[2], value[3], value[0]) if not np.isnan(y) and not np.isnan(x)], default=10)
            y_max += 0.1 * y_max
            y_min = min(
                [y - err for value in values if value[5] == "default"
                 for y, err, x in zip(value[2], value[3], value[0]) if not np.isnan(y) and not np.isnan(x)], default=0)
            y_min -= 0.1 * y_min
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
                self.groups[config["plot"]["group"]] = []
            self.groups[config["plot"]["group"]].append(plot)
        else:
            self.write_to_file(plot, config=config)


def execute_program(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while executing the command: {e}")
        print(e.output)
        return e.output


def get_scale_by_value(value, scale_by):
    if scale_by == "min":
        return np.nanmin(value)
    elif scale_by == "max":
        return np.nanmax(value)
    elif scale_by == "count":
        return len(value)
    elif scale_by == "total":
        return np.nansum(value)
    else:
        return scale_by


# Get the value of a parameter from the results JSON object
def get_param_value(param_path, json_object, min_cutoff, max_cutoff):
    split_path = param_path.split(".")
    value = json_object
    try:
        for key in split_path:
            match = re.match(r"([^\[\]]*)((\[\d+])*)", key)
            if match:
                key = match.group(1)
                indices = re.findall(r"\[(\d+)]", match.group(2))
                if key is not None and key != "":
                    value = value[key]
                for index in indices:
                    value = value[int(index)]
            else:
                value = value[key]
    except (KeyError, IndexError, TypeError):
        warning = "Could not find the parameter at path: " + param_path + ". Skipping specified param..."
        warnings.warn(warning)
        return []
    if isinstance(value, list):
        if isinstance(min_cutoff, str):
            min_cutoff = np.percentile(value, float(min_cutoff[1:]))
        if isinstance(max_cutoff, str):
            max_cutoff = np.percentile(value, float(max_cutoff[1:]))
        if min_cutoff is not None:
            value = [np.nan if elem <= min_cutoff else elem for elem in value if isinstance(elem, numbers.Number)]
        if max_cutoff is not None:
            value = [np.nan if elem >= max_cutoff else elem for elem in value if isinstance(elem, numbers.Number)]
        if min_cutoff is not None or max_cutoff is not None:
            nan_count = np.sum(np.isnan(value))
            if min_cutoff is not None or max_cutoff is not None:
                print("% of values removed due to cutoffs from path", param_path, "is",
                      nan_count / len(value) * 100, "%")
    elif isinstance(value, numbers.Number):
        if min_cutoff is not None and value < min_cutoff:
            value = np.nan
        if max_cutoff is not None and value > max_cutoff:
            value = np.nan
    return value


# Get the X and Y axis values to plot
def get_values(config):
    os.chdir(root_dir)
    # Read the JSON file
    with open(config["results_file"], "r") as f:
        results = json.load(f)
        if not isinstance(results, list):
            results = [results]

    # Initialize the parameters
    x_params = config["x_axis"]
    y_params = config["y_axis"]
    values = []  # Consists of tuples of (x_values, x_err_values, y_values, y_err_values, label, y_position)

    # Check X-axis has either 1 value (in which case we duplicate it for all Y) or the same number of values as Y-axis
    if (len(x_params["values"]) != 1
            and y_params["values"] is not None
            and len(x_params["values"]) != len(y_params["values"])):
        raise Exception("X-axis should have either 1 value or the same number of values as Y-axis!")

    # Duplicate x_params for all instances of y_params if necessary
    if (y_params["values"] is not None
            and len(y_params["values"]) > 1
            and len(x_params["values"]) == 1):
        x_params["values"] = [x_params["values"][0] for _ in range(0, len(y_params["values"]))]

    length = len(y_params["values"]) if y_params["values"] is not None else len(x_params["values"])

    # Get all the values
    for i in range(0, length):
        y_value_param = y_params["values"][i] if y_params["values"] else None
        x_value_param = x_params["values"][i] if x_params["values"] else None
        max_length = 0
        legend = None
        position = "default"
        labels = None

        if y_value_param is not None:
            # Legend
            legend = y_value_param["legend"]
            # Position
            position = y_value_param["position"]
            # Labels
            if y_value_param["labels"] is not None:
                labels = [labels for result in results if (
                    labels := get_param_value(y_value_param["labels"], result, None, None)
                ) is not None]
                labels = np.array(labels).T
            # Values
            y_values = [param_value for result in results if
                        (param_value := get_param_value(y_value_param["param"], result,
                                                        y_value_param["min_cutoff"],
                                                        y_value_param["max_cutoff"])) is not None]
            y_values = np.array(y_values).T
            y_value_param["scale_by"] = get_scale_by_value(y_values, y_value_param["scale_by"])
            y_values = y_values / y_value_param["scale_by"]

            # Pad the values with NaNs if y_values is array of arrays
            if (isinstance(y_values, (list, np.ndarray))
                    and len(y_values) > 0
                    and isinstance(y_values[0], (list, np.ndarray))):
                max_length = max(len(y) for y in y_values)
                y_values = np.array([np.append(y, [np.nan] * (max_length - len(y))) for y in y_values])
            else:
                max_length = len(y_values)

            # Error values
            if y_value_param["error"] is not None:
                y_err_values = [param_value for result in results if
                                (param_value := get_param_value(y_value_param["error"], result,
                                                                None,
                                                                None)) is not None]
                if y_err_values is not None:
                    y_err_values = np.array(y_err_values).T
                    y_err_values = y_err_values / y_value_param["scale_by"]
            else:
                # Set err_values as 0
                if (isinstance(y_values, (list, np.ndarray))
                        and len(y_values) > 0
                        and isinstance(y_values[0], (list, np.ndarray))):
                    y_err_values = [[0 for _ in range(0, max_length)] for _ in range(0, len(y_values))]
                else:
                    y_err_values = [[0 for _ in range(0, max_length)]]
                y_err_values = np.array(y_err_values)
        else:
            y_values = y_err_values = None

        if x_value_param is not None:
            # Legend
            if legend is None:
                legend = x_value_param["legend"]  # Only set if y_param has not already set it

            # values
            x_values = [param_value for result in results if
                        (param_value := get_param_value(x_value_param["param"], result,
                                                        x_value_param["min_cutoff"],
                                                        x_value_param["max_cutoff"])) is not None]
            x_values = np.array(x_values).T
            x_value_param["scale_by"] = get_scale_by_value(x_values, x_value_param["scale_by"])
            x_values = x_values / x_value_param["scale_by"]

            # Pad the values with NaNs if x_values is array of arrays
            if (isinstance(x_values, (list, np.ndarray))
                    and len(x_values) > 0
                    and isinstance(x_values[0], (list, np.ndarray))):
                max_length = max(len(x) for x in x_values)
                x_values = np.array([np.append(x, [np.nan] * (max_length - len(x))) for x in x_values])

            # Error values
            if x_value_param["error"] is not None:
                x_err_values = [param_value for result in results if
                                (param_value := get_param_value(x_value_param["error"], result,
                                                                None,
                                                                None)) is not None]
                if x_err_values is not None:
                    x_err_values = np.array(x_err_values).T
                    x_err_values = x_err_values / x_value_param["scale_by"]
            else:
                # Set err_values as 0
                if (isinstance(x_values, (list, np.ndarray))
                        and len(x_values) > 0
                        and isinstance(x_values[0], (list, np.ndarray))):
                    x_err_values = [[0 for _ in range(0, max_length)] for _ in range(0, len(x_values))]
                else:
                    x_err_values = [[0 for _ in range(0, max_length)]]
        else:
            # Generate x_values as index and x_err_values as 0
            if y_values is not None and isinstance(y_values[0], (list, np.ndarray)):
                x_values = [[i for i in range(0, max_length)] for _ in range(0, len(y_values))]
                x_err_values = [[0 for _ in range(0, max_length)] for _ in range(0, len(y_values))]
            else:
                x_values = [i for i in range(0, max_length)]
                x_err_values = [[0 for _ in range(0, max_length)]]

        # Sort the values by X-axis
        if len(x_values) != len(x_err_values):
            warning = (f"Lengths of x_values and x_err_values do not match!"
                       f"Skipping param {x_value_param['param']} from plot {config['plot']['title']}")
            warnings.warn(warning)
            continue
        if len(y_values) != len(y_err_values):
            warning = (f"Lengths of y_values and y_err_values do not match!"
                       f"Skipping param {y_value_param['param']} from plot {config['plot']['title']}")
            warnings.warn(warning)
            continue
        if len(x_values) != len(y_values):
            warning = "Lengths of x_values and y_values do not match!"
            warnings.warn(warning)
            if len(x_values) == 1:
                warning = (f"Duplicating X-axis values for {x_value_param['param']}, "
                           f"{y_value_param['param']} from plot {config['plot']['title']}")
                warnings.warn(warning)
                x_values = np.array([x_values for _ in range(len(y_values))])
                x_err_values = np.array([x_err_values for _ in range(len(y_values))])
        if len(y_values) == 1 and len(x_values) > 1:
            warning = (f"Duplicating Y-axis values for {x_value_param['param']}, "
                       f"{y_value_param['param']} from plot {config['plot']['title']}")
            warnings.warn(warning)
            y_values = np.array([y_values for _ in range(len(x_values))])
            y_err_values = np.array([y_err_values for _ in range(len(x_values))])
        if labels is None:
            labels = [None] * len(y_values)
        if len(labels) != len(y_values):
            warning = (f"Length of labels does not match Y-axis length!\n" +
                       f"Skipping labels for param {y_value_param['param']} from plot {config['plot']['title']}")
            warnings.warn(warning)
            labels = [None] * len(y_values)

        # Sort the array
        if y_values is not None and len(y_values) > 0 and x_values is not None and len(x_values) > 0:
            combined_array = zip(x_values, x_err_values, y_values, y_err_values, labels)
            sorted_array = sorted(combined_array, key=lambda x: x[0])
            x_values, x_err_values, y_values, y_err_values, labels = zip(*sorted_array)
            y_values = [item[0] if isinstance(item, (list, np.ndarray)) else item for item in y_values]
            y_err_values = [item[0] if isinstance(item, (list, np.ndarray)) else item for item in y_err_values]
            labels = [item[0] if isinstance(item, (list, np.ndarray)) else item for item in labels]
            if all(elem is None for elem in labels):
                labels = None

        # Unpack x_values if necessary
        if x_values is not None:
            x_values = [item[0] if isinstance(item, (list, np.ndarray)) else item for item in x_values]
            x_err_values = [item[0] if isinstance(item, (list, np.ndarray)) else item for item in x_err_values]

        values.append(
            (x_values, x_err_values, y_values, y_err_values, legend, position, y_value_param["visible"], labels))

    return values


def parse_arguments():
    # Create ArgumentParser object
    parser = argparse.ArgumentParser(description='Run multiple experiments with different configurations')

    # Add arguments
    parser.add_argument("-c", "--configs", default="plot_config.json",
                        help='The configuration file for the plot')
    parser.add_argument("-d", "--dir", default=None,
                        help='(Optional) The directory relative to which the paths are in the plot_config')

    # Return the params
    return parser.parse_args()


def check_config(config):
    # Check required parameters
    if ("results_file" not in config or config["results_file"] == '' or config["results_file"] is None
            or not isinstance(config["results_file"], str)):
        raise Exception("Missing required parameter: results_file")
    if not os.path.isabs(config["results_file"]):
        config["results_file"] = os.path.join(root_dir, config["results_file"])
    if not os.path.exists(config["results_file"]):
        return -1
    if "output_path" not in config or config["output_path"] is None or not isinstance(config["output_path"], str):
        config["output_path"] = ''
    else:
        if ':' in (config["output_path"]):
            warnings.warn(": (colon) is not allowed in output path. Replacing it with _")
            config["output_path"] = config["output_path"].replace(":", "_")
    if "plot" not in config or config["plot"] is None or not isinstance(config["plot"], dict):
        raise Exception("Missing required parameter: plot")
    if ("x_axis" not in config or "y_axis" not in config or config["x_axis"] is None or config["y_axis"] is None
            or not isinstance(config["x_axis"], dict) or not isinstance(config["y_axis"], dict)):
        raise Exception("Missing required parameter: x_axis or y_axis")

    # Check for plot parameters
    plot_params = config["plot"]
    if "group" not in plot_params or plot_params["group"] == '':
        plot_params["group"] = None
    else:
        if plot_params["group"]:
            if ':' in (plot_params["group"]):
                warnings.warn(": (colon) is not allowed in group name. Replacing it with _")
                plot_params["group"] = plot_params["group"].replace(":", "_")
            plot_params["group"] = config["output_path"] + ":" + plot_params["group"]
    if ("renderer" not in plot_params or plot_params["renderer"] == '' or plot_params["renderer"] is None
            or not isinstance(plot_params["renderer"], str)):
        plot_params["renderer"] = "bokeh"
    if "type" not in plot_params or plot_params["type"] == '' or plot_params["type"] is None:
        raise Exception("Missing required parameter: plot: type")
    if plot_params["type"] not in ["line", "scatter", "histogram", "heatmap"]:
        raise Exception("Invalid plot type. Must be one of: line, scatter, histogram or heatmap")
    if "notes" not in plot_params or not isinstance(plot_params["notes"], str):
        plot_params["notes"] = None
    # Check for plot-type specific parameters
    # Histogram
    if plot_params["type"] == "histogram":
        if ("histogram" not in plot_params or plot_params["histogram"] is None
                or not isinstance(plot_params["histogram"], dict)):
            plot_params["histogram"] = {}
        if ("bin_width" not in plot_params["histogram"] or plot_params["histogram"]["bin_width"] is None
                or not isinstance(plot_params["histogram"]["bin_width"], numbers.Number)):
            plot_params["histogram"]["bin_width"] = 0

    # Line
    if plot_params["type"] == "line":
        if "line" not in plot_params or plot_params["line"] is None or not isinstance(plot_params["line"], dict):
            plot_params["line"] = {}

    # Scatter
    if plot_params["type"] == "scatter":
        if ("scatter" not in plot_params or plot_params["scatter"] is None
                or not isinstance(plot_params["scatter"], dict)):
            plot_params["scatter"] = {}

    # Check for axis parameters
    y_params = config["y_axis"]
    x_params = config["x_axis"]

    # Delete values where "param" is empty or non-existent
    items_to_delete = []
    if "values" in x_params:
        for value in x_params["values"]:
            if ("param" not in value or value["param"] == '' or value["param"] is None
                    or not isinstance(value["param"], str)):
                items_to_delete.append(value)
    x_params["values"] = [value for value in x_params["values"] if value not in items_to_delete]
    if "values" in y_params:
        for value in y_params["values"]:
            if ("param" not in value or value["param"] == '' or value["param"] is None
                    or not isinstance(value["param"], str)):
                items_to_delete.append(value)
    y_params["values"] = [value for value in y_params["values"] if value not in items_to_delete]
    if len(x_params["values"]) == 0 and len(y_params["values"]) == 0:
        raise Exception("No valid values to plot")

    # Check for Y-axis parameters
    # Check of required parameters
    if plot_params["type"] != "histogram":
        if "values" not in y_params or len(y_params["values"]) == 0:
            raise Exception("Missing required parameter in y_axis: values")
        if len(x_params["values"]) != len(y_params["values"]):
            if len(x_params["values"]) == 1:
                warnings.warn("The number of values in X-axis and Y-axis must be the same."
                              "Duplicating X-axis values for all Y-axis values")
                for i in range(0, len(y_params["values"]) - 1):
                    x_params["values"].append(x_params["values"][0])
            else:
                raise Exception("The number of values in X-axis and Y-axis must be the same.")

    else:  # If plot type is histogram
        if "values" not in y_params and "values" not in x_params:
            raise Exception("Missing values for either axis. Need one!")
        elif len(y_params["values"]) != 1 and len(x_params["values"]) != 1:
            raise Exception("Too many values for either axis. Need one!")
        elif "values" not in y_params or len(y_params["values"]) != 1:
            y_params["values"] = None
        elif "values" not in x_params or len(x_params["values"]) != 1:
            x_params["values"] = None

    if y_params["values"] is not None:
        for value in y_params["values"]:
            if "error" not in value or value["error"] == '' or not isinstance(value["error"], str):
                value["error"] = None
            if "legend" not in value or not isinstance(value["legend"], str):
                value["legend"] = ""
            if "visible" not in value or not isinstance(value["visible"], bool):
                value["visible"] = True
            if "labels" not in value or not isinstance(value["labels"], (str, list)):
                value["labels"] = None
            if ("position" not in value or value["position"] == '' or value["position"] == 'left'
                    or not isinstance(value["position"], str)):
                value["position"] = "default"
            if value["position"] != "default" and value["position"] != "right":
                raise Exception("Y-axis position should be either left or right")
            if "scale_by" not in value or not isinstance(value["scale_by"], (numbers.Number, str)):
                value["scale_by"] = 1
            if isinstance(value["scale_by"], str) and value["scale_by"] not in ["min", "max", "count", "total"]:
                value["scale_by"] = 1
            if "min_cutoff" not in value or not isinstance(value["min_cutoff"], (numbers.Number, str)):
                value["min_cutoff"] = None
            if isinstance(value["min_cutoff"], str) and value["min_cutoff"][0] != "p":
                value["min_cutoff"] = None
            if "max_cutoff" not in value or not isinstance(value["max_cutoff"], (numbers.Number, str)):
                value["max_cutoff"] = None
            if isinstance(value["max_cutoff"], str) and value["max_cutoff"][0] != "p":
                value["max_cutoff"] = None

    # Check for optional parameters
    if "label" not in y_params or y_params["label"] is None or not isinstance(y_params["label"], str):
        y_params["label"] = ""
    if ("label_right" not in y_params or y_params["label_right"] == '' or y_params["label_right"] is None
            or not isinstance(y_params["label_right"], str)):
        y_params["label_right"] = y_params["label"]
    if ("plot_scale" not in y_params or y_params["plot_scale"] == '' or y_params["plot_scale"] is None
            or not isinstance(y_params["plot_scale"], str)):
        y_params["plot_scale"] = "linear"
    if "ticks" not in y_params or len(y_params["ticks"]) == 0 or not isinstance(y_params["ticks"], list):
        y_params["ticks"] = None
    if ("tick_labels" not in y_params or len(y_params["tick_labels"]) == 0 or y_params["ticks"] is None
            or not isinstance(y_params["tick_labels"], list)):
        y_params["tick_labels"] = None
    if ("ticks_right" not in y_params or len(y_params["ticks_right"]) == 0
            or not isinstance(y_params["ticks_right"], list)):
        y_params["ticks_right"] = None
    if ("tick_labels_right" not in y_params or len(y_params["tick_labels_right"]) == 0
            or y_params["ticks_right"] is None or not isinstance(y_params["tick_labels_right"], list)):
        y_params["tick_labels_right"] = None
    if y_params["ticks"] is not None and y_params["tick_labels"] is not None:
        if len(y_params["ticks"]) != len(y_params["tick_labels"]):
            raise Exception(
                f"The number of y_ticks and y_tick_labels must be the same on Y-axis. Faulty config with results file "
                f"{config['results_file']}")
        else:
            temp = {}
        for i in range(0, len(y_params["ticks"])):
            temp[y_params["ticks"][i]] = y_params["tick_labels"][i]
        if plot_params["renderer"] == "bokeh":
            y_params["tick_labels"] = temp

    if y_params["ticks_right"] is not None and y_params["tick_labels_right"] is not None:
        if len(y_params["ticks_right"]) != len(y_params["tick_labels_right"]):
            raise Exception(
                f"The number of y_ticks and y_tick_labels must be the same on the right Y-axis."
                f"Faulty config with results file {config['results_file']}")
        else:
            temp = {}
            for i in range(0, len(y_params["ticks_right"])):
                temp[y_params["ticks_right"][i]] = y_params["tick_labels_right"][i]
            if plot_params["renderer"] == "bokeh":
                y_params["tick_labels"] = temp
    else:
        # Only necessary for right Y-axis due to how it is instantiated
        if plot_params["renderer"] == "bokeh":
            y_params["ticks_right"] = AdaptiveTicker()
            y_params["tick_labels_right"] = {}

    # Check for X-axis parameters
    if "values" not in x_params or len(x_params["values"]) == 0 or not isinstance(x_params["values"], list):
        x_params["values"] = None
    if ("label" not in x_params or x_params["label"] == '' or x_params["label"] is None
            or not isinstance(x_params["label"], str)):
        x_params["label"] = "index"
    if ("plot_scale" not in x_params or x_params["plot_scale"] == '' or x_params["plot_scale"] is None
            or not isinstance(x_params["plot_scale"], str)):
        x_params["plot_scale"] = "linear"
    if "ticks" not in x_params or len(x_params["ticks"]) == 0 or not isinstance(x_params["ticks"], list):
        x_params["ticks"] = None
    if ("tick_labels" not in x_params or len(x_params["tick_labels"]) == 0 or x_params["ticks"] is None
            or not isinstance(x_params["tick_labels"], list)):
        x_params["tick_labels"] = None
    if x_params["ticks"] is not None and x_params["tick_labels"] is not None:
        if len(x_params["ticks"]) != len(x_params["tick_labels"]):
            raise Exception(
                f"The number of x_ticks and x_tick_labels must be the same on the X-axis."
                f"Faulty config with results file {config['results_file']}")
        else:
            temp = {}
            for i in range(0, len(x_params["ticks"])):
                temp[x_params["ticks"][i]] = x_params["tick_labels"][i]
            if plot_params["renderer"] == "bokeh":
                x_params["tick_labels"] = temp

    if x_params["values"] is not None:
        for value in x_params["values"]:
            if "error" not in value or value["error"] == '' or not isinstance(value["error"], str):
                value["error"] = None
            if "legend" not in value or not isinstance(value["legend"], str):
                value["legend"] = ""
            if "scale_by" not in value or not isinstance(value["scale_by"], (numbers.Number, str)):
                value["scale_by"] = 1
            if isinstance(value["scale_by"], str) and value["scale_by"] not in ["min", "max", "count", "total"]:
                value["scale_by"] = 1
            if "min_cutoff" not in value or not isinstance(value["min_cutoff"], (numbers.Number, str)):
                value["min_cutoff"] = None
            if isinstance(value["min_cutoff"], str) and value["min_cutoff"][0] != "p":
                value["min_cutoff"] = None
            if "max_cutoff" not in value or not isinstance(value["max_cutoff"], (numbers.Number, str)):
                value["max_cutoff"] = None
            if isinstance(value["max_cutoff"], str) and value["max_cutoff"][0] != "p":
                value["max_cutoff"] = None

    if ("title" not in plot_params or plot_params["title"] == '' or plot_params["title"] is None
            or not isinstance(plot_params["title"], str)):
        plot_params["title"] = f'{x_params["label"]} vs {y_params["label"]}'

    if ("output_file" not in config or config["output_file"] == '' or config["output_file"] is None
            or not isinstance(config["output_file"], str)):
        config["output_file"] = plot_params["title"].replace(" ", "_")


def main():
    args = parse_arguments()
    if args.dir is not None:
        global root_dir
        root_dir = args.dir
    with open(args.configs, "r") as f:
        configs = json.load(f)

    bkh = Bokeh()
    mpl = Matplotlib()

    progress_bar = progressbar.ProgressBar(max_value=len(configs), redirect_stdout=True, redirect_stderr=True)

    for idx, config in enumerate(configs):
        print(f"\nStarting plot {config['plot']['title']} and results file {config['results_file']}")
        if check_config(config) == -1:
            warnings.warn("No results file found. Skipping plot...")
            continue
        # Get the values to plot
        values = get_values(config)
        if values is None or len(values) == 0:
            continue
        if config["plot"]["renderer"] == "bokeh":
            bkh.plot(config, values)
        elif config["plot"]["renderer"] == "matplotlib":
            mpl.plot(config, values)
        else:
            warnings.warn("Specified Renderer not supported. Must be either 'bokeh' or 'matplotlib' "
                          f"for config with results file {config['results_file']}, ignoring this config")
        progress_bar.update(idx + 1)

    progress_bar.finish()
    bkh.write_group_plots()
    mpl.write_group_plots()


if __name__ == "__main__":
    # Set the working directory
    root_dir = execute_program(["git", "rev-parse", "--show-superproject-working-tree"])
    if root_dir == "":
        root_dir = execute_program(["git", "rev-parse", "--show-toplevel"])
    root_dir = root_dir.strip('\n')
    main()
