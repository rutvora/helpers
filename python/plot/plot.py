import argparse
import json
import numbers
import os
import subprocess
import warnings

import numpy as np
import pandas as pd
from bokeh.embed import file_html
from bokeh.models import Whisker, NumeralTickFormatter, Range1d, ColumnDataSource, PanTool, TapTool, \
    WheelZoomTool, SaveTool, HoverTool, ResetTool, LinearAxis, AdaptiveTicker
from bokeh.plotting import figure
from bokeh.resources import CDN
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
    def __init__(self, config, values):
        # Hard-coded plot params
        self.title_font_size = 20
        self.label_font_size = 20
        self.tick_font_size = 18  # Also sets the font size of the scientific notation (offset, exponent)
        px = 1 / plt.rcParams['figure.dpi']
        self.plot_dimension = (1800 * px, 500 * px)

        # Variable plot params
        self.config = config
        self.values = values

    def plot_by_type(self, ax1, ax2):
        plot_type = self.config["plot"]["type"]
        color_list = list(colors)
        elems = []
        for i in range(0, len(self.values)):
            value = self.values[i]
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
                bin_width = self.config["plot"]["histogram"]["bin_width"]
                if x_axis_values is not None:
                    data = x_axis_values
                else:
                    data = y_axis_values

                if bin_width != 0:
                    bins = np.arange(min(data), max(data), bin_width)
                else:
                    bins = None

                plt.hist(data, bins=bins, label=legend, color=color)
                if bins is not None and self.config["x_axis"]["ticks"] is None:
                    self.config["x_axis"]["ticks"] = bins
                yticks = [0, 0.2, 0.4, 0.6, 0.8, 1]
                self.config["y_axis"]["ticks"] = [tick * len(data) for tick in yticks]
                plt.ylim(0, len(data))
                plt.gca().yaxis.set_major_formatter(PercentFormatter(xmax=len(data)))
            else:
                print(f"Error: Invalid plot type, skipping plot with title {self.config['plot']['title']}")
                return -1
        return elems

    # Plot the values based on the x_axis_values and y_axis_values
    def plot(self):
        # Plot size
        plt.figure(figsize=self.plot_dimension)
        ax1 = plt.gca()
        ax2 = None
        if any(value[5] == "right" for value in self.values):
            ax2 = ax1.twinx()

        # Plot the values
        elems = self.plot_by_type(ax1, ax2)
        if elems == -1:
            return -1
        elems = [elem for elem in elems if isinstance(elem, Line2D)]

        # Legend
        legends = [value[4] for value in self.values]
        plt.legend(elems, legends, loc=0)

        # Axis labels and titles
        x_params = self.config["x_axis"]
        y_params = self.config["y_axis"]

        plt.xlabel(x_params["label"], fontsize=self.label_font_size)
        ax1.set_ylabel(y_params["label"], fontsize=self.label_font_size)
        if ax2 is not None:
            ax2.set_ylabel(y_params["label_right"], fontsize=self.label_font_size)
        plt.title(self.config["plot"]["title"], fontsize=self.title_font_size)

        # Axis scale
        if x_params["plot_scale"] == "log":
            plt.xscale("log")
            plt.gca().xaxis.set_major_formatter(ticker.ScalarFormatter())
        if y_params["plot_scale"] == "log":
            plt.yscale("log")
            plt.gca().yaxis.set_major_formatter(ticker.ScalarFormatter())

        # Plot ticks
        plt.xticks(ticks=x_params["ticks"], labels=x_params["tick_labels"], fontsize=self.tick_font_size)
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
        plt.gca().xaxis.offsetText.set_fontsize(self.tick_font_size)

        # Write to file
        os.chdir(root_dir)
        plot_dir = os.path.abspath(os.path.join(self.config["results_file"], os.pardir, "plots",
                                                self.config["output_path"]))
        if not os.path.exists(plot_dir):
            os.makedirs(plot_dir)
        os.chdir(plot_dir)
        plt.savefig(f'{self.config["output_file"]}.png')


