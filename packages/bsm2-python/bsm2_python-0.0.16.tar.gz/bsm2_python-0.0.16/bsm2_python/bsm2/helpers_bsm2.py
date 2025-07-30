import warnings
from typing import TypedDict

import numpy as np
from numba import int32
from numba.experimental import jitclass
from numba.typed import List

from bsm2_python.bsm2.module import Module


@jitclass
class Combiner(Module):
    """Combines multiple arrays in ASM1 format into one array in ASM1 format."""

    def __init__(self):
        pass

    @staticmethod
    def output(*args):
        """Combines multiple arrays in ASM1 format into one array in ASM1 format.

        Parameters
        ----------
        *args : np.ndarray(21)
            ASM1 arrays to be combined. \n
            [SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP,
            SD1, SD2, SD3, XD4, XD5]

        Returns
        -------
        out : np.ndarray(21)
            ASM1 array with combined values. \n
            [SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP,
            SD1, SD2, SD3, XD4, XD5]
        """

        out = np.zeros(21)
        if args[0][14] == 0:  # if no flow in first array, search for first array with flow
            start_idx = len(args)
            for idx, item in enumerate(args):
                if item[14] != 0:
                    start_idx = idx
                    break
        else:
            start_idx = 0

        for i in range(start_idx, len(args)):
            out[0:14] = (out[0:14] * out[14] + args[i][0:14] * args[i][14]) / (out[14] + args[i][14])
            out[15:21] = (out[15:21] * out[14] + args[i][15:21] * args[i][14]) / (out[14] + args[i][14])
            out[14] += args[i][14]
        return out


@jitclass(spec=(('sp_type', int32),))
class Splitter(Module):
    """Splits an array in ASM1 format into multiple arrays in ASM1 format.

    Parameters
    ----------
    sp_type : int
        Type of splitter (1 or 2) \n
        - 1: Split ratio is specified in splitratio parameter (default).
        - 2: Split ratio is not specified, but a threshold value is specified in qthreshold parameter
                everything above qthreshold is split into the second flow.
    """

    def __init__(self, sp_type=1):
        self.sp_type = sp_type

    def output(self, in1: np.ndarray, splitratio: tuple = (0.0, 0.0), qthreshold: float = 0):
        """Splits an array in ASM1 format into multiple arrays in ASM1 format.

        Parameters
        ----------
        in1 : np.ndarray(21)
            ASM1 array to be split. \n
            [SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP,
            SD1, SD2, SD3, XD4, XD5]
        splitratio : tuple(float) (optional)
            Split ratio for each component. <br>
            Ideally sums up to 1 (except if sp_type=2, then no split ratio is
            needed and flow is split into two flows).
        qthreshold : float
            Threshold value for type 2 splitter.

        Returns
        -------
        outs : list(np.ndarray(21), np.ndarray(21),...)
            ASM1 arrays with split volume flows. list of length of splitratio. \n
            (asm1_flow1, asm1_flow2,...)
        """
        # sanity checks for input
        for ratio in splitratio:
            if ratio < 0.0:
                err = 'Split ratio must be non-negative.'
                raise ValueError(err)
        outs = List()
        if in1[14] == 0:  # if no flow, all split flows are 0
            for _ in range(len(splitratio)):
                out = np.zeros(21)
                out[:] = in1[:]
                out[14] = 0
                outs.append(out)
        else:  # if flow, split flow ratios are calculated
            # if type 2, everything above qthreshold is split in the second flow. splitratios are overwritten!
            threshold_split_mode = 2
            if self.sp_type == threshold_split_mode:
                needed_len = 2
                if len(splitratio) != needed_len:
                    err = 'Split ratio must be of length 2 for type 2 splitter'
                    raise ValueError(err)
                if splitratio[0] != 0 or splitratio[1] != 0:
                    err = 'splitratio[0] and splitratio[1] must be 0 for type 2 splitter'
                    raise ValueError(err)
                splitratio = (qthreshold, in1[14] - qthreshold) if in1[14] >= qthreshold else (in1[14], 0)
            for i, _ in enumerate(splitratio):
                actual_splitratio = splitratio[i] / sum(splitratio)
                out = np.zeros(21)
                out[14] = in1[14] * actual_splitratio
                if out[14] >= 0:  # if there is a physical flow, out is calculated. Otherwise, throw an error
                    out[:14] = in1[:14]
                    out[15:21] = in1[15:21]
                    outs.append(out)
                else:
                    err = f'Negative flow in splitter output {i + 1} with split ratio {actual_splitratio}.'
                    raise ValueError(err)
        return outs


