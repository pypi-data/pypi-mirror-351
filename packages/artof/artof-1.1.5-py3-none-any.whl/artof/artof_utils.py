"""
The artof_utils module provide static utility functions to be used in the artof package.
"""

import os


def get_next_step(it: int, step: int, lens_steps: int):
    """
    Get the next step of a run

    Args:
        it: Current iteration.
        step: Current step.
        lens_steps: Total number of steps per iteration.

    Returns:
        Next iteration and step
    """

    if step == lens_steps - 1:
        return it + 1, 0
    return it, step + 1


def is_last_step(it: int, step: int, stop_iter: int, lens_steps: int):
    """
    Check if the current file is the last file of a run

    Args:
        it: Current iteration.
        step: Current step in iteration.
        lens_steps: Total number of steps.
        stop_iter: Maximum number of iterations.

    Returns:
        Boolean value if the current file is the last file
    """

    return it == stop_iter - 1 and step == lens_steps - 1


def next_file_exists(path: str, it: int, step: int, lens_steps: int):
    """
    Check if the next file of a run exists

    Args:
        path: Path where data files are located.
        it: Current iteration.
        step: Current step.
        lens_steps: Total number of steps.

    Returns:
        Boolean value if the next file exists
    """

    next_step = get_next_step(it, step, lens_steps)
    return os.path.exists(f"{path}/{next_step[0]}_{next_step[1]}")
