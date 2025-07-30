# Copyright (2006)
# Ulf Jeppsson
# Dept. Industrial Electrical Engineering and Automation (IEA), Lund University, Sweden
# https://www.lth.se/iea/

# Copyright (2024)
# Jonas Miederer
# Chair of Energy Process Engineering (EVT), FAU Erlangen-Nuremberg, Germany
# https://www.evt.tf.fau.de/

import numpy as np
from numba import float64
from numba.experimental import jitclass

from bsm2_python.bsm2.module import Module

indices_components = np.arange(21)
SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP, SD1, SD2, SD3, XD4, XD5 = indices_components


@jitclass(spec=[('dw_par', float64[:])])
class Dewatering(Module):
    """Calculates the water and sludge stream concentrations from an 'ideal'
    dewatering unit based on a fixed percentage of solids in the dewatered sludge.

    - A defined amount of total solids are removed from the influent sludge stream
      and goes into the stream of dewatered sludge and the remaining will leave with
      the reject water phase. Soluble concentrations are not affected.

    - Temperature is also handled ideally, i.e. T(out)=T(in).

    Parameters
    ----------
    dw_par : np.ndarray(7)
        Dewatering parameters. \n
        [dewater_perc, TSS_removal_perc, X_I2TSS, X_S2TSS, X_BH2TSS, X_BA2TSS, X_P2TSS]
    """

    def __init__(self, dw_par):
        self.dw_par = dw_par

    def output(self, ydw_in):
        """Returns the sludge and reject concentrations from an 'ideal' dewatering unit.

        Parameters
        ----------
        ydw_in : np.ndarray(21)
            Dewatering influent concentrations of the 21 components
            (13 ASM1 components, TSS, Q, T and 5 dummy states). \n
            [SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP,
            SD1, SD2, SD3, XD4, XD5]

        Returns
        -------
        ydw_s : np.ndarray(21)
            Waste sludge (underflow) concentrations of the 21 components
            (13 ASM1 components, TSS, Q, T and 5 dummy states). \n
            [SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP,
            SD1, SD2, SD3, XD4, XD5]
        ydw_r : np.ndarray(21)
            Reject water (overflow) concentrations of the 21 components
            (13 ASM1 components, TSS, Q, T and 5 dummy states). \n
            [SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP,
            SD1, SD2, SD3, XD4, XD5]
        """

        # dewater_perc, TSS_removal_perc, X_I2TSS, X_S2TSS, X_BH2TSS, X_BA2TSS, X_P2TSS = dw_par
        # y = ydw_s, ydw_r
        # u = ydw_in

        ydw_s = np.zeros(21)
        ydw_r = np.zeros(21)

        tssin = (
            self.dw_par[2] * ydw_in[XI]
            + self.dw_par[3] * ydw_in[XS]
            + self.dw_par[4] * ydw_in[XBH]
            + self.dw_par[5] * ydw_in[XBA]
            + self.dw_par[6] * ydw_in[XP]
        )

        dewater_factor = self.dw_par[0] * 10000 / tssin
        qu_factor = self.dw_par[1] / (100 * dewater_factor)
        reject_factor = (1 - self.dw_par[1] / 100) / (1 - qu_factor)

        if dewater_factor > 1:
            # sludge
            ydw_s[:] = ydw_in[:]
            ydw_s[XI] = ydw_in[XI] * dewater_factor
            ydw_s[XS] = ydw_in[XS] * dewater_factor
            ydw_s[XBH] = ydw_in[XBH] * dewater_factor
            ydw_s[XBA] = ydw_in[XBA] * dewater_factor
            ydw_s[XP] = ydw_in[XP] * dewater_factor
            ydw_s[XND] = ydw_in[XND] * dewater_factor
            ydw_s[TSS] = tssin * dewater_factor
            ydw_s[Q] = ydw_in[Q] * qu_factor
            ydw_s[XD4] = ydw_in[XD4] * dewater_factor
            ydw_s[XD5] = ydw_in[XD5] * dewater_factor

            # reject
            ydw_r[:] = ydw_in[:]
            ydw_r[XI] = ydw_in[XI] * reject_factor
            ydw_r[XS] = ydw_in[XS] * reject_factor
            ydw_r[XBH] = ydw_in[XBH] * reject_factor
            ydw_r[XBA] = ydw_in[XBA] * reject_factor
            ydw_r[XP] = ydw_in[XP] * reject_factor
            ydw_r[XND] = ydw_in[XND] * reject_factor
            ydw_r[TSS] = tssin * reject_factor
            ydw_r[Q] = ydw_in[Q] * (1 - qu_factor)
            ydw_r[XD4] = ydw_in[XD4] * reject_factor
            ydw_r[XD5] = ydw_in[XD5] * reject_factor

        else:
            # the influent is too high on solids to thicken further
            # all the influent leaves with the sludge flow
            ydw_s[:] = ydw_in[:]
            ydw_s[TSS] = tssin

            # reject flow is zero
            ydw_r[:] = 0

        return ydw_s, ydw_r
