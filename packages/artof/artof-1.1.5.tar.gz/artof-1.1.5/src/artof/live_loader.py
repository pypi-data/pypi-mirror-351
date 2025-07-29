"""
Module for the LiveLoader class, which is used for live plotting of ARTOF data.
"""

import os
import time

import numpy as np
import plotly.graph_objects as go
from IPython.display import display

from artof.artof_utils import get_next_step, next_file_exists
from artof.base_loader import BaseLoader
from artof.data_process import get_axis_values, project_data
from artof.plotting import plot_1d, plot_2d, plot_counts, update_subtitle


class LiveLoader(BaseLoader):
    """
    Class for loading and processing artof data in real-time.
    Inherits from the BaseLoader class.
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

    def live_plot(
        self,
        proj_axes: list,
        cust_bin_confs: list = None,
        norm_modes: list = None,
        ranges: list = None,
        norm_step_size: bool = False,
        photon_energy: float = None,
        last_n_it: int = None,
        wrap_low_energy: bool = False,
        trigger_period: int = None,
        width: int = 600,
        height: int = 600,
        multithreading=True,
        timeout: float = 30,
    ) -> None:
        """
        Live plot artof data in real-time.

        Args:
            proj_axes: List containing all axes onto which the projection is performed, e.g., [0,1].
            cust_bin_confs: List of 3 custom binning configurations for the 3 parameters
              [min, max, points], optional. F.e.: [[-1500, 1500, 101], [-1500, 1500, 101],
              [12000, 18000, 201]]
            norm_modes: Normalization mode for binned data ('iterations', 'dwell_time', 'sweep').
                Default is None.
                `iterations`: Normalize data by number of iterations.
                `dwell_time`: Normalize data by dwell time.
                `sweep`: Normalize data by changing window size of sweep data.
            ranges: List containing ranges for axes (e.g., [[50, 101], [0,50], None]), if None
                entire range of axes is used (default entire range of each axis).
            norm_step_size: Normalize data with step size before plotting (default False).
            photon_energy: Photon energy to plot in binding energy, optional (default None).
            last_n_it: Show last n iterations (default None, show all).
            wrap_low_energy: Wrap low energy values to high energy values (default False). If True,
             the trigger period is read from 'timing.txt' file unless provided as `trigger_period`.
            trigger_period: Period between two trigger. When provided time of flight longer than one
             one trigger period can be loaded (default None).
            width: Width of plot (default 600).
            height: Height of plot (default 600).
            multithreading: Use multithreading for data loading (default False).
            timeout: Time in seconds to wait for file to be available (default)

        """
        # reset data
        self.setup_data_vars()

        # set default values if neccessary
        if cust_bin_confs is None:
            cust_bin_confs = [None, None, None]
        if ranges is None:
            ranges = [None, None, None]

        # create empty figure first
        self.fig = go.FigureWidget(layout=go.Layout(width=width, height=height))
        display(self.fig)

        self.set_bin_configs(cust_bin_confs)
        proj_data = self.__setup_plot(proj_axes, photon_energy, height)
        self.__load_and_plot(
            proj_axes,
            proj_data,
            norm_modes,
            ranges,
            norm_step_size,
            last_n_it,
            wrap_low_energy,
            trigger_period,
            multithreading,
            timeout,
        )
        self.print_transform_stats()

    def __setup_plot(self, proj_axes: list, photon_energy: float, height: int) -> list:
        """
        Setup plots for live plotting.

        Args:
            proj_axes: List containing all axes onto which the projection is performed, e.g., [0,1].
            photon_energy: Photon energy to plot in binding energy, optional (default None).
            height: Height of plot.
        """

        fig_title = (
            f"Projection onto {' & '.join([self.axes[i].split('_')[0] for i in proj_axes])} in"
            f" {self.transform_format}-format"
        )
        if len(proj_axes) == 2:  # plot data in 2D as image
            proj_data = np.zeros(
                (
                    len(self.bin_edges[proj_axes[1]]) - 1,
                    len(self.bin_edges[proj_axes[0]]) - 1,
                )
            )
            plot_2d(
                self.fig,
                {"-": proj_data},
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
            proj_data = np.zeros(len(x_data))
            plot_1d(
                self.fig,
                x_data,
                {"-": proj_data},
                self.axes,
                proj_axes,
                photon_energy,
                height,
                title=fig_title,
            )
        else:
            raise ValueError("Projection axes must be 1 or 2.")

        return proj_data

    def __load_and_plot(
        self,
        proj_axes: list,
        proj_data: list,
        norm_modes: list,
        ranges: list,
        norm_step_size: bool,
        last_n_it: int,
        wrap_low_energy: bool,
        trigger_period: int,
        multithreading: bool,
        timeout: float,
    ) -> None:
        """
        Load and plot data in real-time.

        Args:
            proj_axes: List containing all axes onto which the projection is performed, e.g., [0,1].
            proj_data: Data object.
            norm_modes: Normalization mode for binned data ('iterations', 'dwell_time', 'sweep').
            ranges: List containing ranges for axes.
            norm_step_size: Normalize data with step size before plotting.
            last_n_it: Show last n iterations.
            wrap_low_energy: Wrap low energy values to high energy values. If True,
             the trigger period is read from 'timing.txt' file unless provided as `trigger_period`.
            trigger_period: Period between two trigger. When provided time of flight longer than one
             one trigger period can be loaded .
            multithreading: Use multithreading for data loading.
            timeout: Time in seconds to wait for file to be available.

        """
        try:
            next_unloaded_step = (self.start_iter, 0)

            it = self.start_iter
            step = 0
            while next_unloaded_step != (self.stop_iter, 0):
                it, step = self.__get_next_unavail_step(it, step, timeout)

                # transform data
                transformed_data = self.load_and_transform(
                    multithreading,
                    start_step=next_unloaded_step,
                    stop_step=(it, step),
                    trigger_period=trigger_period,
                    wrap_low_energy=wrap_low_energy,
                )
                self.add_transformed_data(transformed_data)

                # bin data ad project data onto axes
                if last_n_it is None:  # show all data if last_n_it is None
                    binned_data_dict = self.bin(
                        transformed_data,
                        norm_modes,
                        cust_start_iter=next_unloaded_step[0],
                        cust_stop_iter=it + 1,
                    )
                    self.add_binned_data(binned_data_dict)
                    binned_data = list(binned_data_dict.values())[0]
                    proj_data += project_data(
                        binned_data, self.bin_edges, proj_axes, ranges, norm_step_size
                    )
                else:
                    last_it = it
                    cur_first_it = max(0, last_it - last_n_it)  # first iteration of current plot
                    # combine all previously loaded iterations not part of current plot
                    self.__combine_binned_data(cur_first_it)
                    # load all iterations that are not in current plot in one go
                    if cur_first_it > next_unloaded_step[0]:
                        binned_data_dict = self.bin(
                            transformed_data,
                            norm_modes,
                            cust_start_iter=next_unloaded_step[0],
                            cust_stop_iter=cur_first_it,
                        )
                        self.add_binned_data(binned_data_dict)
                    # load iterations of current plot with window size 1
                    binned_data_dict = self.bin(
                        transformed_data,
                        norm_modes,
                        win_config=(1, 1),
                        cust_start_iter=cur_first_it,
                        cust_stop_iter=last_it,
                    )
                    self.add_binned_data(binned_data_dict)

                    # get last n iterations and project data onto axes
                    binned_data_values = [
                        self.binned_data[f"{it}-{it}"]
                        for it in range(cur_first_it, last_it)
                        if f"{it}-{it}" in self.binned_data
                    ]
                    binned_data = np.sum(binned_data_values, axis=0)
                    proj_data = project_data(
                        binned_data, self.bin_edges, proj_axes, ranges, norm_step_size
                    )

                # update plot
                if len(proj_axes) == 2:
                    self.fig.data[0].z = proj_data
                elif len(proj_axes) == 1:
                    self.fig.data[0].y = proj_data
                # update subtitle with current frames, if last_n_it is enable
                if last_n_it is not None:
                    update_subtitle(self.fig, f"Iterations {cur_first_it}-{last_it-1}")

                # update steps to load
                next_unloaded_step = (it, step)
        except KeyboardInterrupt:
            print()
            print("Stopping live plotting.")
            if multithreading:
                for thread in self.threads:
                    thread.join()

        # join all iterations
        if last_n_it is not None:
            self.__combine_binned_data(self.stop_iter)

    def live_plot_counts(
        self, sum_iters: bool = False, width: int = 600, height: int = 600, timeout: float = 30
    ) -> None:
        """
        Live plot counts of all measured events.

        Args:
            sum_iters: Sum counts of each iteration, instead of returning counts for each step. Only
                relevant for sweeps. (default False)
            width: Width of plot (default 600).
            height: Height of plot (default 600).
            timeout: Time in seconds to wait for file to be available (default 30).
        """
        # reset data
        self.setup_counts_vars()

        # if mode 'fix', set sum_iters to True
        if self.acquisition_mode == "fix":
            sum_iters = True

        # create empty figure first
        self.fig = go.FigureWidget(layout=go.Layout(width=width, height=height))
        display(self.fig)
        # setup plot with empty data
        plot_counts(self.fig, [], [], sum_iters)
        # load and plot counts
        self.__load_and_plot_counts(sum_iters, timeout)

    def __load_and_plot_counts(self, sum_iters: bool, timeout: int) -> None:
        """
        Load and plot counts of all measured events.

        Args:
            sum_iters: Sum counts of each iteration, instead of returning counts for each step.
            timeout: Time in seconds to wait for file to be available.
        """

        try:
            next_unloaded_step = (self.start_iter, 0)

            it = self.start_iter
            step = 0
            while next_unloaded_step != (self.stop_iter, 0):
                it, step = self.__get_next_unavail_step(it, step, timeout)

                # load counts
                event_counts = self.count_events(
                    sum_iters=sum_iters, start_step=next_unloaded_step, stop_step=(it, step)
                )
                self.add_event_counts(event_counts)

                # update plot
                counts = list(self.event_counts.values())
                iterations = list(self.event_counts.keys())
                self.fig.data[0].x = iterations
                self.fig.data[0].y = counts

                # update steps to load
                next_unloaded_step = (it, step)
        except KeyboardInterrupt:
            print()
            print("Stopping live count plotting.")

    def __get_next_unavail_step(self, it, step, timeout: float) -> tuple:
        """
        Get last available step.

        Returns:
            Tuple containing iteration and step.
        """
        # wait for at least one file to become available
        time_waited = 0
        while not os.path.exists(f"{self.path}/{it}_{step}"):
            if next_file_exists(self.path, it, step, self.lens_steps):
                break
            time.sleep(0.5)
            time_waited += 0.5
            if time_waited >= timeout:
                raise TimeoutError(
                    f"File {self.path}/{it}_{step} not available after {timeout} seconds."
                )
        it, step = get_next_step(it, step, self.lens_steps)

        # add additional steps to load
        while os.path.exists(f"{self.path}/{it}_{step}") and (it, step) != (
            self.stop_iter,
            0,
        ):
            it, step = get_next_step(it, step, self.lens_steps)

        return it, step

    def __combine_binned_data(self, stop_it: int) -> None:
        """
        Combine binned data of all iterations up to stop_it.

        Args:
            stop_it: Stop iteration (exclusive) to combine data.
        """

        binned_data_to_combine = []
        keys_to_remove = [key for key in self.binned_data if int(key.split("-")[0]) < stop_it]
        for key in keys_to_remove:
            it = int(key.split("-")[0])
            if it < stop_it:
                data = self.binned_data.pop(key)
                binned_data_to_combine.append(data)

        if len(binned_data_to_combine) > 0:
            win_id = f"{self.start_iter}-{self.stop_iter-1}"
            self.binned_data[win_id] = np.sum(binned_data_to_combine, axis=0)
