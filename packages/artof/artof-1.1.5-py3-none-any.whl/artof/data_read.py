"""
Module containing functions to read metadata and raw data from measurement directory.
"""

import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, TypeVar

import numpy as np
import pandas as pd

T = TypeVar("T", bound="dataclass")

DATETIME_FORMAT_ACQ = "%Y-%m-%d, %H:%M:%S"
DATETIME_FORMAT_TIMING = "%m/%d/%y %H:%M:%S"


# pylint: disable=invalid-name,too-many-instance-attributes
@dataclass
class General:
    """
    Dataclass for general metadata.
    """

    version: str = ""
    acquisitionStarted: datetime = datetime(1, 1, 1, 0, 0, 0)
    spectrumBeginEnergy: float = 0.0
    spectrumEndEnergy: float = 0.0
    spectrumChannelWidthEnergy: float = 0.0
    lensLowEdgeEnergyStep: float = 0.0
    lensDwellType: str = ""
    lensDwellTime: int = 0
    lensIterations: int = 0
    lensSteps: int = 0
    userSpectrumEndEnergy: float = 0.0
    userLensLowEdgeEnergyStep: float = 0.0
    acquisitionMode: str = ""
    centerEnergy: float = 0.0
    xytFormat: str = ""
    conversionLibraryName: str = ""
    conversionLibraryVersion: str = ""


@dataclass
class Lensmode:
    """
    Dataclass for lensmode metadata.
    """

    lensK: float = 0.0
    vectorSize: int = 0
    maxTheta: float = 0.0
    eKinRef: int = 0
    tofVector: np.ndarray = field(default_factory=lambda: np.array([], dtype=float))  # 1D
    radiusVector: np.ndarray = field(default_factory=lambda: np.array([], dtype=float))  # 1D
    energyMatrix: np.ndarray = field(default_factory=lambda: np.array([], dtype=float))  # 2D
    thetaMatrix: np.ndarray = field(default_factory=lambda: np.array([], dtype=float))  # 2D


def empty_float_array() -> np.ndarray:
    """
    Create empty float array.

    Returns:
        Empty float array.
    """
    return np.array([], dtype=float)


@dataclass
class Detector:
    """
    Dataclass for detector metadata.
    """

    transformVectorSize: int = 0
    transformMaxY: int = 0
    transformXRef: int = 0
    transformXVector: np.ndarray = field(default_factory=empty_float_array)  # 1D
    transformYVector: np.ndarray = field(default_factory=empty_float_array)  # 1D
    transformXMatrix: np.ndarray = field(default_factory=empty_float_array)  # 2D
    transformYMatrix: np.ndarray = field(default_factory=empty_float_array)  # 2D
    x0: int = 0
    y0: int = 0
    t0: int = 0
    t0Tolerance: int = 0
    tdcResolution: float = 0.0
    spatialResolution: int = 0
    spatialDiameter: int = 0
    xDelayTimeMin: int = 0
    xDelayTimeMax: int = 0
    yDelayTimeMin: int = 0
    yDelayTimeMax: int = 0
    zDelayTimeMin: int = 0
    zDelayTimeMax: int = 0


@dataclass
class Analyzer:
    """
    Dataclass for analyzer metadata.
    """

    elementSet: str = ""
    lensMode: str = ""
    passEnergy: int = 0


@dataclass
class Metadata:
    """
    Metadata class containing all metadata for current measurement.
    """

    general: General = field(default_factory=General)
    lensmode: Lensmode = field(default_factory=Lensmode)
    detector: Detector = field(default_factory=Detector)
    analyzer: Analyzer = field(default_factory=Analyzer)


@dataclass
class TimingData:
    """
    Dataclass for timing data.
    """

    timestamp: datetime = datetime(1, 1, 1, 0, 0, 0)
    MasterPeriod: float = 0.0
    PulsePeriodEstimate: int = 0
    TriggerPeriod: float = 0.0


@dataclass
class Timing:
    """
    Dataclass for timing metadata.
    """

    start: TimingData = field(default_factory=TimingData)
    finish: TimingData = field(default_factory=TimingData)


# pylint: enable=invalid-name,too-many-instance-attributes


def read_acquisition_cfg(path: str) -> Metadata:
    """
    Read metadata for given run from acquisition.cfg file.

    Args:
        path: Path to run directory.

    Returns:
        Metadata object containing all info from acquisition.cfg file.
    """

    return read_metadata(f"{path}/acquisition.cfg", Metadata, DATETIME_FORMAT_ACQ)


def read_timing(path: str) -> Timing:
    """
    Read timing metadata for given run from timing.txt file.

    Args:
        path: Path to run directory.

    Returns:
        Timing object containing all info from timing.txt file.
    """

    return read_metadata(f"{path}/timing.txt", Timing, DATETIME_FORMAT_TIMING)


