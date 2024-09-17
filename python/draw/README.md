# draw.py

This file helps you draw a block diagram using JSON format.

## Pre-requisites

_Note: The following commands are for Ubuntu (or Debian-based) OS. Please modify it if you have a different OS._

```bash
apt-get update
# Install python and pip
apt-get install \
  python3 \
  python3-pip \
  graphviz
  
# Install the required python packages
pip3 install -r requirements.txt
```

## Usage

This script helps you plot a graph from the `results.json` produced from `run_experiments.py`.
The resultant image (png) is saved in the same path as the input results.json, in a directory called "plots"

The script has the following parameters (and defaults):

```text
-c, --configs: (Optional, default="diagrams.json")The configurations JSON file for plotting
-d, --dir: (Optional, default is the root dir of the master git project) The directory relative to which all other 
           paths will be considered.  
```

## diagram.json

The `diagrams.json` consists of an array of diagrams, where each diagram consists of "nodes" and "edges", 
and a "title" (all required) for that diagram. See the example `diagrams.json` file in this folder for reference.  

### Node
`id`: (Required, can NOT be "root") The ID of this node. Should be unique per diagram.  
`duplicate`: (Optional, default is false) Duplicate the node with `id` as the node here
(new IDs of the form `id + "_dup_" + str(dup_count)`will be assigned to the children, unless `dup_suffix` is set)  
`dup_suffix`: (Optional, default is None) The suffix to add to the duplicate node IDs  
`title`: (Optional, default is None) The parameters related to the title. See below for details.  
`children`: (Optional, default is None) An array (or NoneType) representing the children of this node 
(will be drawn inside this node)  

**title**
`text`: (Optional, default is None) The text string for the title  
`hpos`: (Optional, default is center) The horizontal position of the title (left, center, right)  
`vpos`: (Optional, default if top) The vertical position of the title (top, mid, bottom)  

### Edge
_Note: You can't connect nodes with their own children_
`start`: (Required) The starting edge
`end`: (Required) The ending edge
`text`: (Optional, default is None) The text to place on this edge
`arrow`: (Optional, default is 0) 0 for no arrow, 1 for arrow at end, 2 for arrows on both start and end  
`curved`: (Optional, default is None) Whether to curve the arrow or not, and from where
(None, "start", "end", "both")  

**start** and **end**
`id`: The `id` of the start edge  
`pos`: The position of the end of the arrow 
(in terms of compass directions, i.e. 'n', 's', 'e', 'w' or combinations thereof)  