def reduce_asm1(asm1_arr, reduce_to=('SI', 'SS', 'XI', 'XS', 'XBH', 'SNH', 'SND', 'XND', 'TSS', 'Q', 'TEMP')):
    """Reduces ASM1 array to selected components.

    Parameters
    ----------
    asm1_arr : np.ndarray(21)
        ASM1 array to be reduced. Needs to contain all ASM1 components: \n
        [SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND,
        XND, SALK, TSS, Q, TEMP, SD1, SD2, SD3, XD4, XD5]
    reduce_to : tuple(str)
        Components to be included in the reduced array. Defaults to all changing components in BSM2 influent file.

    Returns
    -------
    out : np.ndarray
        Reduced ASM1 array.
    """

    asm1_components = (
        'SI',
        'SS',
        'XI',
        'XS',
        'XBH',
        'XBA',
        'XP',
        'SO',
        'SNO',
        'SNH',
        'SND',
        'XND',
        'SALK',
        'TSS',
        'Q',
        'TEMP',
        'SD1',
        'SD2',
        'SD3',
        'XD4',
        'XD5',
    )
    # raise error if asm1_arr is not of shape (:,21)
    if len(asm1_arr.shape) == 1:
        is_1d = True
        asm1_arr = np.expand_dims(asm1_arr, axis=0)
    num_cols = 21
    if asm1_arr.shape[1] != num_cols:
        err = 'ASM1 array must have 21 columns'
        raise ValueError(err)

    out = np.zeros((len(asm1_arr[:, 0]), len(reduce_to)))
    for idx, component in enumerate(reduce_to):
        out[:, idx] = asm1_arr[:, asm1_components.index(component)]

    if is_1d:
        out = out[0]
    return out


def expand_asm1(
    red_arr,
    red_components=('SI', 'SS', 'XI', 'XS', 'XBH', 'SNH', 'SND', 'XND', 'TSS', 'Q', 'TEMP'),
    expand_by=None,
):
    """Expands reduced ASM1 array to full ASM1 array.

    Parameters
    ----------
    red_arr : np.ndarray
        Reduced ASM1 array to be expanded.
    red_components : tuple(str)
        Components in the reduced array. Defaults to all changing components in BSM2 influent file: \n
        [SI, SS, XI, XS, XBH, SNH, SND, XND, TSS, Q, TEMP]
    expand_by : dict(str:int)
        Components to be added to the reduced array. <br>
        Defaults to all non-changing components in BSM2 influent file and their default values: \n
        {"XBA": 0, "XP": 0, "SO": 0, "SNO": 0, "SALK": 7, "SD1": 0, "SD2": 0, "SD3": 0, "XD4": 0, "XD5": 0}

    Returns
    -------
    out : np.ndarray[21]
        Expanded ASM1 array.
    """

    if expand_by is None:
        expand_by = {'XBA': 0, 'XP': 0, 'SO': 0, 'SNO': 0, 'SALK': 7, 'SD1': 0, 'SD2': 0, 'SD3': 0, 'XD4': 0, 'XD5': 0}

    asm1_components = (
        'SI',
        'SS',
        'XI',
        'XS',
        'XBH',
        'XBA',
        'XP',
        'SO',
        'SNO',
        'SNH',
        'SND',
        'XND',
        'SALK',
        'TSS',
        'Q',
        'TEMP',
        'SD1',
        'SD2',
        'SD3',
        'XD4',
        'XD5',
    )
    # raise error if red_arr is not of shape (:,len(red_components))
    if len(red_arr.shape) == 1:
        is_1d = True
        red_arr = np.expand_dims(red_arr, axis=0)

    if red_arr.shape[1] != len(red_components):
        err = 'Reduced ASM1 array must have the same number of columns as red_components'
        raise ValueError(err)

    out = np.zeros((len(red_arr[:, 0]), len(asm1_components)))
    for idx, component in enumerate(asm1_components):
        if component in red_components:
            out[:, idx] = red_arr[:, red_components.index(component)]
        elif component in expand_by:
            out[:, idx] = expand_by[component]
        else:
            warnings.warn(
                f'Component {component} is not in red_components or expand_by. \
                    Component {component} is set to 0',
                stacklevel=1,
            )
            out[:, idx] = 0

    if is_1d:
        out = out[0]
    return out


class PIDParams(TypedDict):
    k: float
    t_i: float
    t_d: float
    t_t: float
    offset: float
    min_value: float
    max_value: float
    setpoint: float
    aw_init: float
    use_antiwindup: bool
