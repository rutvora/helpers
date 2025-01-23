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
  numpy \
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
      "group": null,
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
          "legend": "",
          "visible": true,
          "position": "left",
          "scale_by": 1,
          "min_cutoff": 1,
          "max_cutoff": 1,
          "labels": none,
          "color": "blue"
        }
      ],
      "label": "",
      "plot_scale": "",
      "ticks": [],
      "tick_labels": []
    }
  }, {
    "another": "config here"
  }
]
```

where each config parameters are as follows (Note: default will be used if the parameter is invalid):

**Common**  
`results_file`: (Required) The results.json file to use for this config  
The path is a string which can be the absolute address (e.g. `/home/USER/PROJ/results/results.json`), or an address
relative to the directory of the main git project. For example, you can set the `results_file` as `results/results.json`
if your project is structured as follows:

```
main_proj_dir
  |
  |__ submodules
  |   |
  |   |__ helpers
  |       |
  |       |__ python (THIS DIRECTORY)
  |
  |__ results
      |
      |__ results.json       
```

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
_Note: `output_path` can't contain ":"_  
`output_file`: (Optional, default = title of the plot) The file name of the output plot  
`plot`: (Required) Plot specific parameters (See below)

**Plot parameters**
`title`: (Optional, default="{x_label} vs {y_label}") The title for the plot  
`renderer`: (Optional, default="bokeh") The library to use for plotting. Either "bokeh" or "matplotlib"  
`type`: (Required, allowed="line", "scatter", "histogram", "heatmap") The type of plot to be used  
_Note: If `type` is `histogram`, the plot will be generated from the X-axis if it exists, else the Y-axis._  
`histogram`, `line`, or `scatter`: Parameters specific to the given plot type
`group`: (Optional, int or string) If you want to group plots into a single HTML or image, specify the group
identifier here  
_Note: `group` can't contain ":"_  
_Note: `output_file` and `output_path` will be ignored in case group is specified. The filename will be the group
identifier_
`notes` (Optional, default=None) Some additional HTML text notes that you want to put in the plot
(only works with Bokeh)  
`dimensions` (Optional, default=[None, None]) The dimensions of the plot. 
If None, the plot will use the hard-coded default values  

**histogram**
`bin_width`: (Optional, default=0) The bin width in a histogram. If 0, plotting library decides bin width on its own

**Per axis**  
`values->param`: (Required on Y-axis, Optional on X-axis, default (on X-axis)=index_of_entry_in_y) The parameter from
the results file to use for the axis  
This can be expressed as any combination of key and index in JSON (e.g. `[0].x[0][1].w`) will extract `[1,2,3,4]` out of
the following result:

```json
[
  {
    "x": [
      [
        {
          "w": [0, 0, 0, 0]
        },
        {
          "w": [1, 2, 3, 4]
        }
      ]
    ]
  }
]
```

`values->legend`: (Optional, default=values->param) The legend of this param to place in the plot.
No two legends in the same plot can have duplicates. If there are duplicates, they will default to the param name.  
`values->visible`: (Optional, default=true) Whether this plot is visible by default (only applicable to Y-axis and in
bokeh). Max 5 legends set to visible by default. You can click on the legend to make more of them visible.  
`values->labels`: (Optional, default=None, only on Y-axis) The labels for these individual plot points.
For heatmaps, this label should be an array of integers, which will be used to make the heatmap.  
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
`values->color`: (Optional, default=None) The color of this element (defaults to some random color from a pre-defined
list)

`label`: (Optional, default=param.split(".")[-1]) The label for the axis  
_Note: If param is not specified, label will be "index" on X-axis and "" (null) on Y-axis_
`label_right`: (Optional, default=label) The label for the right Y-axis, if it exists.  
`plot_scale`: (Optional, default="linear", allowed= "linear", "log") The scale for the axis

`ticks`: (Optional, default decided by plotting library) The ticks on the given axis  
`tick_labels`: (Optional, default decided by plotting library) The label on the ticks on the given axis  
`ticks_right`: (Optional, default decided by plotting library) The ticks on the right Y-axis  
`tick_labels_right`: (Optional, default decided by plotting library) The label on the ticks on the right Y-axis  
_Note: `ticks` and `tick_labels` on the Y-axis will not be honoured in histograms_
