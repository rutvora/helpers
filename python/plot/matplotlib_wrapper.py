import os
import warnings

import numpy as np
import progressbar
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
    "golden": "#ffa600",
    "dark_magenta": "#d45087",
    "violet": "#665191",
    "black": "#444444",
}


class Matplotlib:
    def __init__(self, root_dir):
        # Hard-coded plot params
        self.title_font_size = 20
        self.label_font_size = 20
        self.tick_font_size = 18  # Also sets the font size of the scientific notation (offset, exponent)
        self.px = 1 / plt.rcParams['figure.dpi']
        self.plot_dimension = (1800 * self.px, 500 * self.px)
        self.grid_columns = 2
        self.root_dir = root_dir

        # Variable plot params
        self.groups = {}

    def write_to_file(self, plot, config=None, group=None):
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
        os.chdir(self.root_dir)
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
            x_axis_values = value[0]
            x_axis_err = value[1]
            y_axis_values = value[2]
            y_axis_err = value[3]
            legend = value[4]
            position = value[5]
            # visible = value[6]
            # labels = value[7]
            color = value[8]
            color = color if color is not None else colors[color_list[i % len(color_list)]]

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

        x_dim = config["plot"]["dimensions"][0]
        x_dim = x_dim if x_dim is not None else self.plot_dimension[0]
        y_dim = config["plot"]["dimensions"][1]
        y_dim = y_dim if y_dim is not None else self.plot_dimension[1]
        fig, ax = plt.subplots(figsize=(x_dim * self.px, y_dim * self.px))

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
