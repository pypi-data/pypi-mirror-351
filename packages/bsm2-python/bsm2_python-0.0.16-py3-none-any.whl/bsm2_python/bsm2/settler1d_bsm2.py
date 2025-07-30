# Copyright (2006)
# Ulf Jeppsson
# Dept. Industrial Electrical Engineering and Automation (IEA), Lund University, Sweden
# https://www.lth.se/iea/

# Copyright (2024)
# Jonas Miederer
# Chair of Energy Process Engineering (EVT), FAU Erlangen-Nuremberg, Germany
# https://www.evt.tf.fau.de/

import numpy as np
from numba import jit
from scipy.integrate import odeint

from bsm2_python.bsm2.module import Module

indices_components = np.arange(21)
SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP, SD1, SD2, SD3, XD4, XD5 = indices_components


@jit(nopython=True, cache=True)
def settlerequations(t, ys, ys_in, sedpar, dim, layer, q_r, q_w, tempmodel, modeltype):
    """Returns an array containing the differential equations of a non-reactive sedimentation tank
    with variable number of layers (default model is 10 layers), which is compatible with ASM1 model.

    Parameters
    ----------
    t : np.ndarray(2)
        Time interval for integration, needed for the solver [d]. \n
        [step, step + timestep]
    ys : np.ndarray(12 * nooflayers)
        Solution of the differential equations, needed for the solver.
        Values for the 12 components for each layer, sorted by components. \n
        Components: [S_I, S_S, S_O, S_NO, S_NH, S_ND, S_ALK, X_TSS, TEMP, S_D1, S_D2, S_D3] \n
        [SI_LAY1, SI_LAY2, SI_LAY3,..., SI_NOOFLAY, SS_LAY1, SS_LAY2, SS_LAY3,... SS_NOOFLAY, SO_LAY1,...]
    ys_in : np.ndarray(21)
        Settler inlet concentrations of the 21 components
        (13 ASM1 components, TSS, Q, T and 5 dummy states). \n
        [SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, T_WW,
        SD1, SD2, SD3, XD4, XD5]
    sedpar : np.ndarray(7)
        Settler parameters. \n
        [v0_max, v0, r_h, r_p, f_ns, X_t, sb_limit]
    dim : np.ndarray(2)
        Dimensions of the settler, area and height. \n
        [area, height]
    layer : np.ndarray(2)
        Feedlayer and number of layers in the settler. \n
        [feedlayer, nooflayers]
    q_r : float
        Return sludge flow rate [m³ ⋅ d⁻¹].
    q_w : float
        Flow rate of waste sludge [m³ ⋅ d⁻¹].
    tempmodel : bool
        If true, differential equation for the wastewater temperature is used,
        otherwise influent wastewater temperature is just passed through the settler.
    modeltype : int
        - 0: Model with nooflayers for solubles (IWA/COST Benchmark).
        - 1: Model with 1 layer for solubles (GSP-X implementation) (not implemented yet).
        - 2: Model with 0 layers for solubles (old WEST implementation) (not implemented yet).

    Returns
    -------
    dys : np.ndarray(12 * nooflayers)
        Array containing the differential values of `ys_in` only for soluble components,
        total suspended solids (TSS) and temperature the settling model with certain number of layers. \n
        Components: [S_I, S_S, S_O, S_NO, S_NH, S_ND, S_ALK, X_TSS, TEMP, S_D1, S_D2, S_D3] \n
        [SI_LAY1, SI_LAY2, SI_LAY3,..., SI_NOOFLAY, SS_LAY1, SS_LAY2, SS_LAY3,... SS_NOOFLAY, SO_LAY1,...]
    """

    if modeltype != 0:
        # TODO: implement modeltype 1 and 2
        err = 'Modeltypes 1 and 2 not implemented yet'
        raise NotImplementedError(err)

    area = dim[0]
    feedlayer = layer[0]
    nooflayers = layer[1]
    h = dim[1] / nooflayers
    # volume = area * dim[1]

    vs = np.zeros(nooflayers)
    js = np.zeros(nooflayers + 1)
    js_temp = np.zeros(nooflayers)

    dys = np.zeros(12 * nooflayers)  # differential equations only for soluble components, TSS and Temperature

    eps = 0.01
    v_in = ys_in[Q] / area
    # Q_f = ys_in[Q]
    q_u = q_r + q_w
    q_e = ys_in[Q] - q_u
    v_up = q_e / area
    v_dn = q_u / area

    ystemp = ys
    ystemp[ystemp < 0.0] = 0.00001
    ys[ys < 0.0] = 0.00001

    # sedimentation velocity for each of the layers:
    for i in range(nooflayers):
        vs[i] = sedpar[1] * (
            np.exp(-sedpar[2] * (ystemp[i + 7 * nooflayers] - sedpar[4] * ys_in[TSS]))
            - np.exp(-sedpar[3] * (ystemp[i + 7 * nooflayers] - sedpar[4] * ys_in[TSS]))
        )  # ystemp[i+7*nooflayers] is TSS
        vs[vs > sedpar[0]] = sedpar[0]
        vs[vs < 0.0] = 0.0

    # sludge flux due to sedimentation for each layer (not taking into account X limit)
    for i in range(nooflayers):
        js_temp[i] = vs[i] * ystemp[i + 7 * nooflayers]

    # sludge flux due to sedimentation of each layer:
    for i in range(nooflayers - 1):
        if i < (feedlayer - 1 - eps) and ystemp[i + 1 + 7 * nooflayers] <= sedpar[5]:
            js[i + 1] = js_temp[i]
        elif js_temp[i] < js_temp[i + 1]:
            js[i + 1] = js_temp[i]
        else:
            js[i + 1] = js_temp[i + 1]

    # differential equations:
    # soluble component s_i:
    for i in range(feedlayer - 1):
        dys[i] = (-v_up * ystemp[i] + v_up * ystemp[i + 1]) / h
    dys[feedlayer - 1] = (v_in * ys_in[SI] - v_up * ystemp[feedlayer - 1] - v_dn * ystemp[feedlayer - 1]) / h
    for i in range(feedlayer, nooflayers):
        dys[i] = (v_dn * ystemp[i - 1] - v_dn * ystemp[i]) / h

    # soluble component s_s:
    for i in range(feedlayer - 1):
        dys[i + nooflayers] = (-v_up * ystemp[i + nooflayers] + v_up * ystemp[i + 1 + nooflayers]) / h
    dys[feedlayer - 1 + nooflayers] = (
        v_in * ys_in[SS] - v_up * ystemp[feedlayer - 1 + nooflayers] - v_dn * ystemp[feedlayer - 1 + nooflayers]
    ) / h
    for i in range(feedlayer, nooflayers):
        dys[i + nooflayers] = (v_dn * ystemp[i - 1 + nooflayers] - v_dn * ystemp[i + nooflayers]) / h

    # soluble component s_o:
    for i in range(feedlayer - 1):
        dys[i + 2 * nooflayers] = (-v_up * ystemp[i + 2 * nooflayers] + v_up * ystemp[i + 1 + 2 * nooflayers]) / h
    dys[feedlayer - 1 + 2 * nooflayers] = (
        v_in * ys_in[SO] - v_up * ystemp[feedlayer - 1 + 2 * nooflayers] - v_dn * ystemp[feedlayer - 1 + 2 * nooflayers]
    ) / h
    for i in range(feedlayer, nooflayers):
        dys[i + 2 * nooflayers] = (v_dn * ystemp[i - 1 + 2 * nooflayers] - v_dn * ystemp[i + 2 * nooflayers]) / h

    # soluble component s_no:
    for i in range(feedlayer - 1):
        dys[i + 3 * nooflayers] = (-v_up * ystemp[i + 3 * nooflayers] + v_up * ystemp[i + 1 + 3 * nooflayers]) / h
    dys[feedlayer - 1 + 3 * nooflayers] = (
        v_in * ys_in[SNO]
        - v_up * ystemp[feedlayer - 1 + 3 * nooflayers]
        - v_dn * ystemp[feedlayer - 1 + 3 * nooflayers]
    ) / h
    for i in range(feedlayer, nooflayers):
        dys[i + 3 * nooflayers] = (v_dn * ystemp[i - 1 + 3 * nooflayers] - v_dn * ystemp[i + 3 * nooflayers]) / h

    # soluble component s_nh:
    for i in range(feedlayer - 1):
        dys[i + 4 * nooflayers] = (-v_up * ystemp[i + 4 * nooflayers] + v_up * ystemp[i + 1 + 4 * nooflayers]) / h
    dys[feedlayer - 1 + 4 * nooflayers] = (
        v_in * ys_in[SNH]
        - v_up * ystemp[feedlayer - 1 + 4 * nooflayers]
        - v_dn * ystemp[feedlayer - 1 + 4 * nooflayers]
    ) / h
    for i in range(feedlayer, nooflayers):
        dys[i + 4 * nooflayers] = (v_dn * ystemp[i - 1 + 4 * nooflayers] - v_dn * ystemp[i + 4 * nooflayers]) / h

    # soluble component s_nd:
    for i in range(feedlayer - 1):
        dys[i + 5 * nooflayers] = (-v_up * ystemp[i + 5 * nooflayers] + v_up * ystemp[i + 1 + 5 * nooflayers]) / h
    dys[feedlayer - 1 + 5 * nooflayers] = (
        v_in * ys_in[SND]
        - v_up * ystemp[feedlayer - 1 + 5 * nooflayers]
        - v_dn * ystemp[feedlayer - 1 + 5 * nooflayers]
    ) / h
    for i in range(feedlayer, nooflayers):
        dys[i + 5 * nooflayers] = (v_dn * ystemp[i - 1 + 5 * nooflayers] - v_dn * ystemp[i + 5 * nooflayers]) / h

    # soluble component s_alk:
    for i in range(feedlayer - 1):
        dys[i + 6 * nooflayers] = (-v_up * ystemp[i + 6 * nooflayers] + v_up * ystemp[i + 1 + 6 * nooflayers]) / h
    dys[feedlayer - 1 + 6 * nooflayers] = (
        v_in * ys_in[SALK]
        - v_up * ystemp[feedlayer - 1 + 6 * nooflayers]
        - v_dn * ystemp[feedlayer - 1 + 6 * nooflayers]
    ) / h
    for i in range(feedlayer, nooflayers):
        dys[i + 6 * nooflayers] = (v_dn * ystemp[i - 1 + 6 * nooflayers] - v_dn * ystemp[i + 6 * nooflayers]) / h

    # particulate component x_tss:
    for i in range(feedlayer - 1):
        dys[i + 7 * nooflayers] = (
            (-v_up * ystemp[i + 7 * nooflayers] + v_up * ystemp[i + 1 + 7 * nooflayers] - js[i + 1]) + js[i]
        ) / h
    dys[feedlayer - 1 + 7 * nooflayers] = (
        v_in * ys_in[TSS]
        - v_up * ystemp[feedlayer - 1 + 7 * nooflayers]
        - v_dn * ystemp[feedlayer - 1 + 7 * nooflayers]
        - js[feedlayer - 1 + 1]
        + js[feedlayer - 1]
    ) / h
    for i in range(feedlayer, nooflayers):
        dys[i + 7 * nooflayers] = (
            v_dn * ystemp[i - 1 + 7 * nooflayers] - v_dn * ystemp[i + 7 * nooflayers] - js[i + 1] + js[i]
        ) / h

    # Temperature:
    if tempmodel:
        for i in range(feedlayer - 1):
            dys[i + 8 * nooflayers] = (-v_up * ystemp[i + 8 * nooflayers] + v_up * ystemp[i + 1 + 8 * nooflayers]) / h
        dys[feedlayer - 1 + 8 * nooflayers] = (
            v_in * ys_in[TEMP]
            - v_up * ystemp[feedlayer - 1 + 8 * nooflayers]
            - v_dn * ystemp[feedlayer - 1 + 8 * nooflayers]
        ) / h
        for i in range(feedlayer, nooflayers):
            dys[i + 8 * nooflayers] = (v_dn * ystemp[i - 1 + 8 * nooflayers] - v_dn * ystemp[i + 8 * nooflayers]) / h

    # soluble component s_d1:
    for i in range(feedlayer - 1):
        dys[i + 9 * nooflayers] = (-v_up * ystemp[i + 9 * nooflayers] + v_up * ystemp[i + 1 + 9 * nooflayers]) / h
    dys[feedlayer - 1 + 9 * nooflayers] = (
        v_in * ys_in[SD1]
        - v_up * ystemp[feedlayer - 1 + 9 * nooflayers]
        - v_dn * ystemp[feedlayer - 1 + 9 * nooflayers]
    ) / h
    for i in range(feedlayer, nooflayers):
        dys[i + 9 * nooflayers] = (v_dn * ystemp[i - 1 + 9 * nooflayers] - v_dn * ystemp[i + 9 * nooflayers]) / h

    # soluble component s_d2:
    for i in range(feedlayer - 1):
        dys[i + 10 * nooflayers] = (-v_up * ystemp[i + 10 * nooflayers] + v_up * ystemp[i + 1 + 10 * nooflayers]) / h
    dys[feedlayer - 1 + 10 * nooflayers] = (
        v_in * ys_in[SD2]
        - v_up * ystemp[feedlayer - 1 + 10 * nooflayers]
        - v_dn * ystemp[feedlayer - 1 + 10 * nooflayers]
    ) / h
    for i in range(feedlayer, nooflayers):
        dys[i + 10 * nooflayers] = (v_dn * ystemp[i - 1 + 10 * nooflayers] - v_dn * ystemp[i + 10 * nooflayers]) / h

    # soluble component s_d3:
    for i in range(feedlayer - 1):
        dys[i + 11 * nooflayers] = (-v_up * ystemp[i + 11 * nooflayers] + v_up * ystemp[i + 1 + 11 * nooflayers]) / h
    dys[feedlayer - 1 + 11 * nooflayers] = (
        v_in * ys_in[SD3]
        - v_up * ystemp[feedlayer - 1 + 11 * nooflayers]
        - v_dn * ystemp[feedlayer - 1 + 11 * nooflayers]
    ) / h
    for i in range(feedlayer, nooflayers):
        dys[i + 11 * nooflayers] = (v_dn * ystemp[i - 1 + 11 * nooflayers] - v_dn * ystemp[i + 11 * nooflayers]) / h

    return dys


