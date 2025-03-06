import json
import numbers
import os
import re
import warnings

import numpy as np


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
    except (KeyError, IndexError, TypeError):
        warning = "Could not find the parameter at path: " + param_path + ". Skipping specified param..."
        warnings.warn(warning)
        return []
    if isinstance(min_cutoff, str):
        min_cutoff = np.percentile(value, float(min_cutoff[1:]))
    if isinstance(max_cutoff, str):
        max_cutoff = np.percentile(value, float(max_cutoff[1:]))
    if min_cutoff is not None:
        value = [np.nan if elem < min_cutoff else elem for elem in value if isinstance(elem, numbers.Number)]
    if max_cutoff is not None:
        value = [np.nan if elem > max_cutoff else elem for elem in value if isinstance(elem, numbers.Number)]
    if min_cutoff is not None or max_cutoff is not None:
        nan_count = np.sum(np.isnan(value))
        if min_cutoff is not None or max_cutoff is not None:
            print("% of values removed due to cutoffs from path", param_path, "is",
                  nan_count / len(value) * 100, "%")
    return value


# Get the X and Y axis values to plot
def get_values(config, root_dir):
    def get_axis_values(axis_value_param):
        axis_values = get_param_value(axis_value_param["param"], results,
                                      axis_value_param["min_cutoff"],
                                      axis_value_param["max_cutoff"])
        axis_values = np.array(axis_values)
        axis_value_param["scale_by"] = get_scale_by_value(axis_values, axis_value_param["scale_by"])
        if axis_value_param["scale_by"] != 1:
            axis_values = axis_values / axis_value_param["scale_by"]

        # Error values
        if axis_value_param["error"] is not None:
            axis_err_values = get_param_value(axis_value_param["error"], results, None, None)
            if axis_err_values is not None:
                axis_err_values = np.array(axis_err_values)
                if axis_value_param["scale_by"] != 1:
                    axis_err_values = axis_err_values / axis_value_param["scale_by"]
        else:
            # Set err_values as 0
            axis_err_values = np.array([0] * len(axis_values))

        return axis_values, axis_err_values

    os.chdir(root_dir)
    # Read the JSON file
    with open(config["results_file"], "r") as f:
        results = json.load(f)

    # Initialize the parameters
    x_params = config["x_axis"]
    y_params = config["y_axis"]
    values = []  # Consists of tuples of (x_values, x_err_values, y_values, y_err_values, label, y_position)

    # Check X-axis has either 1 value (in which case we duplicate it for all Y) or the same number of values as Y-axis
    if (len(x_params["values"]) != 1
            and y_params["values"] is not None
            and len(x_params["values"]) != len(y_params["values"])):
        warnings.warn("X-axis should have either 1 value or the same number of values as Y-axis!")
        return None

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
                labels = get_param_value(y_value_param["labels"], results, None, None)
            # Values
            y_values, y_err_values = get_axis_values(y_value_param)
        else:
            y_values = y_err_values = None

        if x_value_param is not None:

            # values
            x_values, x_err_values = get_axis_values(x_value_param)
        else:
            # Generate x_values as index and x_err_values as 0
            x_values = np.array([i for i in range(1, len(y_values) + 1)])
            x_err_values = np.array([0] * len(x_values))

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
        if y_values is not None and len(y_values) > 0 and x_values is not None and len(x_values) > 0 \
                and not all(isinstance(elem, str) for elem in x_values):
            combined_array = zip(x_values, x_err_values, y_values, y_err_values, labels)
            sorted_array = sorted(combined_array, key=lambda x: x[0])
            x_values, x_err_values, y_values, y_err_values, labels = zip(*sorted_array)
            x_values = list(x_values)
            x_err_values = list(x_err_values)
            y_values = list(y_values)
            y_err_values = list(y_err_values)
            labels = list(labels)
            if all(elem is None for elem in labels):
                labels = None

        values.append(
            (x_values, x_err_values, y_values, y_err_values, legend, position, y_value_param["visible"], labels,
             y_value_param["color"], y_value_param["marker"]))

    return values