class Bokeh:
    def __init__(self, config, values):
        # Hard-coded plot params
        self.title_font_size = 20
        self.label_font_size = 20
        self.tick_font_size = 18  # Also sets the font size of the scientific notation (offset, exponent)
        self.plot_dimension = (900, 480)

        # Variable plot params
        self.config = config
        self.values = values

    def plot_by_type(self, plot):
        plot_type = self.config["plot"]["type"]
        color_list = list(colors)
        for i in range(0, len(self.values)):
            value = self.values[i]
            color = colors[color_list[i % len(color_list)]]
            x_axis_values = value[0]
            x_axis_err = value[1]
            y_axis_values = value[2]
            y_axis_err = value[3]
            legend = value[4]
            position = value[5]

            # Skip the plot if no parameters were found
            if y_axis_values is None or len(y_axis_values) == 0:
                return -1

            if plot_type == "line":
                if x_axis_values is None:
                    x_axis_values = range(len(y_axis_values))

                # Draw line and points
                plot.line(x_axis_values, y_axis_values, legend_label=legend, line_width=2, line_color=color, alpha=0.8,
                          muted_color=color, muted_alpha=0.2, y_range_name=position)
                plot.scatter(x_axis_values, y_axis_values, fill_color=color, size=8, alpha=0.8, legend_label=legend,
                             muted_color=color, muted_alpha=0.2, y_range_name=position)

                # Draw error bars
                upper_x = pd.Series([x + err for x, err in zip(x_axis_values, x_axis_err)], index=x_axis_values)
                lower_x = pd.Series([x - err for x, err in zip(x_axis_values, x_axis_err)], index=x_axis_values)
                upper_y = pd.Series([y + err for y, err in zip(y_axis_values, y_axis_err)], index=x_axis_values)
                lower_y = pd.Series([y - err for y, err in zip(y_axis_values, y_axis_err)], index=x_axis_values)

                source_x = ColumnDataSource(data=dict(base=y_axis_values, upper=upper_x, lower=lower_x))
                source_y = ColumnDataSource(data=dict(base=x_axis_values, upper=upper_y, lower=lower_y))
                if x_axis_err != [0] * len(x_axis_err):
                    plot.add_layout(Whisker(base="base", upper="upper", lower="lower", level='glyph', dimension='width',
                                            source=source_x, line_color='black', y_range_name=position))
                if y_axis_err != [0] * len(y_axis_err):
                    # plot.add_layout(Whisker(base="base", upper="upper", lower="lower", level='glyph',
                    #                        dimension='height', source=source_y, line_color='black'))
                    # Vertical area for 1 std deviation
                    plot.varea(x="base", y1="lower", y2="upper", source=source_y, fill_color=color, fill_alpha=0.15,
                               legend_label=legend, y_range_name=position)

            elif plot_type == "scatter":
                dot_size = 10
                if x_axis_values is not None:
                    plot.scatter(x_axis_values, y_axis_values, legend_label=legend, color=color, size=dot_size,
                                 alpha=0.8, muted_color=color, muted_alpha=0.2, y_range_name=position)
                else:
                    plot.scatter(y_axis_values, legend_label=legend, color=color, size=dot_size, alpha=0.8,
                                 muted_color=color, muted_alpha=0.2, y_range_name=position)
            elif plot_type == "histogram":
                bin_width = self.config["plot"]["histogram"]["bin_width"]
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
                          legend_label=legend, alpha=0.8, muted_color=color, muted_alpha=0.2, y_range_name=position)
                if bins != "auto" and self.config["x_axis"]["ticks"] is None:
                    self.config["x_axis"]["ticks"] = bins
                yticks = [0, 0.2, 0.4, 0.6, 0.8, 1]
                self.config["y_axis"]["ticks"] = yticks
                plot.y_range = Range1d(0, 1)
                plot.yaxis.formatter = NumeralTickFormatter(format="0%")

            else:
                print(f"Error: Invalid plot type, skipping plot with title {self.config['plot']['title']}")
                return -1

    # Plot the values based on the x_axis_values and y_axis_values
    def plot(self):
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
        plot = figure(width=self.plot_dimension[0], height=self.plot_dimension[1], title=self.config["plot"]["title"],
                      toolbar_location="below", toolbar_sticky=False,
                      tools=[pan, wheel_zoom, tap, save, hover, reset], x_axis_type=self.config["x_axis"]["plot_scale"],
                      y_axis_type=self.config["y_axis"]["plot_scale"])

        # Set default active tools
        plot.toolbar.active_drag = pan
        plot.toolbar.active_scroll = wheel_zoom
        plot.toolbar.active_tap = tap

        # Axis labels and titles
        x_params = self.config["x_axis"]
        y_params = self.config["y_axis"]

        plot.xaxis.axis_label = x_params["label"]
        plot.yaxis.axis_label = y_params["label"]
        plot.axis.axis_label_text_font_size = f"{self.label_font_size}pt"
        plot.title.text = self.config["plot"]["title"]
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
        if self.config["plot"]["type"] != "histogram":
            # X-axis
            x_max = max([x + err for value in self.values for x, err, y in
                         zip(value[0], value[1], value[2]) if not np.isnan(x) and not np.isnan(y)], default=10)
            x_max += 0.1 * x_max
            x_min = min([x - err for value in self.values for x, err, y in
                         zip(value[0], value[1], value[2]) if not np.isnan(x) and not np.isnan(y)], default=0)
            x_min -= 0.1 * x_min
            plot.x_range = Range1d(x_min, x_max)

            # Left Y-axis
            y_max = max(
                [y + err for value in self.values if value[5] == "default"
                 for y, err, x in zip(value[2], value[3], value[0]) if not np.isnan(y) and not np.isnan(x)], default=10)
            y_max += 0.1 * y_max
            y_min = min(
                [y - err for value in self.values if value[5] == "default"
                 for y, err, x in zip(value[2], value[3], value[0]) if not np.isnan(y) and not np.isnan(x)], default=0)
            y_min -= 0.1 * y_min
            plot.y_range = Range1d(y_min, y_max)

            # Right Y-axis
            if any(value[5] == "right" for value in self.values):
                y_max = max(
                    [y + err for value in self.values if value[5] == "right" for y, err, x in
                     zip(value[2], value[3], value[0]) if not np.isnan(y) and not np.isnan(x)], default=10)
                y_max += 0.1 * y_max
                y_min = min(
                    [y - err for value in self.values if value[5] == "right" for y, err, x in
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
        retval = self.plot_by_type(plot)
        if retval == -1:
            return -1

        # Legend Location
        plot.legend.click_policy = "hide"  # "hide" or "mute"
        plot.legend.location = "top_left"
        plot.legend.ncols = int(len(plot.legend.items) / 10) + 1
        if plot.legend.ncols > 2:
            plot.add_layout(plot.legend[0], "below")
            plot.height = int(plot.height * 1.5)
        else:
            plot.add_layout(plot.legend[0], "center")

        # Write to file
        os.chdir(root_dir)
        plot_dir = os.path.abspath(os.path.join(self.config["results_file"], os.pardir, "plots",
                                                self.config["output_path"]))
        if not os.path.exists(plot_dir):
            os.makedirs(plot_dir)
        os.chdir(plot_dir)
        html = file_html(plot, CDN, self.config["plot"]["title"])
        with open(f'{self.config["output_file"]}.html', "w") as f:
            f.write(html)


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
def get_param_value(param_path, json_object, index, min_cutoff, max_cutoff):
    split_path = param_path.split(".")
    value = json_object
    try:
        for key in split_path:
            value = value[key]
        if index is not None:
            if isinstance(index, list):
                for i in index:
                    value = value[i]
            elif isinstance(index, int):
                value = value[index]
    except (KeyError, IndexError):
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

        if y_value_param is not None:
            # Legend
            legend = y_value_param["legend"]
            # Position
            position = y_value_param["position"]
            # Values
            y_values = [param_value for result in results if
                        (param_value := get_param_value(y_value_param["param"], result, y_value_param["index"],
                                                        y_value_param["min_cutoff"],
                                                        y_value_param["max_cutoff"])) is not None]
            y_values = np.array(y_values).T
            y_value_param["scale_by"] = get_scale_by_value(y_values, y_value_param["scale_by"])
            y_values = y_values / y_value_param["scale_by"]

            # Pad the values with NaNs if y_values is array of arrays
            if isinstance(y_values, list) and isinstance(y_values[0], list):
                max_length = max(len(y) for y in y_values)
                y_values = np.array([y + [np.nan] * (max_length - len(y)) for y in y_values])
            else:
                max_length = len(y_values)

            # Error values
            if y_value_param["error"] is not None:
                y_err_values = [param_value for result in results if
                                (param_value := get_param_value(y_value_param["error"], result, y_value_param["index"],
                                                                None,
                                                                None)) is not None]
                if y_err_values is not None:
                    y_err_values = np.array(y_err_values).T
                    y_err_values = y_err_values / y_value_param["scale_by"]
            else:
                # Set err_values as 0
                if isinstance(y_values, list) and isinstance(y_values[0], list):
                    y_err_values = [[0 for _ in range(0, max_length)] for _ in range(0, len(y_values))]
                else:
                    y_err_values = [[0 for _ in range(0, max_length)]]
                y_err_values = np.array(y_err_values).T
        else:
            y_values = y_err_values = None

        if x_value_param is not None:
            # Legend
            if legend is None:
                legend = x_value_param["legend"]  # Only set if y_param has not already set it

            # values
            x_values = [param_value for result in results if
                        (param_value := get_param_value(x_value_param["param"], result, x_value_param["index"],
                                                        x_value_param["min_cutoff"],
                                                        x_value_param["max_cutoff"])) is not None]
            x_values = np.array(x_values).T
            x_value_param["scale_by"] = get_scale_by_value(x_values, x_value_param["scale_by"])
            x_values = x_values / x_value_param["scale_by"]

            # Pad the values with NaNs if y_values is array of arrays
            if isinstance(x_values, list) and isinstance(x_values[0], list):
                max_length = max(len(x) for x in x_values)
                x_values = np.array([x + [np.nan] * (max_length - len(x)) for x in x_values])

            # Error values
            if x_value_param["error"] is not None:
                x_err_values = [param_value for result in results if
                                (param_value := get_param_value(x_value_param["error"], result, x_value_param["index"],
                                                                None,
                                                                None)) is not None]
                if x_err_values is not None:
                    x_err_values = np.array(x_err_values).T
                    x_err_values = x_err_values / x_value_param["scale_by"]
            else:
                # Set err_values as 0
                if isinstance(x_values, list) and isinstance(x_values[0], list):
                    x_err_values = [[0 for _ in range(0, max_length)] for _ in range(0, len(y_values))]
                else:
                    x_err_values = [[0 for _ in range(0, max_length)]]
                x_err_values = np.array(x_err_values).T
        else:
            # Generate x_values as index and x_err_values as 0
            if y_values is not None and isinstance(y_values[0], list):
                x_values = [[i for i in range(0, max_length)] for _ in range(0, len(y_values))]
                x_err_values = [[0 for _ in range(0, max_length)] for _ in range(0, len(y_values))]
            else:
                x_values = [i for i in range(0, max_length)]
                x_err_values = [[0 for _ in range(0, max_length)]]

        # Sort the values by X-axis
        if len(x_values) != len(y_values) or len(x_values) != len(x_err_values) or len(x_values) != len(y_err_values):
            warning = (f"Error: Lengths of x_values, x_err_values, y_values, y_err_values do not match!\n" +
                       f"Skipping param {y_value_param['param']} from plot {config['plot']['title']}")
            warnings.warn(warning)
            continue

        if y_values is not None and len(y_values) > 0 and x_values is not None and len(x_values) > 0:
            combined_array = zip(x_values, x_err_values, y_values, y_err_values)
            sorted_array = sorted(combined_array, key=lambda x: x[0])
            x_values, x_err_values, y_values, y_err_values = zip(*sorted_array)
            y_values = [item[0] if isinstance(item, (list, np.ndarray)) else item for item in y_values]
            y_err_values = [item[0] if isinstance(item, (list, np.ndarray)) else item for item in y_err_values]

        # Unpack x_values if necessary
        if x_values is not None:
            x_values = [item[0] if isinstance(item, (list, np.ndarray)) else item for item in x_values]
            x_err_values = [item[0] if isinstance(item, (list, np.ndarray)) else item for item in x_err_values]

        # Set err_values to NoneType if they are all 0s (which we did to allow cleaner code with zip and sorting above)
        # if y_err_values is not None and all([err == 0 for err in y_err_values]):
        #     y_err_values = None
        # if x_err_values is not None and all([err == 0 for err in x_err_values]):
        #     x_err_values = None
        values.append((x_values, x_err_values, y_values, y_err_values, legend, position))

    return values


def parse_arguments():
    # Create ArgumentParser object
    parser = argparse.ArgumentParser(description='Run multiple experiments with different configurations')

    # Add arguments
    parser.add_argument("-c", "--configs", default="plot_config.json",
                        help='The configuration file for the plot')

    # Return the params
    return parser.parse_args()


def check_config(config):
    # Check required parameters
    if ("results_file" not in config or config["results_file"] == '' or config["results_file"] is None
            or not isinstance(config["results_file"], str)):
        raise Exception("Missing required parameter: results_file")
    if not os.path.isabs(config["results_file"]):
        config["results_file"] = os.path.join(root_dir, config["results_file"])
    if "output_path" not in config or config["output_path"] is None or not isinstance(config["output_path"], str):
        config["output_path"] = ''
    if "plot" not in config or config["plot"] is None or not isinstance(config["plot"], dict):
        raise Exception("Missing required parameter: plot")
    if ("x_axis" not in config or "y_axis" not in config or config["x_axis"] is None or config["y_axis"] is None
            or not isinstance(config["x_axis"], dict) or not isinstance(config["y_axis"], dict)):
        raise Exception("Missing required parameter: x_axis or y_axis")

    # Check for plot parameters
    plot_params = config["plot"]
    if ("renderer" not in plot_params or plot_params["renderer"] == '' or plot_params["renderer"] is None
            or not isinstance(plot_params["renderer"], str)):
        plot_params["renderer"] = "bokeh"
    if "type" not in plot_params or plot_params["type"] == '' or plot_params["type"] is None:
        raise Exception("Missing required parameter: plot: type")
    if plot_params["type"] not in ["line", "scatter", "histogram"]:
        raise Exception("Invalid plot type. Must be one of: line, scatter, histogram")
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
            if "index" not in value or value["index"] == '' or not isinstance(value["index"], (int, list)):
                value["index"] = None
            if "error" not in value or value["error"] == '' or not isinstance(value["error"], str):
                value["error"] = None
            if "legend" not in value or not isinstance(value["legend"], str):
                value["legend"] = ""
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
            if "index" not in value or value["index"] == '' or not isinstance(value["index"], (int, list)):
                value["index"] = None
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
    with open(parse_arguments().configs, "r") as f:
        configs = json.load(f)

    for config in configs:
        print(f"\nStarting plot {config['plot']['title']} and results file {config['results_file']}")
        check_config(config)
        # Get the values to plot
        values = get_values(config)
        if values is None:
            continue
        if config["plot"]["renderer"] == "bokeh":
            Bokeh(config, values).plot()
        elif config["plot"]["renderer"] == "matplotlib":
            Matplotlib(config, values).plot()
        else:
            raise Exception("Specified Renderer not supported. Must be either 'bokeh' or 'matplotlib' "
                            f"for config with results file {config['results_file']}")


if __name__ == "__main__":
    # Set the working directory
    root_dir = execute_program(["git", "rev-parse", "--show-superproject-working-tree"])
    if root_dir == "":
        root_dir = execute_program(["git", "rev-parse", "--show-toplevel"])
    root_dir = root_dir.strip('\n')
    main()