@jit(nopython=True, cache=True)
def get_output(ys_int, ys_in, nooflayers, tempmodel, q_r, q_w, dim, asm1par, sedpar):
    """Returns the return, waste and effluent concentrations of the settler model.

    Parameters
    ----------
    ys_int : np.ndarray(12 * nooflayers)
        Solution of the differential equations, needed for the solver.
        Values for the 12 components for each layer, sorted by components. \n
        Components: [S_I, S_S, S_O, S_NO, S_NH, S_ND, S_ALK, X_TSS, TEMP, S_D1, S_D2, S_D3] \n
        [SI_LAY1, SI_LAY2, SI_LAY3,..., SI_NOOFLAY, SS_LAY1, SS_LAY2, SS_LAY3,... SS_NOOFLAY, SO_LAY1,...]
    ys_in : np.ndarray(21)
        Settler inlet concentrations of the 21 components
        (13 ASM1 components, TSS, Q, T and 5 dummy states). \n
        [SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, T_WW,
        SD1, SD2, SD3, XD4, XD5]
    nooflayers : int
        Number of layers in the settler [-].
    tempmodel : bool
        If true, differential equation for the wastewater temperature is used,
        otherwise influent wastewater temperature is just passed through the settler.
    q_r : float
        Return sludge flow rate [m³ ⋅ d⁻¹].
    q_w : float
        Flow rate of waste sludge [m³ ⋅ d⁻¹].
    dim : np.ndarray(2)
        Dimensions of the settler, area and height. \n
        [area, height]
    asm1par : np.ndarray(24)
        ASM1 parameters. \n
        [MU_H, K_S, K_OH, K_NO, B_H, MU_A, K_NH, K_OA, B_A, NY_G, K_A, K_H, K_X, NY_H,
        Y_H, Y_A, F_P, I_XB, I_XP, X_I2TSS, X_S2TSS, X_BH2TSS, X_BA2TSS, X_P2TSS]
    sedpar : np.ndarray(7)
        Settler parameters. \n
        [v0_max, v0, r_h, r_p, f_ns, X_t, sb_limit]

    Returns
    -------
    ys_ret : np.ndarray(21)
        Array containing the values of the 21 components
        (13 ASM1 components, TSS, Q, T and 5 dummy states)
        in the underflow (bottom layer of settler) at the current time step
        after the integration - **return sludge**. \n
        [SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, T_WW,
        SD1, SD2, SD3, XD4, XD5]
    ys_was : np.ndarray(21)
        Array containing the values of the 21 components
        (13 ASM1 components, TSS, Q, T and 5 dummy states)
        in the underflow (bottom layer of settler) at the current time step
        after the integration - **waste sludge**. \n
        [SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, T_WW,
        SD1, SD2, SD3, XD4, XD5]
    ys_eff : np.ndarray(21)
        Array containing the values of the 21 components
        (13 ASM1 components, TSS, Q, T and 5 dummy states)
        in the effluent (top layer of settler) and at the current time step
        after the integration - **effluent**. \n
        [SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, T_WW,
        SD1, SD2, SD3, XD4, XD5]
    sludge_height : float
        Float containing the continuous signal of sludge blanket level [m].
    ys_tss_internal : np.ndarray(nooflayers)
        Array containing the internal TSS states of the settler. \n
        [TSS_LAY1, TSS_LAY2, TSS_LAY3,..., TSS_NOOFLAYER]
    """

    ys_ret = np.zeros(21)
    ys_was = np.zeros(21)
    ys_eff = np.zeros(21)

    h = dim[1] / nooflayers

    # 0  1  2  3  4   5   6  7  8   9   10  11  12   13  14 15  16  17  18  19  20
    # SI SS XI XS XBH XBA XP SO SNO SNH SND XND SALK TSS Q TEMP SD1 SD2 SD3 XD4 XD5
    # underflow
    ys_ret[SI] = ys_int[nooflayers - 1]
    ys_ret[SS] = ys_int[2 * nooflayers - 1]
    ys_ret[SO] = ys_int[3 * nooflayers - 1]
    ys_ret[SNO] = ys_int[4 * nooflayers - 1]
    ys_ret[SNH] = ys_int[5 * nooflayers - 1]
    ys_ret[SND] = ys_int[6 * nooflayers - 1]
    ys_ret[SALK] = ys_int[7 * nooflayers - 1]
    ys_ret[TSS] = ys_int[8 * nooflayers - 1]
    if tempmodel:
        ys_ret[TEMP] = ys_int[9 * nooflayers - 1]
    else:
        ys_ret[TEMP] = ys_in[TEMP]
    ys_ret[SD1] = ys_int[10 * nooflayers - 1]
    ys_ret[SD2] = ys_int[11 * nooflayers - 1]
    ys_ret[SD3] = ys_int[12 * nooflayers - 1]

    if ys_in[TSS] != 0:  # this condition should also consider XI, XS, XBH, XBA, XP, XND, XD4, XD5
        ys_ret[XI] = ys_ret[TSS] / ys_in[TSS] * ys_in[XI]
        ys_ret[XS] = ys_ret[TSS] / ys_in[TSS] * ys_in[XS]
        ys_ret[XBH] = ys_ret[TSS] / ys_in[TSS] * ys_in[XBH]
        ys_ret[XBA] = ys_ret[TSS] / ys_in[TSS] * ys_in[XBA]
        ys_ret[XP] = ys_ret[TSS] / ys_in[TSS] * ys_in[XP]
        ys_ret[XND] = ys_ret[TSS] / ys_in[TSS] * ys_in[XND]
        ys_ret[XD4] = ys_ret[TSS] / ys_in[TSS] * ys_in[XD4]
        ys_ret[XD5] = ys_ret[TSS] / ys_in[TSS] * ys_in[XD5]
    else:
        ys_ret[XI : XD5 + 1] = 0.0

    ys_ret[Q] = q_r

    ys_was[:] = ys_ret[:]
    ys_was[Q] = q_w

    # effluent
    ys_eff[SI] = ys_int[0]
    ys_eff[SS] = ys_int[nooflayers]
    ys_eff[SO] = ys_int[2 * nooflayers]
    ys_eff[SNO] = ys_int[3 * nooflayers]
    ys_eff[SNH] = ys_int[4 * nooflayers]
    ys_eff[SND] = ys_int[5 * nooflayers]
    ys_eff[SALK] = ys_int[6 * nooflayers]
    ys_eff[TSS] = ys_int[7 * nooflayers]
    if tempmodel:
        ys_eff[TEMP] = ys_int[8 * nooflayers]
    else:
        ys_eff[TEMP] = ys_in[TEMP]
    ys_eff[SD1] = ys_int[9 * nooflayers]
    ys_eff[SD2] = ys_int[10 * nooflayers]
    ys_eff[SD3] = ys_int[11 * nooflayers]

    if ys_in[TSS] != 0:  # this condition should also consider XI, XS, XBH, XBA, XP, XND, XD4, XD5
        ys_eff[XI] = ys_eff[TSS] / ys_in[TSS] * ys_in[XI]
        ys_eff[XS] = ys_eff[TSS] / ys_in[TSS] * ys_in[XS]
        ys_eff[XBH] = ys_eff[TSS] / ys_in[TSS] * ys_in[XBH]
        ys_eff[XBA] = ys_eff[TSS] / ys_in[TSS] * ys_in[XBA]
        ys_eff[XP] = ys_eff[TSS] / ys_in[TSS] * ys_in[XP]
        ys_eff[XND] = ys_eff[TSS] / ys_in[TSS] * ys_in[XND]
        ys_eff[XD4] = ys_eff[TSS] / ys_in[TSS] * ys_in[XD4]
        ys_eff[XD5] = ys_eff[TSS] / ys_in[TSS] * ys_in[XD5]
    else:
        ys_eff[XI : XD5 + 1] = 0.0

    ys_eff[Q] = ys_in[Q] - q_w - q_r

    # internal TSS states, for plant performance only
    ys_tss_internal = np.zeros(nooflayers)
    for i in range(nooflayers):
        ys_tss_internal[i] = ys_int[7 * nooflayers + i]

    # continuous signal of sludge blanket level
    no_sludge_layer = np.where(ys_int[7 * nooflayers : 8 * nooflayers] < sedpar[6])[0]
    # if all layers surpass threshold, sludge level is full.
    sludge_level = nooflayers - 1 - max(no_sludge_layer) if len(no_sludge_layer) > 0 else nooflayers

    if sludge_level == nooflayers:
        sludge_height = h * nooflayers
    elif sludge_level == nooflayers - 1:
        sludge_height = sludge_level * h + h * (ys_int[0] / ys_int[1])
    elif sludge_level == 0:
        sludge_height = (
            h * (ys_int[8 * nooflayers - 1] + ys_int[8 * nooflayers - 2]) / (sedpar[6] - ys_int[8 * nooflayers - 2])
        )
    else:
        sludge_height = sludge_level * h + h * (
            ys_int[8 * nooflayers - 1 - sludge_level] + ys_int[8 * nooflayers - 2 - sludge_level]
        ) / (ys_int[8 * nooflayers - sludge_level] - ys_int[8 * nooflayers - 2 - sludge_level])

    return ys_ret, ys_was, ys_eff, sludge_height, ys_tss_internal


