"""Module containing ARTOFLoader class for loading and processing artof data.

The ARTOFLoader class is used to load and process artof data from a specified directory.
"""

import plotly.graph_objects as go
from IPython.display import display

from .base_loader import BaseLoader
from .data_process import get_axis_values, project_data
from .plotting import plot_1d, plot_2d, plot_counts


class ARTOFLoader(BaseLoader):
    """
    Class for loading and processing artof data.
    """

    def __init__(
        self,
        path: str,
        transform_format: str,
        x0: float = None,
        y0: float = None,
        t0: float = None,
        sweep_type: str = "Sienta",
    ):
        """
        Initialize ARTOFLoader class.

        Args:
            path: Path to run directory.
            transform_format: Format to load data in ('raw', 'raw_SI', 'cylindrical', 'spherical').
            x0: Offset for x ticks, optional (default extracted from acquisition.cfg).
            y0: Offset for y ticks, optional (default extracted from acquisition.cfg).
            t0: Offset for t ticks, optional (default extracted from acquisition.cfg).
            sweep_type: Sweep type ('Sienta' or 'normal'), optional (default 'Sienta').
        """
        super().__init__(path, transform_format, x0, y0, t0, sweep_type)
        self.fig = None

    def transform_data(
        self,
        iter_interval: tuple = None,
        wrap_low_energy: bool = False,
        trigger_period: int = None,
        multithreading: bool = True,
    ):
        """
        Load artof data for run in directory and transform into desired format.

        Args:
            iter_interval: Tuple of start (including) and stop (excluding) lens iteration to load
                (default None, load all).
            wrap_low_energy: Wrap low energy values to high energy values (default False). If True,
                the trigger period is read from 'timing.txt' file unless provided as
                `trigger_period`.
            trigger_period: Period between two trigger. When provided time of flight longer than one
                one trigger period can be loaded (default None).
            multithreading: Use multithreading for data loading (default True).
        """
        # reset loader
        self.setup_data_vars()

        if iter_interval:
            self.set_iter_interval(iter_interval[0], iter_interval[1])
        transformed_data = self.load_and_transform(
            multithreading, wrap_low_energy=wrap_low_energy, trigger_period=trigger_period
        )
        self.add_transformed_data(transformed_data)

        self.print_transform_stats()

    def bin_data(
        self, cust_bin_confs=None, norm_modes: list = None, win_config: tuple[int, int] = None
    ):
        """
        Bin loaded data into 3D histogram.

        Args:
            cust_bin_confs: List of 3 custom binning configurations for the 3 parameters
                [min, max, points]. F.e.: [[-1500, 1500, 101], [-1500, 1500, 101],
                [12000, 18000, 201]]
            norm_modes: Normalization mode for binned data ('iterations', 'dwell_time', 'sweep').
                Default is None.
                - `iterations`: Normalize data by number of iterations.
                - `dwell_time`: Normalize data by dwell time.
                - `sweep`: Normalize data by changing window size of sweep data.
            win_config: Tuple of window size and step size for sweep data (default None, one window)
                If the last window is smaller than the step size, it will be ignored.


        Raises:
            Exception: If data is not loaded before binning.
        """
        # reset binned data from previous binning # pyright: disable=attribute-defined-outside-init
        self.binned_data = {}

        # set binning configurations
        self.set_bin_configs(cust_bin_confs)

        binned_data = self.bin(self.transformed_data, norm_modes, win_config=win_config)
        self.add_binned_data(binned_data)

        # print windows if win_config is given
        if win_config is not None:
            print(
                f"The following {len(self.binned_data)} window(s) were"
                f" created: {list(self.binned_data.keys())}"
            )

    def plot(
        self,
        proj_axes: list,
        ranges=None,
        norm_step_size: bool = False,
        photon_energy: float = None,
        width: int = 600,
        height: int = 600,
    ):
        """
        Plot loaded data as projection onto given axes. Projections are possible onto 1 or 2 axes.

        Args:
            proj_axes: List containing all axes onto which the projection is performed, e.g., [0,1].
            ranges: List containing ranges for axes (e.g., [[50, 101], [0,50], None]), if None
                entire range of axes is used (default entire range of each axis).
            norm_step_size: Normalize data with step size before plotting (default False).
            photon_energy: Photon energy to plot in binding energy, optional (default None).
            width: Width of plot (default 600).
            height: Height of plot (default 600).

        Raises:
            ValueError: An incorrect number of projection axes provided.
        """

        if self.bin_edges is None:
            raise RuntimeError("Data not binned. Please bin data before plotting.")

        if len(proj_axes) not in [1, 2]:
            raise ValueError(f"A projection along {len(proj_axes)} axes is not possible.")

        if ranges is None:
            ranges = [None, None, None]

        # concatenate all binned data into one array TODO show spectral evolution in plot
        # data = np.sum(list(self.binned_data.values()), axis=0)

        proj_data_wins = {}
        for win_id, data in self.binned_data.items():
            proj_data_wins[win_id] = project_data(
                data, self.bin_edges, proj_axes, ranges, norm_step_size
            )

        self.fig = go.Figure(layout=go.Layout(width=width, height=height))

        fig_title = (
            f"Projection onto {' & '.join([self.axes[i].split('_')[0] for i in proj_axes])} in"
            f" {self.transform_format}-format"
        )
        if len(proj_axes) == 2:  # plot data in 2D as heatmap
            plot_2d(
                self.fig,
                proj_data_wins,
                self.bin_edges[proj_axes[0]],
                self.bin_edges[proj_axes[1]],
                self.axes,
                proj_axes,
                photon_energy,
                height,
                title=fig_title,
            )
        elif len(proj_axes) == 1:  # plot data in 1D as line
            x_data = get_axis_values(self.bin_edges, self.axes, photon_energy)[proj_axes[0]]
            plot_1d(
                self.fig,
                x_data,
                proj_data_wins,
                self.axes,
                proj_axes,
                photon_energy,
                height,
                title=fig_title,
            )

        self.fig.show()

    def load_counts(
        self, sum_iters: bool = False, start_step: tuple = None, stop_step: tuple = None
    ):
        """
        Load counts of all measured events.

        Args:
            sum_iters: Sum counts of each iteration, instead of returning counts for each step. Only
                relevant for sweeps. (default False)
            start_step: Start step of the lens iteration (iter, step) (including)
                (default None, start from first step)
            stop_step: Stop step of the lens iteration (iter, step) (excluding)
                (default None, stop at last step)

        """
        # if mode 'fix', set sum_iters to True
        if self.acquisition_mode == "fix":
            sum_iters = True

        # save sum iters for plotting
        self.sum_iters = sum_iters

        # reset counts from previous loading
        self.setup_counts_vars()
        self.add_event_counts(
            self.count_events(sum_iters=sum_iters, start_step=start_step, stop_step=stop_step)
        )

    def plot_counts(self, iter_range: list = None, width: int = 600, height: int = 600):
        """
        Plot counts of all measured events over iterations in given range.

        Args:
            range: Range of iterations to plot (def+ault None, plot all).
            width: Width of plot (default 600).
            height: Height of plot (default 600).
        """

        iterations, counts = self.get_event_counts(iter_range)

        # create plot
        self.fig = go.FigureWidget(layout=go.Layout(width=width, height=height))
        display(self.fig)

        plot_counts(self.fig, iterations, counts, self.sum_iters)
