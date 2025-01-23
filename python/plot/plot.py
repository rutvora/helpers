import argparse
import json
import numbers
import os
import subprocess
import warnings

import progressbar
from bokeh.models import AdaptiveTicker

from bokeh_wrapper import Bokeh
from data_preprocessor import get_values
from matplotlib_wrapper import Matplotlib

MAX_VISIBLE = 5


def execute_program(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while executing the command: {e}")
        print(e.output)
        return e.output


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
    def check_results_file():
        if ("results_file" not in config or config["results_file"] == '' or config["results_file"] is None
                or not isinstance(config["results_file"], str)):
            warnings.warn("Missing required parameter: results_file")
            return -1
        if not os.path.isabs(config["results_file"]):
            config["results_file"] = os.path.join(root_dir, config["results_file"])
        if not os.path.exists(config["results_file"]):
            warnings.warn("results_file does not exist")
            return -1

    def check_output_path():
        if "output_path" not in config or config["output_path"] is None or not isinstance(config["output_path"], str):
            config["output_path"] = ''
        else:
            if ':' in (config["output_path"]):
                warnings.warn(": (colon) is not allowed in output path. Replacing it with _")
                config["output_path"] = config["output_path"].replace(":", "_")

    def check_plot_params():
        if "plot" not in config or config["plot"] is None or not isinstance(config["plot"], dict):
            warnings.warn("Missing parameter: plot")
            return -1
        if "dimensions" not in config["plot"] or len(config["plot"]["dimensions"]) != 2:
            config["plot"]["dimensions"] = [None, None]
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
            warnings.warn("Missing required parameter: plot: type")
            return -1
        if plot_params["type"] not in ["line", "scatter", "histogram", "heatmap"]:
            warnings.warn("Invalid plot type. Must be one of: line, scatter, histogram or heatmap")
            return -1
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

    def check_axis(axis):
        if "values" in axis:
            items_to_delete = []
            for value in axis["values"]:
                if ("param" not in value or value["param"] == '' or value["param"] is None
                        or not isinstance(value["param"], str)):
                    items_to_delete.append(value)
            axis["values"] = [value for value in axis["values"] if value not in items_to_delete]
        else:
            axis["values"] = []
        if len(axis["values"]) > 0:
            # Hashmap to avoid duplicate legends
            legend_map = {}

            # Set max MAX_VISIBLE to visible by default
            visible_count = 0
            for value in axis["values"]:
                if "error" not in value or value["error"] == '' or not isinstance(value["error"], str):
                    value["error"] = None
                if "legend" not in value or not isinstance(value["legend"], str) or value["legend"] in legend_map:
                    value["legend"] = value["param"]
                    if value["legend"] in legend_map:
                        legend_map[value["legend"]] += 1
                        value["legend"] = value["legend"] + "_" + str(legend_map[value["legend"]])
                    else:
                        legend_map[value["legend"]] = 1
                else:
                    legend_map[value["legend"]] = 1
                if "color" not in value or not isinstance(value["color"], str):
                    value["color"] = None
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
                # The below parameters are only useful for Y-axis and are ignored (unused) in the X-axis
                if "visible" not in value or not isinstance(value["visible"], bool):
                    value["visible"] = True
                    visible_count += 1
                else:
                    visible_count += 1
                if visible_count > MAX_VISIBLE:
                    value["visible"] = False
                    visible_count -= 1
                if ("position" not in value or value["position"] == '' or value["position"] == 'left'
                        or not isinstance(value["position"], str)):
                    value["position"] = "default"
                if value["position"] != "default" and value["position"] != "right":
                    warnings.warn("Y-axis position is neither 'default' nor 'right'. Defaulting to 'default' (left)")
                    value["position"] = "default"
                # These are individual element labels to be put inside a heatmap.
                # They are unused in the other plot types
                if "labels" not in value or not isinstance(value["labels"], (str, list)):
                    value["labels"] = None

        # Check for optional parameters
        if "label" not in axis or axis["label"] is None or not isinstance(axis["label"], str):
            axis["label"] = "Undefined"
        if ("label_right" not in axis or axis["label_right"] == '' or axis["label_right"] is None
                or not isinstance(axis["label_right"], str)):
            axis["label_right"] = axis["label"]
        if ("plot_scale" not in axis or axis["plot_scale"] == '' or axis["plot_scale"] is None
                or not isinstance(axis["plot_scale"], str)):
            axis["plot_scale"] = "linear"
        if "ticks" not in axis or len(axis["ticks"]) == 0 or not isinstance(axis["ticks"], list):
            axis["ticks"] = None
        if ("tick_labels" not in axis or len(axis["tick_labels"]) == 0 or axis["ticks"] is None
                or not isinstance(axis["tick_labels"], list)):
            axis["tick_labels"] = None
        if axis["ticks"] is not None and axis["tick_labels"] is not None:
            if len(axis["ticks"]) != len(axis["tick_labels"]):
                warnings.warn(
                    "The number of y_ticks and y_tick_labels must be the same on Y-axis."
                    "Faulty config with results file "
                    f"{config['results_file']}, ignoring the tick labels")
                temp = {}
                for idx in range(0, len(axis["ticks"])):
                    temp[axis["ticks"][idx]] = axis["tick_labels"][idx]
                if config["plot"]["renderer"] == "bokeh":
                    axis["tick_labels"] = temp

        # The below ones are ignores for X-axis
        if ("ticks_right" not in axis or len(axis["ticks_right"]) == 0
                or not isinstance(axis["ticks_right"], list)):
            axis["ticks_right"] = None
        if ("tick_labels_right" not in axis or len(axis["tick_labels_right"]) == 0
                or axis["ticks_right"] is None or not isinstance(axis["tick_labels_right"], list)):
            axis["tick_labels_right"] = None

        if axis["ticks_right"] is not None and axis["tick_labels_right"] is not None:
            if len(axis["ticks_right"]) != len(axis["tick_labels_right"]):
                warnings.warn(
                    f"The number of y_ticks and y_tick_labels must be the same on the right Y-axis."
                    f"Faulty config with results file {config['results_file']}. Ignoring the right-side tick labels")
                temp = {}
                for idx in range(0, len(axis["ticks_right"])):
                    temp[axis["ticks_right"][idx]] = axis["tick_labels_right"][idx]
                if config["plot"]["renderer"] == "bokeh":
                    axis["tick_labels"] = temp
        else:
            # Only necessary for right Y-axis due to how it is instantiated
            if config["plot"]["renderer"] == "bokeh":
                axis["ticks_right"] = AdaptiveTicker()
                axis["tick_labels_right"] = {}

    if check_results_file() == -1:
        return -1
    check_output_path()
    plot_params = config["plot"]
    if check_plot_params() == -1:
        return -1

    if ("x_axis" not in config or "y_axis" not in config or config["x_axis"] is None or config["y_axis"] is None
            or not isinstance(config["x_axis"], dict) or not isinstance(config["y_axis"], dict)):
        warnings.warn("Missing required parameter: x_axis or y_axis")
        return -1

    x_params = config["x_axis"]
    y_params = config["y_axis"]

    check_axis(x_params)
    check_axis(y_params)

    if len(x_params["values"]) == 0 and len(y_params["values"]) == 0:
        warnings.warn("No valid X or Y axis to plot")
        return -1

    # Check for Y-axis parameters
    # Check of required parameters
    if config["plot"]["type"] == "histogram":
        if len(x_params["values"]) > 0:
            y_params["values"] = x_params["values"]
        else:
            x_params["values"] = y_params["values"]
    else:
        if len(x_params["values"]) != len(y_params["values"]):
            if len(x_params["values"]) == 1:
                warnings.warn("The number of values in X-axis and Y-axis must be the same."
                              "Duplicating X-axis values for all Y-axis values")
                for i in range(0, len(y_params["values"]) - 1):
                    x_params["values"].append(x_params["values"][0])
            else:
                warnings.warn("X-axis has more than 1 value, but less than the number of values in Y-axis.")
                return -1

    if ("title" not in plot_params or plot_params["title"] == '' or plot_params["title"] is None
            or not isinstance(plot_params["title"], str)):
        plot_params["title"] = f'{x_params["label"]} vs {y_params["label"]}'

    if ("output_file" not in config or config["output_file"] == '' or config["output_file"] is None
            or not isinstance(config["output_file"], str)):
        config["output_file"] = plot_params["title"].replace(" ", "_")


def main():
    global root_dir

    args = parse_arguments()
    if args.dir is not None:
        global root_dir
        root_dir = args.dir
    with open(args.configs, "r") as f:
        configs = json.load(f)

    bkh = Bokeh(root_dir)
    mpl = Matplotlib(root_dir)

    progress_bar = progressbar.ProgressBar(max_value=len(configs), redirect_stdout=True, redirect_stderr=True)

    for idx, config in enumerate(configs):
        print(f"\nStarting plot {config['plot']['title']} and results file {config['results_file']}")
        if check_config(config) == -1:
            warnings.warn("Skipping plot...")
            continue
        # Get the values to plot
        values = get_values(config, root_dir)
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