class Settler(Module):
    """This is a implementation defining a n-layer settler model.

    - Can simulate n, 1 or 0 layers for the solubles by using `modeltype` = 0, 1 or 2 (currently only 0 implemented).
      Darko Vrecko, March 2005

    - Correction to the functionality of `tempmodel`.
      Krist V. Gernaey, 02 May 2005

    - Activation of dummy states via parameter `activate` = 1 (otherwise 0).

    - Sludge blanket level output added august 2011.

    Parameters
    ----------
    dim : np.ndarray(2)
        Dimensions of the settler, area and height. \n
        [area, height]
    layer : np.ndarray
        Feedlayer and number of layers in the settler. \n
        [feedlayer, nooflayers]
    q_r : float
        Flow rate of sludge return [m³ ⋅ d⁻¹].
    q_w : float
        Flow rate of waste sludge [m³ ⋅ d⁻¹].
    ys0 : np.ndarray(12 ⋅ nooflayers)
        Initial values for the 12 components for each layer, sorted by components. \n
        Components: [S_I, S_S, S_O, S_NO, S_NH, S_ND, S_ALK, X_TSS, TEMP, S_D1, S_D2, S_D3] <br>
        [SI_LAY1, SI_LAY2, SI_LAY3,..., SI_NOOFLAY, SS_LAY1, SS_LAY2, SS_LAY3,... SS_NOOFLAY, SO_LAY1,...]
    sedpar : np.ndarray(7)
        Settler parameters. \n
        [v0_max, v0, r_h, r_p, f_ns, X_t, sb_limit]
    asm1par : np.ndarray(24)
        ASM1 parameters. \n
        [MU_H, K_S, K_OH, K_NO, B_H, MU_A, K_NH, K_OA, B_A, NY_G, K_A, K_H, K_X, NY_H,
        Y_H, Y_A, F_P, I_XB, I_XP, X_I2TSS, X_S2TSS, X_BH2TSS, X_BA2TSS, X_P2TSS]
    tempmodel : bool
        If true, differential equation for the wastewater temperature is used,
        otherwise influent wastewater temperature is just passed through the settler.
    modeltype : int
        - 0: Model with nooflayers for solubles (IWA/COST Benchmark).
        - 1: Model with 1 layer for solubles (GSP-X implementation) (not implemented yet).
        - 2: Model with 0 layers for solubles (old WEST implementation) (not implemented yet).
    """

    def __init__(self, dim, layer, q_r, q_w, ys0, sedpar, asm1par, tempmodel, modeltype):
        self.dim = dim
        self.layer = layer
        self.q_r = q_r
        self.q_w = q_w
        self.ys0 = ys0
        self.sedpar = sedpar
        self.asm1par = asm1par
        self.tempmodel = tempmodel
        self.modeltype = modeltype

        if self.modeltype != 0:
            err = 'Model type not implemented yet. Choose modeltype = 0'
            raise NotImplementedError(err)

    def output(self, timestep, step, ys_in):
        """Returns the solved differential equations of settling model.

        Parameters
        ----------
        timestep : float
            Size of integration interval [d].
        step : float
            Upper boundary for integration interval [d].
        ys_in : np.ndarray(21)
            Settler inlet concentrations of the 21 components
            (13 ASM1 components, TSS, Q, T and 5 dummy states). \n
            [SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, T_WW,
            SD1, SD2, SD3, XD4, XD5]

        Returns
        -------
        ys_ret : np.ndarray(21)
            Array containing the values of the 21 components
            (13 ASM1 components, TSS, Q, T and 5 dummy states)
            in the underflow (bottom layer of settler) at the current time step
            after the integration - **return sludge**. \n
            [SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, T_WW,
            SD1, SD2, SD3, XD4, XD5]
        ys_was : np.ndarray(21)
            Array containing the values of the 21 components
            (13 ASM1 components, TSS, Q, T and 5 dummy states)
            in the underflow (bottom layer of settler) at the current time step
            after the integration - **waste sludge**. \n
            [SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, T_WW,
            SD1, SD2, SD3, XD4, XD5]
        ys_eff : np.ndarray(21)
            Array containing the values of the 21 components
            (13 ASM1 components, TSS, Q, T and 5 dummy states)
            in the effluent (top layer of settler) and at the current time step
            after the integration - **effluent**. \n
            [SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, T_WW,
            SD1, SD2, SD3, XD4, XD5]
        sludge_height : float
            Float containing the continuous signal of sludge blanket level [m].
        ys_tss_internal : np.ndarray(nooflayers)
            Array containing the internal TSS states of the settler. \n
            [TSS_LAY1, TSS_LAY2, TSS_LAY3,..., TSS_NOOFLAYER]
        """
        # check if too much sludge is returned
        if ys_in[Q] < 0:
            raise ValueError('The influent flow rate (Q) must be greater than 0.')
        q_r = min(self.q_r, ys_in[Q])
        q_w = min(self.q_w, ys_in[Q] - q_r)

        nooflayers = self.layer[1]
        # ys_TSS = np.zeros(nooflayers)
        t_eval = np.array([step, step + timestep])

        odes = odeint(
            settlerequations,
            self.ys0,
            t_eval,
            tfirst=True,
            args=(ys_in, self.sedpar, self.dim, self.layer, q_r, q_w, self.tempmodel, self.modeltype),
        )
        ys_int = odes[1]
        self.ys0 = ys_int

        ys_ret, ys_was, ys_eff, sludge_height, ys_tss_internal = get_output(
            ys_int, ys_in, nooflayers, self.tempmodel, self.q_r, self.q_w, self.dim, self.asm1par, self.sedpar
        )

        return ys_ret, ys_was, ys_eff, sludge_height, ys_tss_internal
