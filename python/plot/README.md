# Pre-requisites

_Note: The following commands are for Ubuntu (or Debian-based) OS. Please modify it if you have a different OS._

```bash
apt-get update
# Install python and pip
apt-get install \
  python3 \
  python3-pip
  
# Install the required python packages
pip3 install \
  termcolor \
  bokeh \
  matplotlib
```


# Usage

This script helps you plot a graph from the `results.json` produced from `run_experiments.py`.
The resultant image (png) is saved in the same path as the input results.json, in a directory called "plots"

The script has the following parameters (and defaults):

```text
-c, --configs: (Optional, default="plot_config.json")The configurations JSON file for plotting
```

The `plot_config.json` looks like:

```json
[
  {
    "results_file": "",
    "output_path": "",
    "output_file": "",
    "plot": {
      "title": "",
      "renderer": "bokeh",
      "type": "",
      "histogram": {
        "bin_width": 0.2
      },
      "line": {
      },
      "scatter": {
      }
    },
    "x_axis": {
      "values": [
        {
          "param": "",
          "index": None,
          "error": "",
          "legend": "",
          "scale_by": 1,
          "min_cutoff": 1,
          "max_cutoff": 1
        }
      ],
      "label": "",
      "plot_scale": "",
      "ticks": [],
      "tick_labels": []
    },
    "y_axis": {
      "values": [
        {
          "param": "",
          "index": None,
          "legend": "",
          "position": "left",
          "scale_by": 1,
          "min_cutoff": 1,
          "max_cutoff": 1
        }
      ],
      "label": "",
      "plot_scale": "",
      "ticks": [],
      "tick_labels": []
    }
  }, {
    ...
  }
]
```

where each config parameters are as follows (Note: default will be used if the parameter is invalid):

**Common**  
`results_file`: (Required) The results.json file to use for this config  
_Note: The results file should be an array of jsons, each of which is a result. Even if the file contains one result, it
should be in a JSON array format_  
For example:

```json
[
  {
    "some_values": [1, 2, 3, 4],
    "some_other_values": [1, 2, 3, 4]
  }
]
```

`output_path`: (Optional, default="") The path or directory inside the plots folder where the plot needs to be saved.  
`output_file`: (Optional, default = title of the plot) The file name of the output plot  
`plot`: (Required) Plot specific parameters (See below)

**Plot-specific parameters**
`title`: (Optional, default="{x_label} vs {y_label}") The title for the plot  
`renderer`: (Optional, default="bokeh") The library to use for plotting. Either "bokeh" or "matplotlib"  
`type`: (Required, allowed="line", "scatter", "histogram") The type of plot to be used  
_Note: If `type` is `histogram`, the plot will be generated from the axis where only 1 "values" entry is present._  
`histogram`, `line`, or `scatter`: Parameters specific to the given plot type

**histogram**
`bin_width`: (Optional, default=0) The bin width in a histogram. If 0, plotting library decides bin width on its own

**Per axis**  
`values->param`: (Required on Y-axis, Optional on X-axis, default (on X-axis)=index_of_entry_in_y) The parameter from
the results file to use for the axis  
`values->index`: (Optional, default=None) Index of the array, if param is an array of arrays.  
Can optionally represent an index in multiple nested arrays by specifing an array of index.  
For example: [[[1,2,3], [4,5,6]]] can be represented as [0,1] to get [4,5,6].  
`values->legend`: (Optional, default="") The legend of this param to place in the plot
`values->position`: (Optional, default="left") The location of the Y-axis (left or right).  
`values->scale_by`: (Optional, default=1) Divide all values of that axis by this value. Can be a number or "min",
"max", "count", or "total"  
`values->min_cutoff`: (Optional, default=None) Ignore values less than the specified value (before scaling by
scale_by). Can be a number or a percentile value specified as a string (e.g. "p25")  
`values->max_cutoff`: (Optional, default=None) Ignore values more than the specified value (before scaling by
scale_by). Can be a number or a percentile value specified as a string (e.g. "p25")  
`values->error`: (Optional, default=None) The parameter in the results file corresponding to the error of the given
parameter  
_Note: `error` applies only to plots where it makes sense (line, for now)_

`label`: (Optional, default=param.split(".")[-1]) The label for the axis  
_Note: If param is not specified, label will be "index" on X-axis and "" (null) on Y-axis_
`label_right`: (Optional, default=label) The label for the right Y-axis, if it exists.  
`plot_scale`: (Optional, default="linear", allowed= "linear", "log") The scale for the axis

`ticks`: (Optional, default decided by plotting library) The ticks on the given axis  
`tick_labels`: (Optional, default decided by plotting library) The label on the ticks on the given axis  
`ticks_right`: (Optional, default decided by plotting library) The ticks on the right Y-axis  
`tick_labels_right`: (Optional, default decided by plotting library) The label on the ticks on the right Y-axis  
_Note: `ticks` and `tick_labels` on the Y-axis will not be honoured in histograms_