def read_metadata(file: str, metadata_object: Callable[[], T], datetime_format: str) -> T:
    """
    Read any metadata from a given file and return it as a dataclass object. Unknown sections or
    attributes will be skipped with a warning.

    Args:
        file: Path to metadata file.
        metadata_object: Callable that returns an empty instance of the metadata dataclass.
        datetime_format: Format for datetime parsing.

    Returns:
        An instance of the metadata dataclass containing metadata from the file.
    """

    metadata = metadata_object()

    with open(file, encoding="utf-8") as f:
        cur_section = None
        while line := f.readline():
            # strip line of linebreaks
            line = line.rstrip()
            # skip empty lines
            if not line:
                continue
            # set current section
            if line.startswith("["):
                cur_section = line[1:-1]
                try:
                    cur_dataclass = getattr(metadata, cur_section)
                except AttributeError:
                    print(f"Unknown section {cur_section} in {file}. Skipping it.")
                    cur_dataclass = None
                    continue
            else:
                if cur_dataclass is None:
                    continue
                # retrieve parameter name and value
                par_name, value = line.split("=")
                # set attribute in current dataclass
                try:
                    setattr(
                        cur_dataclass,
                        par_name,
                        parse_type(cur_dataclass, par_name, value, datetime_format),
                    )
                except AttributeError:
                    print(f"Attribute {par_name} not found in {cur_section}. Skipping it.")
                    continue

        return metadata


def parse_type(dclass: "dataclass", par_name: str, value: any, datetime_format: str) -> any:
    """
    Parse string read from file to given type. Possible non-trivial conversions are int, float,
    datetime, list.

    Args:
        dclass: Dataclass containing the given parameter.
        par_name: Name of parameter.
        value: Value to be set for parameter.
        datetime_format: Format for datetime parsing.

    Returns:
        Parsed parameter.
    """
    data_type = type(getattr(dclass, par_name)).__name__
    match data_type:
        case "str":
            return value
        case "int":
            return int(value)
        case "float":
            return float(value)
        case "datetime":
            return datetime.strptime(value, datetime_format)
        case "ndarray":
            data = np.array(list(map(float, value.strip("[]").split(" "))))
            # reorganize theta and energy matrices from 1D list to 2D list
            if par_name in ["energyMatrix", "thetaMatrix"]:
                data = np.reshape(data, (-1, dclass.vectorSize))
            # reorganize transformation matrices from 1D list to 2D list
            elif par_name in ["transformXMatrix", "transformYMatrix"]:
                data = np.reshape(data, (-1, dclass.transformVectorSize))
            return data
        case _:
            print(f"Did not find data type {data_type} for {par_name}, saving it as string.")
            return value


def get_metadata_df(metadata: Metadata, pars: list, run_name: str = None) -> pd.DataFrame:
    """
    Get selected keys from metadata as pandas DataFrame.

    Args:
        metadata: Metadata object containing all metadata.
        pars: List of keys to be extracted from metadata (when 'None' all metadata will be returned)
        run_name: Name of current run to be displayed in first column, optional.

    Returns:
        DataFrame containing all requested metadata.
    """
    # create dict from metadata object (and for all its sub-objects (2 levels))
    metadata_dict = metadata.__dict__.copy()
    for key in metadata_dict.keys():
        metadata_dict[key] = metadata_dict[key].__dict__

    # create empty DataFrame
    df = pd.DataFrame()
    # add run name if given
    if run_name is not None:
        df["run"] = [run_name]

    # extract selected keys from metadata
    if pars is None:  # add all items
        for key, sub_dict in metadata_dict.items():
            for sub_key, value in sub_dict.items():
                df[f"{key}.{sub_key}"] = [value]
    else:
        for par in pars:
            key, sub_key = par.split(".")
            try:
                df[par] = [metadata_dict[key][sub_key]]
            except KeyError:
                print(f"Key {par} not found in metadata. Skipping it.")

    return df


def load_file(path: str, it: int, step: int) -> np.ndarray:
    """
    Load raw data from file and transform into data points with 3 values.

    Args:
        path: Path to run directory.
        it: Current lens iteration.
        step: Current lens step.

    Returns:
        2D list containing three int32 values per row.
    """
    filepath = f"{path}/{it}_{step}"
    raw_data = np.fromfile(filepath, dtype=np.int32)
    # reshape long array into 2D array with 3 values per entry
    return np.reshape(raw_data, (-1, 3))


def load_counts(path: str, it: int, step: int) -> int:
    """
    Count number of events in given lens iteration and step assuming int32 enconding.

    Args:
        path: Path to run directory.
        it: Current lens iteration.
        step: Current lens step.

    Returns:
        Number of events in given lens iteration and step.
    """

    filepath = f"{path}/{it}_{step}"

    # opening file to make sure it's available
    with open(filepath, "rb") as f:
        f.seek(0, os.SEEK_END)
        # get filesize in bits (1 byte = 8 bits)
        filesize = f.tell() * 8
        # divide by 32 bits (int32) and 3 values per entry
        return filesize // (32 * 3)
